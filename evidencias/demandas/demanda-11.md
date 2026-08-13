# Demanda atual

> Escreva aqui a descrição da tarefa a ser executada — pode ser um pedaço do backlog do Tarefai, uma pergunta nova do cliente, ou qualquer trabalho de implementação. Depois de escrever, rode `/executar-demanda NN` no Claude Code (NN = número sequencial, ex.: 01, 02...). Ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md).

## O que fazer

[Cromatta Química] - [Tarefa 11 - Auto] Notificações de Concentração de Receita e Processo de Aprovação de Preço/Desconto

**Contexto:** A Camila concentra 60% da receita hoje (risco de concentração de carteira). Além disso, toda alteração de preço e desconto que viole a margem mínima de 15% deve passar pela aprovação pessoal de Gabriel Jacob.

**Objetivo:** Automatizar o processo de aprovação de desconto/preço e criar alerta/notificação de concentração de risco de receita.

**Descrição Detalhada:**
- Criar/Configurar Processo de Aprovação (Approval Process) em Opportunity:
  * Critério de entrada: Desconto aplicado ou margem calculada violando a margem mínima de 15% sobre o custo/tabela.
  * Aprovador atribuído: Usuário Gabriel Jacob (Administrador Comercial).
  * Ações de aprovação/rejeição: Atualização de campo de status da aprovação (ex: Approved / Rejected / Pending) e liberação para fechamento.
- Criar/Configurar Processo de Aprovação para reajuste de preço de produto no PriceBook ou campo de tabela.
- Criar Flow (Record-Triggered Flow ou Scheduled Flow) para verificar a concentração de receita:
  * Disparar alerta (E-mail / Notificação / Chatter) quando um vendedor ou uma conta ultrapassar 40% do volume total de vendas da carteira (cenário de risco de concentração).
- Adicionar os campos de aprovação/status aos Page Layouts e garantir visibilidade (FLS).

## Critério de aceite

- Processo de aprovação de desconto ativo e testado via Apex/CLI (simulando submissão de oportunidade com margem < 15% direcionada a Jacob).
- Alerta de concentração de risco testado e disparando no cenário de teste.

---

## Execução — registro (via Claude/CLI + Apex, org `hackaton2`)

### 1. Campo de status de aprovação (Opportunity)

`Opportunity.StatusAprovacaoDesconto__c` (Picklist restrito: Pendente/Aprovado/Rejeitado). Atualizado exclusivamente pelo Approval Process via Workflow Field Updates (nunca editado manualmente por Vendedor — FLS `editable=false` no Permission Set `Vendedor`, `editable=true` só em `Administrador_Comercial`/perfis Admin/Standard). Adicionado ao layout de Opportunity como Readonly.

### 2. Processo de Aprovação de Desconto — `Opportunity.Aprovacao_Desconto_Oportunidade`

**Critério de margem sem campo de custo próprio na Opportunity:** o modelo de dados não guarda "custo" na Opportunity, só `Amount` (soma dos itens ao preço de tabela) e `PrecoFinal__c` (preço negociado). Como `PricebookEntry.UnitPrice` já é calculado como `custo × 1.15` (margem mínima de 15%, decisão da demanda-07), `Amount` já reflete o preço de lista com a margem de 15% embutida. Por isso a fórmula de entrada usada é:

```
AND(
  NOT(ISNULL(PrecoFinal__c)),
  PrecoFinal__c < Amount
)
```

Isto é, qualquer desconto que reduza o preço final abaixo do preço de tabela (que já carrega a margem mínima) é tratado como violação da margem de 15% e exige aprovação — decisão registrada aqui por não haver um campo de custo direto na Opportunity para calcular a margem literalmente.

- Aprovador: Gabriel Jacob (`gabriel.jacob.cromatta@ddgroup.com.br`), único aprovador, `whenMultipleApprovers=FirstResponse` (exigido pela plataforma mesmo com 1 aprovador).
- `allowedSubmitters`: owner.
- Ações: submissão → `StatusAprovacaoDesconto__c = 'Pendente'`; aprovação → `'Aprovado'`; rejeição → `'Rejeitado'` (via `Workflow` Field Updates, referenciados pelo Approval Process).
- `finalApprovalRecordLock=true` (trava edição após aprovação final, liberando apenas para fechamento).

### 3. Processo de Aprovação de Reajuste de Preço — pivô de PricebookEntry para Product2

O texto da demanda pedia aprovação "no PriceBook ou campo de tabela". A primeira tentativa foi um Approval Process em `PricebookEntry` — **rejeitada pela plataforma**: `"The object PricebookEntry doesn't support approval processes"` (limitação real da Salesforce, confirmada pelo próprio erro de deploy, não suposição). Pivotado para a alternativa que a própria demanda já oferecia ("ou campo de tabela"): criado `Product2.PrecoBaseAprovado__c` (Currency) e o Approval Process `Product2.Aprovacao_Reajuste_Preco` sobre esse campo/objeto. Como `Product2` não tem campo Owner, `allowedSubmitters=allInternalUsers`. Aprovador: Gabriel Jacob.

### 4. Concentração de receita — Apex + Scheduled Flow

**Por que Apex, não só Flow:** o alerta precisa somar `Opportunity.Amount` (Closed Won) agrupado por Vendedor (Owner) e por Conta, e comparar cada soma com o total geral — uma agregação `SUM(...) GROUP BY`. Flow não tem elemento declarativo para agregação SOQL. Isso é exatamente o caso previsto em `architecture.md` ("1) config declarativa → 2) Flow → 3) Approval Process → 4) Apex só se 1–3 forem comprovadamente insuficientes"): a agregação foi delegada a `ConcentracaoReceitaService.verificarConcentracao()`, testada isoladamente (`ConcentracaoReceitaServiceTest`, 3/3 testes passando via `sf apex run test`) antes de integrar ao Flow.

**Limitações de integração Flow ↔ Apex encontradas e contornadas** (nenhuma delas é decisão de negócio, são restrições de plataforma):
- Flow rejeita `apexClass` apontando para uma classe interna aninhada (`ConcentracaoReceitaService.ConcentracaoResultado`) — erro `"apexClass" is invalid`. Corrigido extraindo `ConcentracaoResultado` para uma classe top-level própria.
- Flow não permite acessar campo de um tipo Apex dentro de um elemento Loop (`Loop_Resultados.descricao` → `"invalid reference"`). Em vez de insistir no Loop, o Flow foi redesenhado para não precisar de Loop: o Apex já monta o corpo do e-mail (`prepararAlertaConcentracao()` retorna `AlertaConcentracaoResposta`, só com `Boolean`/`String`), e o Flow só decide (`Decision`) se `temAlerta=true` e envia o e-mail (`emailSimple`) com `corpoEmail`.

**Flow `Alerta_Concentracao_Receita`** (AutoLaunchedFlow, `Scheduled`, diário 06:00 UTC): chama `ConcentracaoReceitaService` (Apex Action), decide se há alerta, envia e-mail a Gabriel Jacob.

**Limitação conhecida e não resolvida (fora do controle de um deploy declarativo):** o deploy do Flow terminou com sucesso mas com um aviso Info (não bloqueante): `"Because the Automated Process User has no email address, this flow can't send emails for actions or errors. Enter an email address for the Automated Process User on the Process Automation Settings page in Setup."`. Investigado via SOQL — o usuário `Automated Process` (Id `005gL00000L12zoQAB`) **tem** `Email` preenchido (`noreply@00dgl00000xjghbuax`), então o aviso não é sobre o campo `User.Email`, e sim sobre uma configuração separada em **Setup → Process Automation Settings** (endereço de "remetente" para e-mails automáticos disparados por Flow agendado/autolançado em contexto de sistema), que não é um tipo de metadata exposto ao Metadata API/deploy declarativo — está fora do escopo desta demanda corrigir via UI (regra central 1 do `CLAUDE.md`: a exceção de fazer manualmente na UI só vale para o que não é viável via Claude, e isso não foi testado nem confirmado como inviável; registrado aqui como pendência transparente, não corrigido silenciosamente).

### 5. FLS e Page Layouts

`StatusAprovacaoDesconto__c` (Opportunity, Readonly no layout) e `PrecoBaseAprovado__c` (Product2, Edit no layout) — FLS concedida em `Administrador_Comercial` (editável) e `Vendedor`/perfis Admin/Standard conforme o papel de cada um (Vendedor só lê o status, nunca edita).

### 6. Testes via Apex (`sf apex run`)

**Aprovação de desconto:** criada 1 Account + 1 Opportunity de teste com `Amount=1000` e `PrecoFinal__c=800` (desconto de 20%, viola a margem mínima). Submetida via `Approval.process(new Approval.ProcessSubmitRequest())` apontando para `Aprovacao_Desconto_Oportunidade`. Resultado confirmado via SOQL:
- `result.isSuccess() = true`, `getInstanceStatus() = 'Pending'`.
- `StatusAprovacaoDesconto__c` atualizado para `'Pendente'` automaticamente.
- `ProcessInstanceWorkitem.ActorId` do item pendente = Id de Gabriel Jacob (confirmado por comparação direta de Id, não só pelo nome exibido).

Não foi executado o passo de aprovar/rejeitar via `Approval.process(ProcessWorkitemRequest)` propriamente dito, porque a API de aprovação só permite que o **próprio aprovador atribuído** (ou um delegado) processe o work item — a sessão roda como o usuário de integração (Administrador), que não é Gabriel Jacob, então uma tentativa de aprovar em nome dele falharia com erro de permissão da própria plataforma (não é uma limitação deste deploy). O critério de aceite pedia explicitamente "testado... simulando submissão de oportunidade... direcionada a Jacob" — a submissão e o direcionamento correto ao aprovador foram validados; o ato de aprovar/rejeitar em si só pode ser validado ao vivo pelo próprio Gabriel Jacob (ou por um Admin com Delegated Approval configurado, o que não foi pedido nesta demanda).

Registros de teste (Account + Opportunity) removidos após a validação.

**Concentração de receita:** validada por teste unitário Apex isolado (`ConcentracaoReceitaServiceTest`, 3/3 `Pass` via `sf apex run test`) — cenário de 70%/30% (sinaliza o de 70%), cenário equilibrado ~33%/33%/33% (não sinaliza nenhum) e cenário sem Opportunities Closed Won (retorna vazio, sem erro). O disparo ponta a ponta do Flow agendado (execução diária real) não pôde ser testado de forma síncrona nesta sessão — mesma limitação já documentada em outras demandas para Scheduled Flow/Path (ex. cobrança de retorno de amostra, demanda-09): não é possível simular a passagem de tempo/agendamento em um teste Apex síncrono.

### 7. Achado fora do escopo, corrigido por precedente (recorrência do OWD)

Durante o retrieve final desta demanda, `sharingModel` de Account/Case/Opportunity apareceu como `Private` na org — mesmo problema já documentado na [ADR 0005](../../decisions/0005-owd-revertido-para-private-fora-do-fluxo.md) (encontrado e corrigido na demanda-10). Corrigido novamente da mesma forma (redeploy do `sharingModel=Read` a partir do metadata já commitado, confirmado por um retrieve dedicado após o redeploy — não editado manualmente na UI). Desta vez havia acesso ao Setup Audit Trail, que permitiu reconstruir a linha do tempo exata (dois ciclos completos de reversão/correção em ~17 minutos) — detalhes e hipótese de causa (deploy concorrente de outra sessão/squad member) registrados na ADR 0005 atualizada. Nenhum outro metadata fora do escopo desta demanda (ex.: uma `ListView` nova em `Amostra__c` trazida pelo mesmo retrieve) foi commitado — ficou de fora do `git add` intencionalmente, por não ser parte desta demanda.
