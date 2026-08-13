# Log de execução de demandas

Uma linha por demanda executada via `/executar-demanda`. Ver [README.md](README.md) e [docs/como-executar-demandas.md](../docs/como-executar-demandas.md).

| # | Data | Demanda (resumo) | O que foi feito | Commit |
| --- | --- | --- | --- | --- |
| 01 | 2026-08-13 | Solution Design + Data Mapping da Cromatta Química — PDF corporativo (`02_Solution_Design_Cromatta_Quimica_Squad02.pdf`), com logo e cores da marca (`imgs/`) | Gerado via HTML+CSS/SVG renderizado a PDF por Chrome headless (`entregaveis/`). Conteúdo: diagrama de objetos, Data Mapping campo a campo, Security Model, automações previstas, uso do Claude por etapa. Validado via MCP (`run_soql_query` em `PermissionSet`/`EntityDefinition`) que a "Tarefa 02" (Security Model) e o objeto `Amostra__c` ainda não existem na org — documentado como design especificado, não implementado. Fechada a decisão pendente em `architecture.md`: `Amostra__c` é objeto customizado (Master-Detail em Opportunity). | d87e560 |
