# Demanda atual

> Escreva aqui a descrição da tarefa a ser executada — pode ser um pedaço do backlog do Tarefai, uma pergunta nova do cliente, ou qualquer trabalho de implementação. Depois de escrever, rode `/executar-demanda NN` no Claude Code (NN = número sequencial, ex.: 01, 02...). Ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md).

## O que fazer

[Cromatta Química] - [Tarefa 8 - Sales] Configuração do Objeto Oportunidade e Etapas do Funil Dual

**Contexto:** Existem dois caminhos comerciais — produto já existente com custo conhecido, e produto novo que precisa ser desenvolvido e testado no laboratório.

**Objetivo:** Modelar os dois fluxos de vendas, Record Types correspondentes e campos de controle (motivo de perda, urgência, contrato e volume mínimo).

**Descrição Detalhada:**
- Criar os dois Record Types e Processos de Venda (Sales Processes) em Opportunity:
  * Caminho A - Produto Existente: Prospecção -> Apresentação de Catálogo Técnico -> Apresentação de Custo -> Negociação -> Fechado (Ganho/Perdido)
  * Caminho B - Produto Novo: Prospecção -> Levantamento Técnico -> Desenvolvimento/Envio de Amostra -> Ajustes -> Formação de Preço -> Fechado (Ganho/Perdido)
- Criar os campos customizados em Opportunity:
  * MotivoDaPerda__c (Picklist: Preço Alto, Prazo Curto, Incompatibilidade Técnica, Desistência por Demora, Outro)
  * IndicadorUrgencia__c (Checkbox - Sinaliza problema com fornecedor atual)
  * PossuiContratoRecorrente__c (Checkbox)
  * VolumeMinimoMensal__c (Number)
- Criar Regra de Validação (Validation Rule) em Opportunity para tornar obrigatorio o preenchimento do campo MotivoDaPerda__c sempre que o estágio (StageName) for alterado para 'Closed Lost' (Fechado Perdido).
- Adicionar os novos campos e seções aos Page Layouts dos dois Record Types de Oportunidade e garantir visibilidade (FLS).

## Critério de aceite

- Dois Record Types e Sales Processes configurados e funcionais.
- Teste Apex criando duas oportunidades (uma para Produto Existente e outra para Produto Novo) simulando a transição de etapas.
- Teste da Validation Rule garantindo bloqueio ao fechar como Perdido sem o Motivo da Perda.

---

## Execução — registro (via Claude/CLI + Apex, org `hackaton2`)

**Status: concluída.**

1. **Numeração:** demanda 07 não existe neste repositório — 08 executada por instrução explícita, sem tentar preencher a lacuna (mesmo padrão da demanda 05/06).
2. **Estágios customizados (`StandardValueSet:OpportunityStage`):** adicionados 8 novos valores globais (Prospecção, Apresentação de Catálogo Técnico, Apresentação de Custo, Negociação, Levantamento Técnico, Desenvolvimento/Envio de Amostra, Ajustes, Formação de Preço), reaproveitando os já existentes `Closed Won`/`Closed Lost` como etapa final de fechamento dos dois caminhos. Confirmado via describe, antes e depois do deploy, que nenhum valor pré-existente (inclusive alguns globais inativos que já estavam na org antes deste projeto) foi removido.
3. **2 Business Processes + 2 Record Types:** `Caminho_A_Produto_Existente` e `Caminho_B_Produto_Novo`, cada um com sua sequência de estágios própria (compartilhando "Prospecção" como etapa inicial comum).
4. **4 campos customizados em Opportunity:** `MotivoDaPerda__c`, `IndicadorUrgencia__c`, `PossuiContratoRecorrente__c`, `VolumeMinimoMensal__c` (os dois últimos espelham os campos homônimos de Account criados na demanda-05, agora também na Opportunity, conforme já previsto em `architecture.md`).
5. **Validation Rule `Motivo_Da_Perda_Obrigatorio`:** usa `ISPICKVAL(StageName, "Closed Lost")` (lição repetida da demanda-06 — comparação direta `=` com picklist não é suportada em fórmula).
6. **FLS + visibilidade de Record Type:** concedidas nos Permission Sets `Administrador_Comercial`/`Vendedor` (via `recordTypeVisibilities`, sem o elemento `<default>` — que só existe no schema de Profile, não de PermissionSet, corrigido após erro de deploy) e nos profiles `Admin`/`Standard` (via `recordTypeVisibilities` + `layoutAssignments` — este último só existe em Profile, por isso os usuários com perfil "Standard User" também precisaram de ajuste direto no profile, não só no Permission Set).
7. **Page Layout:** os 4 campos novos foram adicionados a uma única seção "Dados Comerciais Cromatta" no layout padrão único de Opportunity (`Opportunity-Opportunity Layout`), atribuído explicitamente aos dois Record Types via `layoutAssignments` nos profiles Admin e Standard — não foram criados dois layouts visualmente distintos, já que os 4 campos novos não são específicos de um caminho ou outro.
8. **Teste via Apex (`sf apex run`, script não commitado):**
   - Oportunidade Caminho A criada e avançada por todas as 4 etapas abertas (Prospecção → Apresentação de Catálogo Técnico → Apresentação de Custo → Negociação) sem erro.
   - Oportunidade Caminho B criada e avançada por todas as 5 etapas abertas (Prospecção → Levantamento Técnico → Desenvolvimento/Envio de Amostra → Ajustes → Formação de Preço) sem erro.
   - Tentativa de inserir Opportunity já como `Closed Lost` **sem** `MotivoDaPerda__c` → bloqueada pela Validation Rule, exceção capturada e confirmada (`FIELD_CUSTOM_VALIDATION_EXCEPTION`).
   - Opportunity fechada como `Closed Lost` **com** `MotivoDaPerda__c = "Preço Alto"` → sucesso, sem bloqueio.
   - Registros de teste (Account + 3 Opportunities) removidos da org após validação — não fazem parte do dataset real da Cromatta.
9. **Descoberta de metadata:** `BusinessProcess` é filho de `CustomObject` (vive em `objects/Opportunity/businessProcesses/`, não em uma pasta `businessProcesses/` na raiz de `force-app`) e exige `<fullName>` explícito — diferente do que a primeira tentativa assumiu, corrigido por tentativa/erro e confirmado no deploy final.

---

## Complemento — 2 campos financeiros informativos (via Claude/CLI + Apex, org `hackaton2`)

**Status: concluído.**

1. **2 novos campos em Opportunity:** `PrecoFinal__c` (Currency, preço final negociado e aprovado) e `CotacaoDolarReferencia__c` (Number, 10.4, cotação do dólar apenas informativa — sem cálculo automático vinculado, consistente com a [ADR 0002](../../decisions/0002-sem-integracao-erp-precificacao-v1.md), que já definia que o v1 não teria motor de precificação automático via câmbio).
2. **Page Layout:** os 2 campos foram adicionados à mesma seção "Dados Comerciais Cromatta" do layout único de Opportunity (`Opportunity-Opportunity Layout`) já usado pelos dois Record Types (Caminho A e Caminho B) — sem necessidade de criar layouts novos, já que esse layout já está atribuído a ambos via `layoutAssignments` (ver item 7 da execução original acima).
3. **FLS:** concedida no profile Admin, no profile Standard (base dos 9 usuários) e no Permission Set Vendedor, como pedido.
4. **Teste via Apex (`sf apex run`, script não commitado):** criada 1 Account + 2 Opportunities de teste, uma em cada Record Type (Caminho A e Caminho B), ambas com `PrecoFinal__c` e `CotacaoDolarReferencia__c` preenchidos — confirmado via SOQL que os valores foram gravados corretamente nos dois Record Types. Registros de teste removidos após validação.
5. **Manifest:** `Opportunity` já era membro de `CustomObject` no manifest (desde a execução original desta demanda) — os 2 campos novos já foram cobertos automaticamente pelo retrieve completo, sem necessidade de alterar o manifest.
