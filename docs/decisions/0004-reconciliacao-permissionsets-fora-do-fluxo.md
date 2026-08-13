---
title: "ADR 0004 — Correção: Permission Sets da demanda 02 foram criados via Claude, não fora do fluxo"
category: "decision"
status: "retificada"
version: "2.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# ADR 0004 — Correção: Permission Sets da demanda 02 foram criados via Claude, não fora do fluxo

## Contexto

A v1.0 desta ADR registrou, incorretamente, que os Permission Sets `Vendedor` e `Laboratorio` (encontrados na org durante a reanálise arquitetural da demanda 01) haviam sido criados **fora do fluxo Claude**, por um mentor do hackathon (Ricardo Custodio), sem registro em `evidencias/log.md`.

**Isso estava errado.** A causa raiz: a sessão que fez essa reanálise não tinha rodado `git pull` antes de investigar, então não via o histórico real do repositório — só o estado da org via MCP/SOQL, que mostra `CreatedBy.Name = "Ricardo Custodio"` nos registros de `PermissionSet`. Esse nome é o titular do usuário administrador padrão desta org de hackathon (`hackaton2@ddgroup.com.br`) — reflete a identidade do usuário Salesforce usado na sessão, não necessariamente quem operou o teclado.

Ao rodar `git pull`, ficou evidente que **Inaldo Junior** (Dev responsável pelo uso do Claude, conforme o BRD oficial) já havia executado a demanda 02 de forma completa e correta:

- `demanda.md` preenchido e arquivado em `evidencias/demandas/demanda-02.md`.
- `evidencias/log.md` atualizado (entrada 02) com resumo do que foi feito, desvios registrados e hash do commit.
- Metadata deployada via `sf project deploy start` (Permission Sets `Administrador_Comercial`, `Vendedor`, `Laboratorio`; OWD Public Read Only; campo `User.Linha_de_Produto__c`; Queue `Laboratório`; 9 usuários com `PermissionSetAssignment`).
- Retrieve real da org feito antes do push (regra central 2 do `CLAUDE.md`) e validação via SOQL/Tooling API (regra central 4), não só via CLI.

## Decisão

**Retificar esta ADR.** Não há reconciliação de trabalho "fora do fluxo" a fazer — a demanda 02 seguiu o processo corretamente. Nenhuma ação de commit/push adicional é necessária para os três Permission Sets.

O que permanece como pendência real, identificada durante essa mesma investigação (não relacionada ao engano acima):

1. **Origem do Record Type `Business_Account` em Account** — existe na org (confirmado via SOQL), mas não é mencionado em `demanda-01.md` nem em `demanda-02.md`. Origem não identificada. Como a [ADR 0003](0003-account-sem-record-type-tipopessoa.md) decidiu não usar Record Type para esse propósito, este Record Type fica **órfão** — não usar em nova automação, remoção fica para decisão futura (não é bloqueante).
2. **Divergência de grafia nas linhas de produto:** a demanda 02 usou "Flecha"/"Cromata" (grafia de `business-scenario.md` no momento da execução); o BRD oficial usa "Flexa"/"Cromata". O picklist `User.Linha_de_Produto__c`, já deployado, tem os valores com a grafia antiga. Precisa de uma demanda de correção (rename de valor de picklist ou novo valor + migração) antes de mais dados serem cadastrados com a grafia divergente.

## Consequências

- Lição de processo: **antes de investigar divergência entre org e repositório, sempre `git pull` primeiro** — o estado real do Git pode explicar o que a org sozinha não explica. Adicionar isso como passo explícito no roteiro de `/executar-demanda` e no `salesforce-preflight-check`.
- `evidencias/log.md` (entrada 03) documenta esta correção, para que a entrada errada original não fique como registro definitivo.
- `architecture.md` deve refletir que `Administrador_Comercial` e a Queue "Laboratório" **já existem**, não são mais pendências de implementação.

## Alternativas descartadas

| Alternativa | Por que foi descartada |
| --- | --- |
| Manter a v1.0 desta ADR sem correção | Registraria permanentemente uma acusação incorreta sobre o trabalho de um colega de squad |
| Apagar a v1.0 sem deixar rastro da correção | Esconderia o erro em vez de aprender com ele — contra o espírito de transparência do projeto |
