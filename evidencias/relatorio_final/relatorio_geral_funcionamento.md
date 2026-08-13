# Relatório Geral de Funcionamento — Correções de Auditoria, Massa de Dados e Automação

| Campo | Valor |
| --- | --- |
| Data/hora de execução | 2026-08-13, ~19:57–20:12 UTC (deploys/testes) e 20:30 UTC (fechamento deste relatório) |
| Org | `hackaton2` (`hackaton2@ddgroup.com.br`, Org Id `00DgL00000XJGhBUAX`) |
| Executado via | Claude Code + Salesforce CLI (`sf`) + Anonymous Apex, sessão única |
| Escopo | Correções da auditoria (FLS de `Amostra__c` + automação de aprovação de desconto), massa de dados de teste encadeada, retrieve de metadata |

---

## 1. Correções da auditoria

### 1.1 FLS de `Amostra__c` restaurada

**Achado da auditoria:** os Permission Sets `Administrador_Comercial`, `Laboratorio` e `Vendedor` haviam perdido as `fieldPermissions` dos 6 campos customizados de `Amostra__c` na org (regressão já sinalizada, mas não corrigida, em `evidencias/demandas/demanda-13.md`, seção 6 — provável efeito de um redeploy parcial concorrente de outra sessão, mesmo padrão da [ADR 0005](../../decisions/0005-owd-revertido-para-private-fora-do-fluxo.md)).

**Confirmação do achado antes da correção** (SOQL em `FieldPermissions`, `SobjectType='Amostra__c'`, os 3 Permission Sets): **0 registros** — confirmado que a FLS estava de fato ausente na org, não só uma suspeita.

**Correção:** redeploy dos Permission Sets locais (já commitados corretamente no repositório) para a org:
```
sf project deploy start --metadata PermissionSet --target-org hackaton2
```
Resultado: `Succeeded`, 3 componentes deployados (`Administrador_Comercial`, `Laboratorio`, `Vendedor`).

**Confirmação pós-correção** (mesma query SOQL): **18 registros** (3 Permission Sets × 6 campos: `CustoEstimado__c`, `DataEnvio__c`, `NumeroTentativa__c`, `PesoVolumeEnviado__c`, `ProdutoAmostrado__c`, `Resultado__c`).

| Permission Set | Read | Edit (típico) |
| --- | --- | --- |
| Administrador_Comercial | ✅ todos os 6 campos | ✅ todos os 6 campos |
| Vendedor | ✅ todos os 6 campos | ✅ todos os 6 campos |
| Laboratorio | ✅ todos os 6 campos | ✅ `Resultado__c` (edita o resultado do teste); demais somente leitura |

**Status: corrigido e confirmado via SOQL.**

### 1.2 Automação de submissão para aprovação no estágio "Apresentação de Custo"

**Achado da auditoria:** o Approval Process `Opportunity.Aprovacao_Desconto_Oportunidade` (já existente desde a demanda-11, critério `PrecoFinal__c < Amount`) só era submetido manualmente ou via Apex direto (`Approval.process()`) — não havia nenhum gatilho automático quando a Oportunidade chegava ao estágio correto com desconto fora da margem.

**Correção:** novo Flow `Oportunidade_Submete_Aprovacao_Desconto` (Record-Triggered, Opportunity, disparo em Atualização):

- **Critério de entrada (Start):** `StageName = "Apresentação de Custo"` (a plataforma não permite comparar dois campos do registro — `PrecoFinal__c < Amount` — diretamente no critério de entrada do Start; erro confirmado em deploy: *"O elemento Início não pode ter uma condição de filtro de registro que faça referência a um recurso ou elemento"*).
- **Decision** (`Decision_Desconto_Abaixo_Margem`): resolve a comparação de campo a campo (`PrecoFinal__c < Amount`) e verifica que `StatusAprovacaoDesconto__c` ainda está em branco (evita ressubmissão em toda gravação subsequente da mesma Oportunidade, inclusive a gravação gerada pelo próprio Field Update do Approval Process ao submeter).
- **Ação:** `Submit for Approval` (`processDefinitionNameOrId = Aprovacao_Desconto_Oportunidade`), com `submitterId = $Record.OwnerId` (necessário porque o Flow roda como Automated Process User, e o Approval Process exige `allowedSubmitters=owner`).
- **Fault path:** cria uma Task de alerta para o Owner da Oportunidade se a submissão falhar (ex.: já existe uma aprovação pendente), em vez de falhar silenciosamente.

**Revisão técnica:** conduzida com a persona do agente `flow-reviewer` deste projeto (subagent_type nativo indisponível nesta sessão — persona carregada via agente geral a partir de `.claude/agents/flow-reviewer.md`). Veredito: **aprovado com ressalvas**; nenhum bloqueio; parâmetros da action `submit` e validade de `doesRequireRecordChangedToMeetCriteria`/Decision confirmados corretos. Descrições adicionadas aos elementos por recomendação da revisão.

**Deploy:**
```
sf project deploy start --source-dir force-app/main/default/flows/Oportunidade_Submete_Aprovacao_Desconto.flow-meta.xml --target-org hackaton2
```
Resultado: `Succeeded`, Flow `Active`.

**Teste ponta a ponta via Anonymous Apex** (update real de registro, não `Approval.process()` direto — registros de teste removidos após validação):

| Cenário | Ação | Resultado esperado | Resultado obtido |
| --- | --- | --- | --- |
| Positivo | Opportunity → `StageName="Apresentação de Custo"`, `PrecoFinal__c=800 < Amount=1000` | `StatusAprovacaoDesconto__c='Pendente'`, 1 work item de aprovação | ✅ `Pendente`; 1 work item |
| Idempotência | Mesma Opportunity, editar campo não relacionado (`Description`) | Não ressubmeter, não duplicar work item, nenhuma Task de falha | ✅ ainda 1 work item; 0 Tasks de falha |
| Negativo | Outra Opportunity, `StageName="Apresentação de Custo"`, `PrecoFinal__c=1200 ≥ Amount=1000` | Não submeter | ✅ `StatusAprovacaoDesconto__c=null` |

**Status: corrigido, deployado e testado (3/3 cenários OK).**

**Limitações conhecidas, documentadas e não corrigidas nesta demanda** (transparência, não bloqueio):
- Se a aprovação for recall (`allowRecall=true` no Approval Process) sem alteração de `StageName`/`PrecoFinal__c`/`Amount`, o Flow não ressubmete automaticamente (o `Decision` só reavalia `StatusAprovacaoDesconto__c` em branco; um recall não limpa esse campo). Risco residual baixo, fora do escopo pedido.
- O fault path (Task de alerta) não tem faultConnector próprio — se a própria criação da Task falhar, não há segunda camada de tratamento além do alerta padrão de erro não tratado do Process Automation Settings da org.

---

## 2. Massa de dados de teste (Anonymous Apex, registros persistentes)

Script único (`sf apex run`), executado com sucesso na primeira tentativa, sem erros de validação. Todos os registros abaixo **permanecem na org** (não foram removidos — são a massa de dados solicitada, diferente dos registros de teste do Flow na seção 1.2, que foram removidos após validação).

| # | Objeto | Registros criados | Detalhe |
| --- | --- | --- | --- |
| 1 | Account | **2** (1 PJ + 1 PF) | PJ: "Industria Alfa Quimica Ltda" (`TipoPessoa__c=PJ`, `CNPJ_CPF__c`, `LinhaDeProduto__c=Cromata;Flecha`, `OrigemCadastro__c=Indicação`, `UltimaCompra__c`, `PossuiContratoRecorrente__c=true`, `VolumeMinimoMensal__c=5000`). PF: "Marcos Vinicius Pereira" (mesmos campos, `PossuiContratoRecorrente__c=false`) |
| 2 | Contact | **2** | Vinculados às 2 Contas acima, com `Cargo__c`, `Email`, `Phone` (+ `AreaResponsavel__c` no contato da Conta PJ, exigido pela Validation Rule `Contato_PJ_Campos_Obrigatorios`) |
| 3 | Lead | **1** (PJ) | "Beta Revestimentos Industriais SA" — `Company`, `Name`, `Email`, `Phone`, `CNPJ_CPF__c`, `LinhaDeInteresse__c=Flexa` (ver desvio documentado na seção 4) |
| 4 | Product2 | **2** (ativos) | "Verniz Industrial Alfa 500" e "Tinta Jato Digital Beta 1L", com `DescricaoTecnica__c` e `PrecoBaseAprovado__c` |
| 5 | PricebookEntry | **2** (ativas, Pricebook Padrão) | Uma por produto acima |
| 6 | Opportunity | **2** (1 Caminho A + 1 Caminho B) | Caminho A vinculada à Account PF (`Amount=5000,00` após rollup automático, `PrecoFinal__c=4750,00`, `CotacaoDolarReferencia__c=5,35`, `IndicadorUrgencia__c=true`). Caminho B vinculada à Account PJ (`Amount=11000,00`, `PrecoFinal__c=11000,00`, `CotacaoDolarReferencia__c=5,40`, `IndicadorUrgencia__c=false`) |
| 7 | OpportunityLineItem | **2** | 1 por Oportunidade, com `PrecoVendido__c` preenchido |
| 8 | Amostra__c | **2** (1 Reprovada + 1 Aprovada) | Ambas vinculadas à Oportunidade Caminho B, com `ProdutoAmostrado__c`, `PesoVolumeEnviado__c`, `DataEnvio__c`, `NumeroTentativa__c` (1 e 2), `Resultado__c`, `CustoEstimado__c` |
| 9 | Case | **1** ("Envio e Teste de Amostra") | Criado **automaticamente pelo Flow** `Amostra_Reprovada_Cria_Case` ao inserir a Amostra Reprovada; complementado nesta demanda com `ContactId`, `CausaTecnicaReprovacao__c=Incompatibilidade com Substrato`, `MarcacaoVisitaTecnica__c=true`, `DataVisitaTecnica__c`. `OwnerId` confirmado = Queue "Laboratório" (automático, sem intervenção manual) |

**Validações executadas (via SOQL, no próprio script e depois via `sf data query`):**
- `Case.OwnerId == Id da Queue Laboratorio` → `true`.
- `Case.AccountId == Account PJ` → `true`; `Case.ContactId == Contact PJ` → `true`; `Case.Amostra__c == Amostra Reprovada` → `true`.
- `Case.RecordType.DeveloperName == "Envio_e_Teste_de_Amostra"` → confirmado.
- `Opportunity.Amount` recalculado automaticamente pela plataforma como soma dos `OpportunityLineItem` (5.000,00 e 11.000,00) — comportamento esperado, não é um erro do script.

**Total de registros novos criados nesta demanda: 14** (2 Account + 2 Contact + 1 Lead + 2 Product2 + 2 PricebookEntry + 2 Opportunity + 2 OpportunityLineItem + 2 Amostra__c — o Case foi criado pela automação, não diretamente pelo script, e por isso contado separadamente na tabela acima).

---

## 3. Desvios e decisões documentadas (transparência)

| # | Item | Decisão tomada e motivo |
| --- | --- | --- |
| 1 | `Lead.AreaResponsavel__c` | Campo pedido para o Lead **não existe** no schema (nem local, nem na org — confirmado via describe). Esse campo existe apenas em `Contact`. Não inventado nem presumido; não preenchido no Lead. |
| 2 | `Lead.EmailFinanceiro__c` e `Lead.ResponsavelFechamento__c` | Não estavam na lista de campos pedida para o Lead, mas são exigidos pela Validation Rule `Lead_PJ_Campos_Obrigatorios` para `TipoPessoa__c=PJ` — preenchidos para permitir o insert, sem os quais o Lead PJ não teria sido cadastrado. |
| 3 | `Contact.AreaResponsavel__c` no contato da Conta PJ | Não estava na lista pedida para os Contacts, mas é exigido pela Validation Rule `Contato_PJ_Campos_Obrigatorios` — preenchido pelo mesmo motivo do item 2. |
| 4 | Arquivos de outra sessão incluídos no `git add force-app/` | O retrieve final trouxe metadata completa e já funcionando de uma demanda em andamento por outra sessão/dev, não relacionada a esta tarefa: campo `Contact.AreaResponsavel__c`, `Opportunity.LinhaDeProduto__c`, 2 novas Validation Rules (`Conta_PJ_Campos_Obrigatorios`, `Contato_PJ_Campos_Obrigatorios`), ajustes de Layout/FLS e picklist de `Case.Type` no Record Type "Envio e Teste de Amostra". Confirmado que são metadata **completa e já ativa na org** (não um estado parcial/quebrado — a própria massa de dados desta demanda dependeu dessas Validation Rules para inserir os Contacts corretamente). Incluídos no commit por instrução explícita (`git add force-app/`) e por serem consistentes com a política deste projeto de manter o repositório sem *drift* em relação ao estado real da org (mesmo princípio das ADRs 0004/0005). |

---

## 4. Retrieve e manifest

- `manifest/package.xml` atualizado: novo membro `Oportunidade_Submete_Aprovacao_Desconto` no tipo `Flow`.
- `sf project retrieve start --manifest manifest/package.xml --target-org hackaton2` executado com sucesso; metadata local sincronizada com o estado real da org antes do commit (regra central 2 do `CLAUDE.md`).
- `sharingModel` de `Account`/`Case`/`Opportunity` confirmado como `Read` (Public Read Only) — sem recorrência do problema das ADRs 0005/demandas 10/11.

---

## 5. Resumo de status

| Item | Status |
| --- | --- |
| FLS de `Amostra__c` (3 Permission Sets) | ✅ Corrigido e confirmado via SOQL |
| Flow de submissão automática de aprovação de desconto | ✅ Criado, deployado (`Active`) e testado (3/3 cenários) |
| Massa de dados de teste (Parte 2) | ✅ 14 registros novos criados + 1 Case gerado por automação, todos validados via SOQL |
| Retrieve + manifest | ✅ Executado, `sharingModel` confirmado íntegro |
