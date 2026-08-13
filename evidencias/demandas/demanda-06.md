# Demanda atual

> Escreva aqui a descrição da tarefa a ser executada — pode ser um pedaço do backlog do Tarefai, uma pergunta nova do cliente, ou qualquer trabalho de implementação. Depois de escrever, rode `/executar-demanda NN` no Claude Code (NN = número sequencial, ex.: 01, 02...). Ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md).

## O que fazer

[Cromatta Química] - [Tarefa 6 - Sales] Configuração do Objeto Lead e Regras de Conversão

**Contexto:** A Cromatta prospecta empresas (PJ) e pessoas físicas (PF) via internet, feiras, indicação e visita porta a porta.

**Objetivo:** Capturar e converter leads associando-os à linha de produto de interesse, garantindo obrigatoriedade de campos conforme tipo de pessoa.

**Descrição Detalhada:**
- Criar em Lead os campos customizados:
  * CNPJ_CPF__c (Text)
  * TipoPessoa__c (Picklist: PF, PJ)
  * OrigemProspeccao__c (Picklist: Internet, Feira do Setor, Indicação, Prospecção Ativa/Porta a Porta)
  * LinhaDeInteresse__c (Picklist: Cromatta, Flexa, Jato)
  * EmailFinanceiro__c (Email)
  * ResponsavelFechamento__c (Text)
- Implementar Regras de Validação (Validation Rules) ou obrigatoriedade no layout para tornar obrigatórios:
  * PF: Nome, CNPJ_CPF__c (CPF), E-mail.
  * PJ: CNPJ_CPF__c (CNPJ), Company (Razão Social), EmailFinanceiro__c, ResponsavelFechamento__c.
- Configurar o mapeamento de conversão de Lead (LeadConvertSettings / Custom Field Mapping) para Account, Contact e Opportunity, garantindo que LinhaDeInteresse__c, CNPJ_CPF__c e TipoPessoa__c sejam herdados corretamente na conversão.
- Adicionar os novos campos ao Page Layout do Lead e garantir visibilidade (Field-Level Security) para os perfis.

## Critério de aceite

- Criar e converter 2 Leads de teste via Apex/CLI (um PF e um PJ).
- Confirmar que na conversão os dados migram sem perda para Conta, Contato e Oportunidade.

---

## Execução — registro (via Claude/CLI + Apex, org `hackaton2`)

**Status: concluída**, com um desvio de grafia corrigido e uma limitação técnica documentada.

1. **Correção de grafia:** esta demanda pedia `LinhaDeInteresse__c (Picklist: Cromatta, Flexa, Jato)`. O BRD oficial (fonte de verdade, ver `architecture.md`) usa **Cromata** (um só "t") e **Flexa** — usei essa grafia correta no campo novo. Isso NÃO corrige os campos já existentes com a grafia errada "Flecha/Cromata" (`User.Linha_de_Produto__c`, demanda-02; `Account.LinhaDeProduto__c`, demanda-05) — essa é uma pendência já registrada em `architecture.md`, fora do escopo desta demanda, para uma correção dedicada.
2. **Campos criados em Lead:** `TipoPessoa__c`, `CNPJ_CPF__c`, `OrigemProspeccao__c`, `LinhaDeInteresse__c`, `EmailFinanceiro__c`, `ResponsavelFechamento__c`.
3. **Validation Rules:** `Lead_PF_Campos_Obrigatorios` (Nome/CNPJ_CPF__c/Email obrigatórios quando TipoPessoa__c=PF) e `Lead_PJ_Campos_Obrigatorios` (CNPJ_CPF__c/Company/EmailFinanceiro__c/ResponsavelFechamento__c obrigatórios quando TipoPessoa__c=PJ). Usam `ISPICKVAL()` (comparação direta `=` com picklist não é suportada em fórmula).
4. **Conflito de layout resolvido:** o Lead Layout padrão já tinha `Company` marcado como **Required** no próprio layout — isso bloquearia todo Lead PF (que não precisa de Company) independentemente da Validation Rule. Mudei `Company` para `Edit` no layout, deixando a obrigatoriedade condicional inteiramente a cargo das Validation Rules.
5. **`Lead.Company` já é opcional no schema** (nillable=true) porque Person Accounts está habilitado nesta org (ADR 0003) — confirmado via describe antes de assumir que precisaria de alguma configuração extra para permitir Lead PF sem Company.
6. **Mapeamento de conversão (`LeadConvertSettings`):** mapeado `Lead.TipoPessoa__c` → `Account.TipoPessoa__c` e `Lead.CNPJ_CPF__c` → `Account.CNPJ_CPF__c`. **`LinhaDeInteresse__c` NÃO foi mapeado** — Salesforce rejeitou o deploy com erro de tipo (`Datatype mismatch: Picklist -> MultiPicklist`, `Account.LinhaDeProduto__c` é multiselect). Mapear Picklist→MultiselectPicklist na conversão de Lead não é suportado pela plataforma; reportando em vez de forçar/simular. Fica como gap documentado, resolvível futuramente ao corrigir a pendência de grafia (item 1) ou ao decidir se `LinhaDeInteresse__c` deveria também ser multiselect.
   - Nota técnica de metadata: o tipo correto é `LeadConvertSettings` (não `Settings:LeadConvertSettings` nem pasta `settings/`) — arquivo singleton em `force-app/main/default/LeadConvertSettings/LeadConvertSettings.LeadConvertSetting-meta.xml`, descoberto por tentativa/erro e confirmado via `sf org list metadata-types`.
7. **FLS:** concedida no profile Admin e no Permission Set Vendedor para os 6 campos novos de Lead.
8. **Page Layout:** nova seção "Dados Comerciais Cromatta" no Lead Layout com os 6 campos.
9. **Teste via Apex (`sf apex run`, script não commitado):** criado 1 Lead PF (sem Company, com CPF/Email) e 1 Lead PJ (com Company/CNPJ/EmailFinanceiro__c/ResponsavelFechamento__c), ambos convertidos com sucesso (status picklist real da org é `"Converted"`, não `"Closed - Converted"` como eu havia assumido inicialmente — corrigido após erro `INVALID_STATUS`). Conversão confirmada via SOQL pós-conversão: `Account.TipoPessoa__c` e `Account.CNPJ_CPF__c` migraram corretamente em ambos os casos; `Contact` preservou Nome/E-mail; `Opportunity` foi criada em ambas as conversões. Registros de teste (Lead/Account/Contact/Opportunity) removidos após validação — não fazem parte do dataset real da Cromatta.
10. **Lição operacional repetida:** como em demandas anteriores, um deploy com `rollbackOnError` (padrão) reverte TODO o lote se um componente falhar — por isso corrigi a sintaxe da Validation Rule e reimplantei o lote completo (campos + regras) de uma vez, em vez de assumir que os campos já criados na tentativa anterior persistiram.
