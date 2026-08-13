# Análise técnica — Reanálise arquitetural do Solution Design (Demanda 01) — Cromatta Química

| Campo | Valor |
| --- | --- |
| Documento | Reanálise arquitetural — Solution Design Cromatta Química (Squad 02) |
| Demanda de origem | 01 — `evidencias/demandas/demanda-01.md` |
| Cliente/Projeto | Cromatta Química — hackathon DDGROUP (`quimicahackaton`) |
| Org analisada | `cromatta-hackathon` — alias local confirmado via `.sf/config.json`; Organization Id `00DgL00000XJGhBUAX`; Nome "Cromatta Química"; Enterprise Edition; `IsSandbox = false` (Developer/Enterprise dedicada ao evento, não é sandbox de uma Produção real — consistente com `project-context.md`) |
| Autor | salesforce-architect (modo leitura/análise) |
| Data | 2026-08-13 |
| Versão | 1.0 |
| Status do artefato analisado | Ativo, porém **parcialmente desatualizado** — ver Seção 5 |
| Classificação | Interno |

---

## 1. Resumo executivo

O Solution Design (`entregaveis/02_Solution_Design_Cromatta_Quimica_Squad02.html`) cobre corretamente o núcleo do modelo de dados (Lead → Account/Contact/Opportunity → Product2 → Amostra__c → Case) e toma uma decisão tecnicamente correta ao modelar `Amostra__c` como objeto customizado em Master-Detail com Opportunity — decisão mais bem justificável do que o próprio documento explicita, porque o Master-Detail é o que permite ao objeto herdar o OWD Public Read Only da Opportunity sem sharing rule adicional e habilita rollup summary, algo que o documento tenta usar mas não amarra corretamente (ver Seção 8, dependência #4).

> **Nota pós-análise (2026-08-13):** o BRD oficial (`entregaveis/BRD_Cromatta_Quimica_Squad02_final.pdf`, seção 3.5.2) documenta essa relação como **Lookup**, não Master-Detail. O tech lead decidiu seguir o BRD (ver [ADR 0003](../../decisions/0003-account-sem-record-type-tipopessoa.md) e a entrada "03" em `evidencias/log.md`) — a avaliação técnica abaixo permanece como registro do raciocínio da alternativa Master-Detail, mas **não é mais a decisão vigente** para essa relação específica. Os achados sobre Account/Person Accounts e sobre a reconciliação de metadata (Seções 5, 6, 15) continuam válidos e já foram endereçados nas ADRs 0003/0004.

A reanálise, no entanto, encontrou **dois achados que não são falha do documento em si, mas que tornam parte do seu conteúdo factualmente desatualizado ou pendente de decisão antes de qualquer avanço**:

1. **Crítico — ADR 0001 pode estar assentada sobre uma premissa que não é mais verdadeira nesta org específica.** Consulta direta à org (`cromatta-hackathon`) confirma que o campo `Account.IsPersonAccount` existe e que há um Record Type nativo `PersonAccount` (`IsPersonType = true`) — ambos só existem quando **Person Accounts já está habilitado** na org. A ADR 0001 previu textualmente esse cenário ("Caso a organização do hackathon já disponibilize uma org com Person Accounts habilitado antes da execução, esta decisão pode ser revista — mas... exige nova ADR"). Isso ainda não foi feito. O modelo de dados do Solution Design (Seções 2 e 3) foi construído sobre a premissa da ADR 0001 sem essa reverificação.
2. **Crítico — a org já tem parte da "Tarefa 02" (Security Model) implementada, fora do fluxo de evidência do projeto.** Os Permission Sets `Vendedor` e `Laboratorio` já existem na org (criados em 2026-08-13, com descrição citando "demanda-02"), mas não há nenhuma linha para a demanda 02 em `evidencias/log.md`, nenhum arquivo em `force-app/main/default/permissionsets/` e nenhuma Queue "Laboratório" criada. O callout do próprio Solution Design ("ESPECIFICADO, NÃO IMPLEMENTADO") está desatualizado no momento desta análise.

Fora esses dois achados de estado, a Seção 3 (Data Mapping) tem lacunas técnicas concretas e verificáveis: falta um campo de relacionamento entre `Case` e `Amostra__c` (sem o qual o próprio rollup que o documento propõe não é implementável), e o Approval Process de preço/desconto não tem critério de entrada declarado nem confirmação de que `PricebookEntry` suporta Approval Process nativamente.

**Classificação técnica do artefato:** **Aprovado com ressalvas** — o núcleo do desenho é sólido e reaproveitável, mas não deve seguir para a próxima demanda de implementação sem resolver os dois itens críticos e os gaps de alto risco listados na Seção 15.

### Respostas diretas às 5 perguntas

| # | Pergunta | Resposta objetiva |
| --- | --- | --- |
| 1 | Diagrama e Data Mapping completos? | Não integralmente. Núcleo comercial está coberto; faltam: relacionamento Case↔Amostra\_\_c, campos que sustentem o Approval Process de dois níveis, modelagem de metas/quotas por vendedor (explícitas no cenário de negócio) e a automação de atribuição de Owner por linha de produto ("cliente fica com quem trouxe"). Detalhe na Seção 8 e 15. |
| 2 | `Amostra__c` como objeto customizado M-D é a alternativa correta? | Sim — confirmado pela matriz de decisão da Seção 10. M-D é superior a Lookup porque herda sharing da Opportunity (compatível com o Security Model) e habilita rollup summary nativo. O documento acerta a decisão mas não explicita essa justificativa. *(Nota pós-análise: o BRD oficial define Lookup, não M-D — ver nota acima.)* |
| 3 | O Security Model atende "vê tudo, edita só o próprio"? | Sim, no desenho — e a implementação parcial já existente na org confirma a configuração correta (`ViewAllRecords`/`ModifyAllRecords` desligados). Lacunas reais: Lead não tem OWD definido, Gestor não está definido a nível de campo/objeto ("acesso total" é vago), e não há regra de atribuição de Owner na conversão de Lead. Detalhe na Seção 12. |
| 4 | Automações têm dependência de licença/risco técnico não mencionado? | Sim. Maior risco: Approval Process sobre `PricebookEntry` (objeto historicamente não suportado por Approval Process — requer confirmação oficial). Risco de licenciamento do Entitlement Management está sobrestimado pelo documento — evidência da org sugere que o recurso já está disponível. Roteamento químico-por-linha não tem lógica definida (só 2 químicos, 3 linhas). Detalhe na Seção 8 e 15. |
| 5 | Classificação final com riscos por severidade | **Aprovado com ressalvas.** Ver Seção 11 (decisão) e Seção 15 (riscos). |

---

## 2. Contexto

O time precisava de um desenho técnico único antes de configurar qualquer coisa via Claude na org, para evitar retrabalho entre demandas (`demanda-01.md`). O Solution Design consolidou modelo de dados, Data Mapping, Security Model e automações previstas, com base em `architecture.md`, `business-scenario.md` e as ADRs 0001/0002. Esta reanálise foi solicitada para auditar esse entregável antes de qualquer nova demanda de implementação avançar sobre ele.

## 3. Escopo

- Seções 2 e 3 do Solution Design (diagrama de objetos e Data Mapping), confrontadas com `business-scenario.md` e `architecture.md`.
- Seção 4 (Security Model) — aderência ao requisito "vê tudo, edita só o próprio" e riscos.
- Seção 5 (Automações) — dependências de licença e riscos técnicos.
- Decisão `Amostra__c` como objeto customizado Master-Detail — comparação com alternativas.
- Estado real da org `cromatta-hackathon`, verificado de forma independente via MCP (`run_soql_query`), para confirmar ou contestar as afirmações de "não implementado" do próprio documento e das ADRs.
- Classificação técnica final com riscos por severidade.

## 4. Fora do escopo

- Seção 6 do Solution Design ("Uso do Claude por etapa") — não é uma decisão arquitetural, é um plano de execução; não avaliada aqui.
- Revisão de código Apex/LWC — não há nenhum componente desse tipo relacionado a este design.
- Execução de qualquer ação de escrita (criação de metadata, ativação de automação, ajuste de permissão) — modo leitura/análise, conforme solicitado.
- Auditoria completa da "Tarefa 02" (Security Model) como demanda própria — ela é citada aqui apenas como evidência de estado real, não avaliada em profundidade como entrega independente.
- Confirmação definitiva de licenciamento do Entitlement Management via Setup (a consulta objeto-a-objeto usada aqui é evidência indireta, não uma confirmação de feature flag) — registrado como limitação (Seção 19).

## 5. Estado atual (com evidência)

**O documento afirma, na Seção 4:** "ESPECIFICADO, NÃO IMPLEMENTADO... nenhum Permission Set, Sharing Rule ou objeto 'Amostra' relacionado a este projeto existe hoje na org."

**A verificação independente feita nesta análise, executada agora contra a org `cromatta-hackathon`, mostra um quadro parcialmente diferente:**

- `Amostra__c` **não existe** — confirmado (`EntityDefinition` vazio para `%Amostra%`). Nisso o documento está correto e atual.
- Os Permission Sets **`Vendedor`** e **`Laboratorio`** **já existem** na org, criados em `2026-08-13T14:28:07Z` e `2026-08-13T14:33:07Z`, com descrição interna citando explicitamente "demanda-02 e architecture.md". Isso significa que uma demanda 02 já foi executada contra a org **depois** da geração deste Solution Design, mas:
  - não há entrada correspondente em `evidencias/log.md` (só existe a linha 01);
  - não há `force-app/main/default/permissionsets/` no repositório;
  - não há Queue chamada "Laboratório" (só existe a Queue padrão `Default_Queue_Agentforce_Contact_Center`);
  - não existe Permission Set `Gestor`;
  - nenhum dos dois Permission Sets tem atribuição a usuário (`PermissionSetAssignment` retorna 0 registros para ambos).
- O Account do org tem o Record Type nativo **`PersonAccount`** (`IsPersonType = true`) além do customizado `Business_Account` — a existência desse Record Type nativo só é possível se **Person Accounts já estiver habilitado** nesta org, contrariando a premissa de indisponibilidade da ADR 0001. Nenhum registro de Account criado até o momento é Person Account (`IsPersonAccount = false` no registro amostrado) e não há Account/Opportunity criados na data de hoje — ou seja, **o custo de decidir agora é próximo de zero**, mas a decisão precisa ser tomada antes que dados reais sejam carregados.
- `Entitlement` é um objeto consultável na org e já tem 1 registro — indício de que o recurso Entitlement Management está habilitado (ou ao menos disponível) nesta org, o que reduz o risco que o próprio Solution Design levanta na Seção 5. `Service Cloud` aparece como `UserLicense` ativa (30 licenças, 0 em uso).

**Conclusão da Seção 5:** o estado real da org, no momento desta análise, diverge do estado descrito no Solution Design e nas ADRs que o sustentam. Por precedência (`instruction-precedence.md`, nível 3 — estado real verificado — prevalece sobre a afirmação do documento), estas divergências são tratadas como fato, não como hipótese, e detalhadas como risco crítico na Seção 15.

## 6. Evidências analisadas

| Tipo de evidência | Fonte | Resultado | Observação |
| --- | --- | --- | --- |
| Consulta à org | `SELECT Id, Name, OrganizationType, IsSandbox, InstanceName FROM Organization` | 1 registro: Cromatta Química, Enterprise Edition, `IsSandbox=false` | Confirma identidade da org analisada |
| Consulta à org | `SELECT ... FROM PermissionSet WHERE IsCustom = true` | 88 Permission Sets, incluindo `Laboratorio` e `Vendedor` (customizados, criados em 2026-08-13) | Contradiz o callout "não implementado" do Solution Design |
| Consulta à org | `SELECT ... FROM ObjectPermissions WHERE ParentId IN (SELECT Id FROM PermissionSet WHERE Name = 'Vendedor')` | CRU (sem Delete) em Lead/Account/Contact/Opportunity/Case; Read em Product2; `ViewAllRecords`/`ModifyAllRecords` = false em todos | Implementação real coerente com "vê tudo (via OWD), edita só o próprio" |
| Consulta à org | `SELECT ... FROM ObjectPermissions WHERE ParentId IN (SELECT Id FROM PermissionSet WHERE Name = 'Laboratorio')` | Read/Create/Edit em Case; Read em Account/Contact/Opportunity | Coerente com persona Químico/Laboratório do design |
| Consulta à org | `SELECT ... FROM PermissionSetAssignment WHERE PermissionSet.Name IN ('Vendedor','Laboratorio')` | 0 registros | Nenhum usuário tem os Permission Sets atribuídos ainda |
| Consulta à org | `SELECT ... FROM Group WHERE Type = 'Queue'` | Só a Queue padrão do Agentforce Contact Center | Queue "Laboratório" não existe |
| Consulta à org | `SELECT IsPersonAccount, Id FROM Account LIMIT 1` | Query válida (campo existe) | Prova que Person Accounts está habilitado nesta org |
| Consulta à org | `SELECT ... FROM RecordType WHERE SobjectType = 'Account'` | `Business_Account` (custom) e `PersonAccount` (`IsPersonType=true`, nativo) | Confirma Person Accounts habilitado + RT customizado já criado |
| Consulta à org | `SELECT ... FROM EntityDefinition WHERE QualifiedApiName LIKE '%Amostra%'` (Tooling) | 0 registros | Confirma que `Amostra__c` não existe — este ponto do documento está correto |
| Consulta à org | `SELECT COUNT() FROM Account/Opportunity WHERE CreatedDate = TODAY` | 0 em ambos | Nenhum dado real carregado ainda — custo de qualquer pivô no modelo de Account é hoje próximo de zero |
| Consulta à org | `SELECT COUNT() FROM Entitlement` | 1 registro | Indício de que Entitlement Management está habilitado/disponível |
| Consulta à org | `SELECT Name, TotalLicenses, UsedLicenses FROM UserLicense` (filtro Service Cloud) | `Service Cloud`: 30 total, 0 em uso | Licença de Service Cloud confirmada disponível |
| Filesystem | `force-app/main/default/{objects,permissionsets,flows,sharingRules}` | Nenhuma dessas pastas existia no repositório (no momento da análise) | Confirma que nada havia sido *retrieved* para o repositório, mesmo havendo metadata na org |
| Filesystem | `manifest/package.xml` | Só continha ApexClass/Component/Page/Trigger/Aura/LWC/StaticResource "*" | Manifest era o herdado do template padrão do `sf project generate`, não refletia este design |
| Documento do projeto | `evidencias/log.md` | Só havia a linha da demanda 01 | Nenhuma demanda 02 registrada, apesar de metadata na org referenciar "demanda-02" |
| Documento do projeto | `docs/transcricao.md` | Confirma nomes dos químicos ("Sérgio e André", ainda a confirmar oficialmente) e prazos de SLA | Fonte primária consistente com `business-scenario.md` |

## 7. Componentes envolvidos

| Tipo | Componente | Papel na análise | Status |
| --- | --- | --- | --- |
| Custom Object | `Amostra__c` | Objeto central da Seção 2 do Solution Design | Não existe na org (confirmado) |
| Standard Object | `Account`, `Contact`, `Opportunity`, `Case`, `Lead`, `Product2`, `PricebookEntry` | Modelo de dados padrão referenciado | Existem nativamente; Record Types customizados parcialmente criados (`Business_Account`) |
| Record Type | `Business_Account` (Account) | Modelo B2B da ADR 0001 | Já existe na org |
| Record Type | `PersonAccount` (Account) | Recurso nativo que só existe com Person Accounts habilitado | Já existe na org — evidência que contradiz a premissa da ADR 0001 |
| Permission Set | `Vendedor` | Security Model, persona vendedor | Já existe na org, sem atribuição de usuário, não commitado |
| Permission Set | `Laboratorio` | Security Model, persona químico | Já existe na org, sem atribuição de usuário, não commitado |
| Permission Set | `Gestor` | Security Model, persona gestor | Não existe — pendente |
| Queue | "Laboratório" | Roteamento de Case | Não existe — pendente |
| Feature | Entitlement Management | Automação de SLA | Indícios de disponibilidade (objeto acessível, 1 registro) — não confirmado via Setup |
| ADR | `decisions/0001-*.md` | Fundamenta o modelo de Account | Premissa de indisponibilidade de Person Accounts está desatualizada para esta org específica |

## 8. Matriz de dependências

| Artefato origem | Artefato dependente | Tipo | Direção | Impacto funcional | Impacto técnico | Risco de regressão | Evidência | Recomendação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Amostra__c` | `Opportunity` | Master-Detail | Amostra → Opportunity | Sharing e rollup herdados corretamente | Cascade delete de Amostras se Opportunity for excluída | Baixo (comportamento desejado) | architecture.md, Seção 2/3 do Solution Design | Manter — decisão correta *(nota pós-análise: revisto para Lookup pelo BRD, ver nota no topo)* |
| `Amostra__c` | `Product2` | Lookup | Amostra → Product2 | Rastreio de qual produto foi amostrado | Nenhum cascade — correto, produto não deve ser apagado por amostra | Baixo | Data Mapping, linha "Amostra enviada" | Manter |
| **Case** | **`Amostra__c`** | **Ausente (no momento da análise)** | — | Sem relacionamento declarado no Solution Design nem em `architecture.md` na época | Rollup "Numero_da_Tentativa\_\_c (rollup)" descrito na Seção 3 não seria implementável sem um campo de relacionamento | Alto | Data Mapping, linha "Histórico de tentativas" | **Resolvido:** o BRD confirma `Case.AmostraId__c` (Lookup em Amostra__c) — já incorporado em `architecture.md` |
| Approval Process (preço-base) | `PricebookEntry` | Automação → Objeto | Approval → PricebookEntry | Aprovação de preço-base do produto | `PricebookEntry` não consta historicamente na lista de objetos padrão suportados por Approval Process — confirmar na documentação oficial da release/edição antes de prosseguir | Alto — se não suportado, a automação descrita não pode ser implementada como desenhada | Nenhuma evidência de confirmação no documento nem na org | Confirmar suporte oficial; se não suportado, mover "preço-base" para um campo em `Product2` (que suporta Approval Process) ou redesenhar via Flow |
| Approval Process (desconto) | `Opportunity` | Automação → Objeto | Approval → Opportunity | Aprovação de desconto por volume | Nenhum campo declarado como critério de entrada (ex.: percentual de desconto) | Médio — sem critério, o Approval Process não tem gatilho definido | Data Mapping não lista campo de desconto separado de `Valor_Final_de_Venda__c` | Criar campo explícito (ex.: `Percentual_Desconto__c`) como critério de entrada do Approval Process |
| Flow (roteamento laboratório) | Queue "Laboratório" | Automação → Queue | Flow → Queue | Case reprovado é roteado à fila | Queue não existe; roteamento por linha a um dos 2 químicos não tem lógica de mapeamento definida | Médio-Alto | Verificado: só existe Queue padrão do Agentforce | Definir mapeamento linha→químico (Custom Metadata Type ou múltiplas Queues) antes de construir o Flow |
| `Account.RecordType` (ADR 0001) | Modelo de dados inteiro (Seções 2 e 3) | Decisão arquitetural → modelo | ADR → Diagrama | Toda a segmentação PJ/PF do diagrama depende da premissa da ADR | Person Accounts já habilitado nesta org, ao contrário do que a ADR presumiu ser inviável | **Crítico** — decisão de modelagem pode precisar ser revista antes de mais campos/automações serem construídos sobre ela | `IsPersonAccount` e RT `PersonAccount` confirmados na org via SOQL | **Resolvido:** ver [ADR 0003](../../decisions/0003-account-sem-record-type-tipopessoa.md) — BRD define Account único com `TipoPessoa__c` |
| Permission Sets `Vendedor`/`Laboratorio` (já na org) | `evidencias/log.md` / `force-app/` | Rastreabilidade | Org → Repositório | Nenhum, mas rompe a garantia de auditabilidade via Git | Drift entre org e repositório não documentado | **Crítico para governança do projeto** | PermissionSet.CreatedDate + ausência de linha 02 em log.md + ausência de `permissionsets/` | **Resolvido:** ver [ADR 0004](../../decisions/0004-reconciliacao-permissionsets-fora-do-fluxo.md) — retrieve feito, log atualizado |
| Lead (origem, linha de interesse) | Account/Opportunity (Owner) | Regra de negócio → Automação | Lead → Account | "Cliente fica com quem trouxe, dentro da linha" (business-scenario.md) | Nenhuma automação de atribuição de Owner por linha de produto está desenhada | Médio | business-scenario.md, tabela do time comercial; ausência em architecture.md e no Solution Design | Desenhar Assignment Rule/Flow de atribuição de Owner na conversão do Lead |
| Metas por vendedor/linha (business-scenario.md) | Dashboards (architecture.md, item 7) | Dado → Relatório | Meta → Dashboard | Dashboards de "faturamento vs. meta" e "ranking" não têm onde buscar a meta armazenada | Nenhum objeto/campo de meta foi mapeado | Médio | business-scenario.md, seção "Metas e gestão comercial"; ausente na Seção 3 do Solution Design | Definir onde a meta é armazenada (objeto `Quota` nativo do Forecasting, ou Custom Object `Meta__c`) |

## 9. Alternativas avaliadas — modelagem de `Amostra`

### Campos na própria Opportunity
**Descrição:** Armazenar dados de amostra como campos diretos na Opportunity (ex.: `Amostra_1_Data__c`, `Amostra_2_Data__c`...).
**Vantagens:** Nenhum objeto novo; zero curva de aprendizado adicional.
**Limitações:** Requer número fixo e arbitrário de "slots" de amostra; o próprio cenário de negócio exige múltiplas tentativas rastreadas sem limite conhecido a priori; impossível reportar por amostra individual; nenhuma automação por registro de amostra (o Flow de roteamento ao laboratório perde o gatilho natural). **Inaplicável** — descartada corretamente pelo documento, ainda que sem essa justificativa explícita.

### Objeto customizado com Lookup em Opportunity
**Descrição:** `Amostra__c` como Lookup (não Master-Detail) para `Opportunity`.
**Vantagens:** Permite reparenting mais livre; Amostra poderia existir sem Opportunity.
**Limitações:** Contradiz a regra de negócio ("amostra enviada dentro da oportunidade" é sempre atrelada — não existe amostra "solta"); não herda o OWD Public Read Only da Opportunity automaticamente — seria necessário definir OWD próprio para `Amostra__c` e, possivelmente, sharing rules adicionais, o que o próprio Security Model do documento não previu; não suporta rollup summary nativo. *(Nota pós-análise: esta é a alternativa que o BRD oficial efetivamente adotou — ver ADR 0003. A limitação de OWD próprio foi endereçada em `architecture.md`: Amostra__c recebe OWD Public Read Only explícito.)*

### Objeto customizado com Master-Detail em Opportunity (decisão original do documento, superada)
**Descrição:** `Amostra__c` em Master-Detail com `Opportunity`, Lookup com `Product2`.
**Vantagens:** Herda automaticamente o OWD Public Read Only da Opportunity via "Controlled by Parent"; habilita rollup summary nativo; cascade delete evita amostras órfãs.
**Limitações:** Reparenting da Opportunity-pai é mais restrito.
**Status:** Superada pelo BRD oficial, que define Lookup — ver nota no topo do documento.

## 10. Matriz de decisão — modelagem de `Amostra`

| Alternativa | Aderência | Complexidade | Performance | Escalabilidade | Segurança | Testabilidade | Manutenção | Risco | Recomendação (na época da análise) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Campos na Opportunity | Baixa | Baixa | Alta | Baixa (limite fixo de tentativas) | N/A | Baixa | Baixa | Alto (não atende ao requisito) | Não recomendado |
| **Objeto customizado, Lookup** | Média (na época) → **Alta, confirmado pelo BRD** | Média | Alta | Alta | Média → Alta (com OWD próprio definido) | Média | Média | Médio → Baixo | **Decisão final, conforme BRD** |
| Objeto customizado, Master-Detail | Alta (avaliação original) | Média | Alta | Alta | Alta (herda sharing automaticamente) | Alta | Alta | Baixo | Superada pelo BRD |

## 11. Solução recomendada

**Decisão final (pós-BRD):** `Amostra__c` como objeto customizado em **Lookup** com Opportunity e Lookup com Product2, com OWD próprio (Public Read Only) — conforme BRD 3.5.2 e [ADR 0003](../../decisions/0003-account-sem-record-type-tipopessoa.md).

**Decisão sobre o Solution Design como um todo:** **Aprovado com ressalvas**, todas endereçadas nas ADRs 0003 e 0004 e nas atualizações de `architecture.md`/`business-scenario.md` subsequentes a esta análise.

**Fontes oficiais a consultar antes de prosseguir:** Salesforce Help (Person Accounts — habilitação e reversibilidade), documentação oficial de Approval Process (lista de objetos suportados, incluindo `PricebookEntry`), documentação oficial de Entitlement Management (requisitos de habilitação por edição) — nenhuma delas foi confirmada nesta análise por não haver acesso de leitura ao Setup da org além do que é exposto via SOQL/Tooling API.

## 12. Segurança, permissões e governança

- **Sharing e contexto de execução:** OWD Public Read Only em Account/Opportunity/Case está corretamente desenhado para o requisito "vê tudo, edita só o próprio" — a implementação parcial já existente na org confirma isso (`ViewAllRecords`/`ModifyAllRecords = false` em ambos os Permission Sets criados).
- **CRUD e FLS:** confirmado via evidência real que `Vendedor` tem CRU (sem Delete) em Lead/Account/Contact/Opportunity/Case e Read em Product2. `Laboratorio` tem CRU em Case e Read em Account/Contact/Opportunity.
- **Permissionamento — lacunas (endereçadas em `architecture.md`):**
  - Permission Set "Administrador Comercial" (nome oficial do BRD, substitui "Gestor") ainda não existe.
  - `Lead` não tem OWD nem sharing definidos.
  - Nenhuma automação de atribuição de Owner (Account/Opportunity) por vendedor/linha de produto foi desenhada.
- **Licenciamento:** Entitlement Management — evidência indireta sugere disponibilidade, mas não confirmado via Setup/Feature Settings.

## 13. Performance e escalabilidade

Ambiente de hackathon, sem dados reais carregados. Nenhum risco de volume no estado atual ou projetado (6 vendedores, 2 químicos, dezenas/centenas de registros de demonstração).

## 14. Impactos

| Dimensão | Impacto | Severidade |
| --- | --- | --- |
| Funcional | Rastreabilidade de amostra até o Case — resolvida pelo `AmostraId__c` do BRD | Resolvido |
| Funcional | Aprovação de preço-base pode não ser implementável como desenhada em `PricebookEntry` | Alto |
| Técnico | Modelo de Account — resolvido, ver ADR 0003 | Resolvido |
| Governança | Drift entre org e repositório — resolvido, ver ADR 0004 | Resolvido |
| Segurança | Ausência de definição de OWD para Lead | Médio |
| Automações | Roteamento químico-por-linha sem lógica de mapeamento definida | Médio-Alto |
| Relatórios/dashboards | Ausência de modelo de dados para metas/quotas | Médio |

## 15. Riscos

| # | Risco | Severidade | Status |
| --- | --- | --- | --- |
| 1 | Modelo de Account construído sobre premissa da ADR 0001 desatualizada | Crítico | **Resolvido — ADR 0003** |
| 2 | Progresso na org sem registro em `evidencias/log.md` | Crítico | **Resolvido — ADR 0004, entrada 02 do log** |
| 3 | Ausência de relacionamento Case↔Amostra\_\_c | Alto | **Resolvido — BRD confirma `AmostraId__c`, já em `architecture.md`** |
| 4 | Approval Process de "preço-base" presume suporte em `PricebookEntry`, não confirmado | Alto | Aberto |
| 5 | Roteamento "por linha de produto ao químico responsável" sem lógica de mapeamento | Alto | Aberto |
| 6 | Approval Process de desconto sem campo de critério de entrada | Médio-Alto | Aberto |
| 7 | Permission Set do Administrador Comercial não detalhado a nível de objeto/campo | Médio | Aberto |
| 8 | Nenhuma automação de atribuição de Owner de Account/Opportunity por linha na conversão do Lead | Médio | Aberto |
| 9 | Nenhum objeto/campo para metas/quotas por vendedor | Médio | Aberto |
| 10 | OWD de Lead não definido | Baixo-Médio | Aberto |
| 11 | Risco de licenciamento do Entitlement Management pode estar sobrestimado | Baixo | Aberto (a favor) |

## 16–18. Critérios de aceite, testes e rollback

Ver seções equivalentes no corpo original desta análise (arquivada sem alteração de conteúdo abaixo deste ponto) — nenhuma ação de escrita foi executada por este agente; toda reconciliação foi feita posteriormente, por decisão do tech lead, registrada nas ADRs 0003 e 0004.

## 19. Limitações da análise

| # | O que não foi validado | Risco residual | Validação necessária |
| --- | --- | --- | --- |
| 1 | Habilitação formal do Entitlement Management via Setup/Feature Settings | Baixo-médio | Confirmar em Setup > Feature Settings > Service > Entitlement Management |
| 2 | Suporte oficial de Approval Process sobre `PricebookEntry` | Alto se não suportado | Consultar documentação oficial de Approval Process |
| 3 | Origem exata da criação dos Permission Sets (confirmado depois: Ricardo Custodio, mentor) | Resolvido — ver ADR 0004 | — |
| 4 | Se Person Accounts foi habilitado deliberadamente ou é padrão do template da org | Médio | Consultar Setup Audit Trail |
| 5 | FLS dos Permission Sets já criados | Baixo | Revisar `FieldPermissions` em auditoria futura |

## 20. Próximos passos

| Prioridade | Ação | Status |
| --- | --- | --- |
| Imediato | Divergência ADR 0001 vs. estado real da org | **Feito — ADR 0003** |
| Imediato | Reconciliar "demanda-02" | **Feito — ADR 0004, retrieve, log 02/03** |
| Antes da próxima demanda de modelo de dados | Campo de relacionamento Case↔Amostra\_\_c | **Feito — `architecture.md` já reflete `AmostraId__c`** |
| Antes da demanda de automações | Confirmar suporte de Approval Process em `PricebookEntry`; critério de entrada do desconto | Aberto |
| Antes da demanda de automações | Lógica de roteamento químico-por-linha | Aberto |
| Antes da demanda de Security Model | Detalhar CRUD/FLS do Permission Set "Administrador Comercial" | Aberto |
| Melhoria futura | Modelar metas/quotas por vendedor | Aberto |

---

**Arquivos lidos para esta análise** (todos em `/Users/paulocarvalho/Desktop/cromatta`): `evidencias/demandas/demanda-01.md`, `entregaveis/02_Solution_Design_Cromatta_Quimica_Squad02.html`, `architecture.md`, `business-scenario.md`, `decisions/0001-modelo-conta-b2b-b2c-sem-person-accounts.md`, `decisions/0002-sem-integracao-erp-precificacao-v1.md`, `evidencias/log.md`, `docs/project-context.md`, `docs/transcricao.md` (busca direcionada), `manifest/package.xml`, árvore de `force-app/main/default/`, e os documentos de governança/padrões em `knowledge/` e `templates/` deste mesmo repositório. Consultas ao vivo executadas contra a org `cromatta-hackathon` via `run_soql_query` (Organization, PermissionSet, ObjectPermissions, PermissionSetAssignment, Group, RecordType, Account, EntityDefinition, Entitlement, UserLicense, PermissionSetLicense) e `get_username`.

Nenhum arquivo foi criado, alterado ou deployado por este agente. Nenhum commit, push ou escrita na org foi executado por ele — análise inteiramente em modo leitura. As reconciliações registradas nas notas acima (ADRs 0003/0004, atualizações de `architecture.md`) foram decisões e ações do tech lead/Claude em sessão posterior, não deste agente.
