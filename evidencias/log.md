# Log de execução de demandas

Uma linha por demanda executada via `/executar-demanda`. Ver [README.md](README.md) e [docs/como-executar-demandas.md](../docs/como-executar-demandas.md).

| # | Data | Demanda (resumo) | O que foi feito | Commit |
| --- | --- | --- | --- | --- |
| 02 | 2026-08-13 | Setup da org Salesforce: Company Profile "Cromatta Química", perfis/Permission Sets (Administrador Comercial, Vendedor, Laboratório), OWD Public Read Only em Account/Opportunity/Case, campo Linha de Produto no User, fila Laboratório, 9 usuários cadastrados (Jacob, 6 vendedores, Sérgio e André). | Via CLI `sf`: Organization.Name atualizado; deploy de metadata (CustomField `User.Linha_de_Produto__c`, `sharingModel=Read` em Account/Opportunity/Case, 3 PermissionSets, Queue `Laboratório`, FLS no profile Admin); 9 `User` criados com `PermissionSetAssignment` correspondente. Validado via SOQL/Tooling API (não só CLI). Linhas de produto grafadas conforme `business-scenario.md` (Cromata/Flecha/Jato) — ver nota de desvio em `evidencias/demandas/demanda-02.md`. Pendente: teste de login real como Vendedor (manual, Gabriel Moraes/Paulo Carvalho). | `8f90a62` |
