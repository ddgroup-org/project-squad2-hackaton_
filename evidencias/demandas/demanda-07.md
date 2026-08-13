# Demanda atual

> Escreva aqui a descrição da tarefa a ser executada — pode ser um pedaço do backlog do Tarefai, uma pergunta nova do cliente, ou qualquer trabalho de implementação. Depois de escrever, rode `/executar-demanda NN` no Claude Code (NN = número sequencial, ex.: 01, 02...). Ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md).

## O que fazer

[Cromatta Química] - [Tarefa 7 - Sales] Cadastro do Catálogo de Produtos e Tabela de Preços

**Contexto:** O vendedor apresenta um catálogo técnico ao cliente; o preço final é imputado manualmente pelo comercial.

**Objetivo:** Cadastrar os produtos organizados pelas 3 linhas (Cromatta, Flexa, Jato) a partir dos dados em `dados/`, com Price Book padrão ativo e campo de Preço Vendido na linha da Oportunidade.

**Descrição Detalhada:**
- Inspecionar a pasta `dados/` para localizar o arquivo de catálogo (`.xlsx` ou `.csv`) e ler os produtos das abas existentes (ex: Flexa, Cromatta). Para linhas sem planilha (ex: Jato), utilizar de 3 a 5 produtos de exemplo.
- Criar/garantir os campos customizados:
  * Em Product2: campo de linha/família de produto (`LinhaDeProduto__c` ou utilizar o campo standard `Family` com os valores: Cromatta, Flexa, Jato) e `DescricaoTecnica__c` (Text/Long Text).
  * Em OpportunityLineItem (Linha de Produto da Oportunidade): campo `PrecoVendido__c` (Currency) para o preço final negociado manualmente pelo comercial.
- Executar um script (Python/Apex) para cadastrar os produtos no objeto Product2 e associá-los ao Standard Pricebook (Pricebook2) criando os respectivos PricebookEntry (ativos e com preço de lista padrão).
- Adicionar os campos customizados aos Layouts de Página correspondentes e garantir visibilidade (FLS).

## Critério de aceite

- Produtos das 3 linhas cadastrados e ativos no Price Book padrão.
- Campo `PrecoVendido__c` ativo e testado no objeto OpportunityLineItem.
- Consulta SOQL comprovando a criação dos produtos e PricebookEntries.

---

## Execução — registro (via Claude/CLI + Apex, org `hackaton2`)

**Status: concluída.**

1. **Catálogo real, sem invenção:** `dados/Catalogo.xlsx` tem 3 abas — "Leia-me", "Flexa (B2B revenda)" e "Cromatta (indústria)". Não há aba dedicada a Jato, mas a aba Cromatta já contém um **segmento** "Jato — Impressão Digital" com 8 produtos reais (CRM-J01 a CRM-J08). Usei esses produtos reais para a linha Jato em vez de inventar 3-5 produtos de exemplo, como a demanda sugeria como alternativa apenas para o caso de não haver dados — havia dados, então não presumi a ausência deles.
2. **54 produtos cadastrados:** Flexa (30), Cromata (16, segmentos Dispersão de Pigmentos/Tintas/Ligantes), Jato (8). Planilha lida via parsing manual do XML interno do `.xlsx` (não havia Python disponível no ambiente — só o stub da Microsoft Store; usei Node.js, que já era usado pelo MCP do projeto).
3. **Grafia do campo `Family`:** a demanda pedia valores "Cromatta, Flexa, Jato" — usei **Cromata** (um só "t") seguindo a grafia oficial do BRD/`architecture.md`, mesma correção já aplicada nas demandas 06/08 (a empresa é "Cromatta", a linha de produto é "Cromata").
4. **`Product2.Family` é um `StandardValueSet` global** (`Product2Family`), não um campo com `valueSet` próprio — descoberto por erro de deploy ("cannot define valueSet on a standard field"), corrigido depois. Os 3 valores novos foram adicionados sem remover o valor pré-existente "None".
5. **Preço de lista:** como a planilha só tem "Custo unitário" (fictício, conforme nota da própria planilha) e não um preço de venda, usei `PrecoLista = Custo × 1.15` (margem mínima de 15% sobre o custo, regra já confirmada em `business-scenario.md`) como `PricebookEntry.UnitPrice`. Isso é diferente e não deve ser confundido com `PrecoVendido__c` (em `OpportunityLineItem`), que é o preço final negociado manualmente pelo comercial — os dois campos foram testados juntos no mesmo cenário (ver item 7).
6. **Standard Pricebook estava inativo** (`IsActive=false`) — precisou ser ativado antes de criar `PricebookEntry` ativos.
7. **Teste via Apex (`sf apex run`, scripts não commitados):**
   - Carga dos 54 `Product2` + 54 `PricebookEntry` (ativos, `UnitPrice` = custo × 1.15) em uma única execução — confirmado via SOQL (`GROUP BY Family`: Flexa 30, Cromata 16, Jato 8; `COUNT` de `PricebookEntry` ativos = 54). Há também 1 `Product2` pré-existente na org ("Shipping Charge Product", de antes deste projeto) com `Family` em branco — não é nosso, não foi tocado.
   - Teste de `PrecoVendido__c`: criada 1 Account + 1 Opportunity + 1 `OpportunityLineItem` de teste com `UnitPrice` (lista) = 21.28 e `PrecoVendido__c` (negociado, 10% de desconto) = 19.152 — confirmado via SOQL que os dois valores coexistem corretamente e são independentes.
   - Registros de teste (Account/Opportunity/OpportunityLineItem) removidos após validação — os 54 produtos e PricebookEntries do catálogo real **permanecem** na org (são o entregável desta demanda, não dados de teste).
8. **FLS + Page Layout:** `DescricaoTecnica__c` (Product2) e `PrecoVendido__c` (OpportunityLineItem) com FLS no profile Admin/Standard e no Permission Set Vendedor (leitura para Product2, leitura+edição para o preço vendido); adicionados aos layouts `Product2-Product Layout` e `OpportunityLineItem-Opportunity Product Layout`.
9. **`dados/Catalogo.xlsx`:** já estava na pasta do repositório (não versionado) antes desta demanda — commitado agora junto com o restante, conforme pedido no passo 8 da instrução (`git add dados/`).
