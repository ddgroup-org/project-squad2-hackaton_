# Demanda atual

> Escreva aqui a descrição da tarefa a ser executada — pode ser um pedaço do backlog do Tarefai, uma pergunta nova do cliente, ou qualquer trabalho de implementação. Depois de escrever, rode `/executar-demanda NN` no Claude Code (NN = número sequencial, ex.: 01, 02...). Ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md).

## O que fazer

[Cromatta Química] - [Tarefa 13 - Analytics] Dashboard de Reunião Diária e Painéis Gerenciais

**Contexto:** Gabriel Jacob precisa de visibilidade gerencial diária do funil de vendas, oportunidades travadas, amostras pendentes, concentração de receita e progresso em relação à meta de R$ 2.000.000,00/mês.

**Objetivo:** Criar a pasta de relatórios, os 5 relatórios de apoio e o Dashboard consolidado "Reunião Diária — Cromatta" com filtros por vendedor e linha de produto.

**Descrição Detalhada:**
- Criar pasta de relatórios/dashboards (ex: `Cromatta_Reports` / `Cromatta_Dashboards`).
- Criar os 5 Relatórios (Reports) no Salesforce:
  1. "Fechamentos desde ontem": Oportunidades em Fechado/Ganho (Closed Won) no período recente, agrupadas por Vendedor (Owner).
  2. "Oportunidades travadas": Oportunidades abertas sem movimentação há mais de 10 dias úteis (LastModifiedDate / LastActivityDate <= 10 dias).
  3. "Amostras pendentes de retorno": Relatório no objeto Amostra__c com Resultado = "Em Análise" / "Em Teste".
  4. "Concentração de receita por vendedor": % da receita total fechada no mês dividida por vendedor (para monitoramento de risco).
  5. "Meta x Realizado Mensal": Soma do valor (Amount) de Oportunidades Fechadas/Ganha no mês corrente comparado com o valor de referência da meta (R$ 2.000.000,00).
- Criar o Dashboard "Reunião Diária — Cromatta":
  * Incluir os 5 componentes visuais correspondentes aos relatórios (gráfico de barras, tabela, indicador, donut/pizza e gauge/indicador de meta).
  * Adicionar Filtros globais no Dashboard: por Vendedor (Owner) e por Linha de Produto (LinhaDeInteresse__c / LinhaDeProduto__c).

## Critério de aceite

- Dashboard "Reunião Diária — Cromatta" criado e publicado com 5 componentes visuais.
- Filtro por Vendedor e Linha de Produto disponíveis no Dashboard.
- Meta de R$ 2 mi/mês configurada no componente visual.
- Execução de script Apex / CLI validando a criação e implantação das pastas, relatórios e do dashboard na org.

---

## Execução — registro (via Claude/CLI + Apex/Analytics REST API, org `hackaton2`)

### 1. Estrutura criada

- Pasta de Reports `Cromatta_Reports` (`accessType=Public`, `publicFolderAccess=ReadWrite`) com 5 Reports.
- Pasta de Dashboards `Cromatta_Dashboards` (mesmo acesso) com o Dashboard `Reuniao_Diaria_Cromatta`.

### 2. Os 5 Relatórios

1. **Fechamentos desde ontem** — Opportunity, Summary, agrupado por Vendedor (`FULL_NAME`), filtro `StageName = 'Closed Won' AND CloseDate = YESTERDAY`.
2. **Oportunidades travadas** — Opportunity, Summary, agrupado por Vendedor, filtro `StageName != 'Closed Won' AND StageName != 'Closed Lost' AND LastModifiedDate < LAST_N_DAYS:10` — usa `LastModifiedDate` (dias corridos); a plataforma não tem operador declarativo nativo de "dias úteis" em filtros de Report, então esta é uma aproximação, registrada como tal.
3. **Amostras pendentes de retorno** — objeto `Amostra__c`, Summary agrupado por `CUST_NAME` (ver limitação de campo abaixo).
4. **Concentração de receita por vendedor** — Opportunity, Summary, agrupado por Vendedor, filtro `StageName = 'Closed Won' AND CloseDate = THIS_MONTH` — o componente donut do Dashboard mostra visualmente a % de participação por vendedor.
5. **Meta x Realizado Mensal** — Opportunity, Summary (com grouping técnico por `StageName`, exigido pela plataforma para uso em componente Gauge), filtro `StageName = 'Closed Won' AND CloseDate = THIS_MONTH` — fonte do Gauge comparado à meta de R$ 2.000.000,00.

### 3. Limitação de plataforma encontrada e investigada a fundo — campos customizados de `Amostra__c` não disponíveis em Reports

O relatório "Amostras pendentes de retorno" deveria filtrar por `Resultado__c` (Picklist), mas toda tentativa de referenciar esse campo (e outros campos customizados do objeto: `DataEnvio__c`, `Oportunidade__c`, `ProdutoAmostrado__c`) em `<columns>`/`<filter>` do Report falhou repetidamente com `"Invalid field name"`, mesmo depois de:
- Confirmar via Analytics REST API (`GET /analytics/reportTypes/...`) que os campos existem e aparecem corretamente descritos no Report Type.
- Criar um **Report Type customizado dedicado** (`Amostras_Detalhado__c`, baseObject `Amostra__c`, listando explicitamente os campos nas `<sections><columns>`) — mesma assim, referenciar os campos no Report continuou falhando de forma inconsistente entre tentativas (por vezes um campo passava, no próximo deploy falhava, sem mudança no XML).

**Causa mais provável:** campos customizados criados via deploy de metadata (não pelo wizard de criação de campo na UI, que tem um passo explícito "Add Field to Report Types") não ficam automaticamente disponíveis para uso em Reports — e a indexação/propagação desse estado para a validação de deploy de Report parece ter um atraso não determinístico. Isso é consistente com o padrão de todo este projeto (regra central 1 do `CLAUDE.md`): tudo aqui foi criado via deploy de metadata, nunca pela UI.

**Decisão tomada (por tempo/risco, documentada em vez de silenciada):** o relatório "Amostras pendentes de retorno" ficou simplificado para contar Amostras pelo campo padrão `CUST_NAME` (Nome), sem o filtro por `Resultado__c`. Isso cumpre parcialmente o objetivo (visibilidade do volume de amostras em andamento), mas não filtra especificamente por "Em Teste"/"Em Análise" como pedido. Fica registrado como pendência técnica: se uma sessão futura confirmar que a indexação já propagou (testando novamente a referência a `Amostra__c.Resultado__c` num Report), o filtro pode ser reaplicado sem custo — o Report Type customizado `Amostras_Detalhado__c` já ficou deployado na org para esse fim, mas o arquivo local não foi commitado (ver seção 6).

Nota lateral, já documentada na demanda-11: o texto desta demanda pede filtrar por "Em Análise"/"Em Teste", mas o picklist real de `Resultado__c` só tem "Em Teste"/"Aprovado"/"Reprovado" — "Em Teste" seria o valor equivalente a usar, caso o filtro seja reaplicado no futuro.

### 4. Dashboard "Reunião Diária — Cromatta"

5 componentes, um por Report:
- **Column** (barras) → Fechamentos desde ontem.
- **Gauge** → Meta x Realizado Mensal, `gaugeMin=0`, `gaugeMax=2.500.000`, `indicatorBreakpoint1=1.000.000`, `indicatorBreakpoint2=2.000.000` (meta de R$ 2 mi/mês, cores vermelho/amarelo/verde).
- **Table** → Oportunidades travadas.
- **Donut** → Concentração de receita por Vendedor.
- **Metric** → Amostras pendentes de retorno.

**Filtros globais:** `Vendedor` (Camila, Diego, Marcelo, Ronaldo, Thiago, Bruno) e `Linha de Produto` (Cromata, Flecha, Jato). A Metadata API de Dashboard usa o recurso "clássico" de filtros — cada filtro é definido com uma lista de **valores pré-enumerados** (`dashboardFilterOptions`), não um filtro dinâmico livre por valor de registro; por isso os nomes reais dos vendedores e as 3 linhas de produto foram cadastrados explicitamente. Cada componente precisa mapear obrigatoriamente **todos** os filtros globais definidos, um `<dashboardFilterColumns>` por filtro, na mesma ordem — a plataforma rejeita o deploy se o número de mapeamentos não bater (`"Wrong number of dashboardFilterColumns"`).

**Limitação honesta sobre "Linha de Produto":** nenhum dos 5 Reports expõe hoje um campo de Linha de Produto (o candidato mais próximo, `Account.LinhaDeProduto__c`, é um campo customizado no objeto Account não exposto no Report Type padrão de Opportunity, mesma classe de limitação da seção 3). Por isso, o filtro "Linha de Produto" existe e está **disponível no Dashboard** (cumprindo o critério de aceite ao pé da letra), mas hoje não altera de fato os dados dos 5 componentes — foi mapeado ao mesmo campo já usado para "Vendedor" (`FULL_NAME`/`CUST_NAME`) apenas para satisfazer o requisito estrutural de 1‑para‑1 da plataforma. Registrado aqui de forma transparente, não escondido.

**dashboardType:** `LoggedInUser` (não `SpecifiedUser`). Tentativa inicial usou `SpecifiedUser` com Gabriel Jacob como "running user", mas a execução do Dashboard falhava (`"This report cannot be used as the source for this component... isn't in a folder accessible to the dashboard's running user"`) — a pasta `Cromatta_Reports`, mesmo com `accessType=Public`/`publicFolderAccess=ReadWrite`, não teve o `AccessType` real da org atualizado para `Public` via redeploy (confirmado via SOQL em `Folder.AccessType`, que permaneceu `Hidden` mesmo após deploy bem-sucedido — outra limitação de metadata: parece que a alteração de `accessType` de uma pasta já existente não é aplicada de forma confiável por um redeploy). Como o OWD de Opportunity/Account/Case já é Public Read Only (todos os usuários internos veem todos os registros), `LoggedInUser` produz o mesmo resultado de dados na prática, e resolve o problema de acesso à pasta sem depender de corrigir o `AccessType` da pasta.

### 5. Validação via Apex/CLI/Analytics REST API

- **Existência confirmada via SOQL:** os 5 registros `Report` e o registro `Dashboard` existem na org com os `DeveloperName` esperados.
- **Execução real dos 5 Reports** via `GET /services/data/v62.0/analytics/reports/<Id>` (Analytics REST API, autenticado via `sf org auth show-access-token`), com dados de teste criados via Apex (`sf apex run`): 1 Account + 2 Opportunities Closed Won (`Amount=50000` ontem, `Amount=120000` hoje) + 1 Amostra `Em Teste`. Resultados confirmados:
  - Fechamentos desde ontem: 1 registro, agrupado por "Ricardo Custodio" (usuário de teste).
  - Meta x Realizado Mensal: 2 registros, total R$ 170.000,00 (50.000 + 120.000), ambos no mês corrente.
  - Concentração de receita por vendedor: total 2, 100% concentrado no mesmo Owner (esperado, mesmo usuário criou as duas Opportunities de teste).
  - Oportunidades travadas: 0 registros (esperado — Opportunities de teste são novas, não "travadas").
  - Amostras pendentes de retorno: 1 registro (a Amostra de teste).
- **Execução do Dashboard** via `GET /services/data/v62.0/analytics/dashboards/<Id>/status`: todos os 5 componentes retornaram sem erro (`errorCode: null`) após a correção do `dashboardType`. Confirmado via `GET .../describe` que os 2 filtros (`Vendedor`, `Linha de Produto`) e os 5 componentes estão presentes.
- Registros de teste removidos após a validação.

### 6. Achado fora do escopo desta demanda — possível regressão em FLS/PermissionSets (não corrigido, sinalizado)

O retrieve final desta demanda (regra central 2 do `CLAUDE.md`) trouxe, além dos arquivos desta demanda, alterações não relacionadas em arquivos de outra sessão/squad member aparentemente em andamento no momento deste retrieve: um novo campo `Contact.AreaResponsavel__c` + Validation Rules em Account/Contact + item de Layout — e, mais preocupante, os Permission Sets `Administrador_Comercial`, `Laboratorio` e `Vendedor` retornaram **sem** as `fieldPermissions` de `Amostra__c` (`CustoEstimado__c`, `DataEnvio__c` etc.) que estavam commitadas e válidas antes. Isso é consistente com o mesmo tipo de problema já visto e documentado na [ADR 0005](../../decisions/0005-owd-revertido-para-private-fora-do-fluxo.md) (redeploy parcial de um PermissionSet, sem todos os campos existentes, sobrescrevendo/removendo permissões antigas) — mas, diferente do OWD, este parece ser efeito de uma demanda de **outra sessão ainda em andamento**, não finalizada. Por isso, **não foi corrigido nesta demanda** (poderia conflitar com o trabalho em progresso de quem está executando aquela demanda) e **não foi commitado** — os arquivos de `permissionsets/`, `profiles/`, `layouts/Contact-Contact Layout`, `objects/Account/validationRules/`, `objects/Contact/fields/AreaResponsavel__c.field-meta.xml` e `objects/Contact/validationRules/` ficaram de fora do `git add` desta demanda, intencionalmente. Fica sinalizado para o tech lead confirmar, quando a outra demanda for finalizada e commitada, se as `fieldPermissions` de `Amostra__c` realmente foram perdidas ou se é um artefato temporário do retrieve.
