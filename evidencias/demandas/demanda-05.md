# Demanda atual

> Escreva aqui a descrição da tarefa a ser executada — pode ser um pedaço do backlog do Tarefai, uma pergunta nova do cliente, ou qualquer trabalho de implementação. Depois de escrever, rode `/executar-demanda NN` no Claude Code (NN = número sequencial, ex.: 01, 02...). Ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md).

## O que fazer

[Cromatta Química] - [Tarefa 5 - Sales] Configuração dos Objetos Conta e Contato

**Contexto:** Conta e Contato são a base de todo o modelo — Lead converte para eles, Oportunidade e relatórios dependem deles. Precisam existir antes da conversão de Lead ser configurada.

**Objetivo:** Ter os campos de Conta e Contato prontos para receber os dados vindos da conversão de Lead.

**Descrição Detalhada:**
- Criar em Conta (Account):
  * TipoPessoa__c (Picklist: PF, PJ)
  * CNPJ_CPF__c (Text)
  * LinhaDeProduto__c (Multiselect Picklist)
  * OrigemCadastro__c (Picklist/Text)
  * UltimaCompra__c (Date)
  * StatusCarteira__c (Formula - Text: "Ativo" se UltimaCompra__c até 60 dias; "Inativo" se acima de 60 dias)
  * PossuiContratoRecorrente__c (Checkbox)
  * VolumeMinimoMensal__c (Number)
- Criar em Contato (Contact):
  * Cargo__c (Picklist: comprador, químico, decisor)

## Critério de aceite

- Campos criados em Conta e Contato.
- Fórmula de StatusCarteira__c calculada e testada com uma data de compra simulada.
- Campos de contrato recorrente testados em uma Conta de exemplo.

---

## Execução — registro (via Claude/CLI, org `hackaton2`)

**Status: concluída.**

1. **Numeração:** este repositório não tem demandas 03/04 registradas em `evidencias/log.md` — a Demanda 05 foi executada mesmo assim, por instrução explícita, sem tentar preencher a lacuna.
2. **Campos criados** (metadata declarativa, `sf project deploy start`):
   - `Account.TipoPessoa__c` (Picklist: PF, PJ)
   - `Account.CNPJ_CPF__c` (Text, 20)
   - `Account.LinhaDeProduto__c` (MultiselectPicklist: Cromata, Flecha, Jato)
   - `Account.OrigemCadastro__c` (Picklist: Feira, Indicação, Prospecção Ativa, Internet — mesmos valores já usados na origem do Lead em `business-scenario.md`, para manter consistência campo a campo na conversão)
   - `Account.UltimaCompra__c` (Date)
   - `Account.StatusCarteira__c` (Formula Text: `"Ativo"` se `UltimaCompra__c` ≤ 60 dias, `"Inativo"` se > 60 dias, **`"Sem Compras"` se em branco** — caso de borda não especificado na demanda, adicionado para a fórmula não devolver vazio numa Conta nova sem histórico de compra)
   - `Account.PossuiContratoRecorrente__c` (Checkbox)
   - `Account.VolumeMinimoMensal__c` (Number 16,2)
   - `Contact.Cargo__c` (Picklist: Comprador, Químico, Decisor)
3. **FLS:** concedida explicitamente no profile `Admin` (lição da Demanda 02 — campo novo não fica visível nem para o admin sem isso) e no Permission Set `Vendedor` (leitura/edição em todos os campos novos, exceto `StatusCarteira__c` que é fórmula — somente leitura em ambos por ser calculada).
4. **Validação com dados de teste** (via CLI `sf data create/query/delete`, não Apex — não havia necessidade de código para popular/validar campos, regra de preferência declarativa de `architecture.md`): 3 Contas de teste cobrindo os 3 ramos da fórmula (compra há 24 dias → `Ativo`; há mais de 60 dias → `Inativo`; sem data → `Sem Compras`) e 2 Contatos com `Cargo__c` preenchido, todos confirmados via SOQL e depois **removidos** da org (eram só para validação, não fazem parte do dataset real da Cromatta).
5. **Manifest:** adicionado `Contact` à lista de `CustomObject` (member) em `manifest/package.xml` — os campos novos de `Account`/`User` já eram cobertos pelos members existentes. Retrieve completo executado após o deploy, refletindo o estado real da org antes do commit.
