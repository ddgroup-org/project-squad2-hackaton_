---
title: "ADR 0004 — Reconciliação de metadata criada fora do fluxo Claude/executar-demanda"
category: "decision"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# ADR 0004 — Reconciliação de metadata criada fora do fluxo Claude/`/executar-demanda`

## Contexto

A regra central 1 deste projeto (`CLAUDE.md`) é: tudo via Claude/IA, exceção só por inviabilidade técnica, sempre registrada. A reanálise arquitetural da demanda 01 (agente `salesforce-architect`, ver [evidencias/demandas/reanalise-demanda-01.md](../evidencias/demandas/reanalise-demanda-01.md)) encontrou, consultando a org `cromatta-hackathon` diretamente:

- Dois Permission Sets, `Vendedor` e `Laboratorio`, já existentes na org, criados em 13/08/2026 (14:28 e 14:33 UTC), com descrição interna citando "demanda-02 e architecture.md".
- `CreatedBy.Name = Ricardo Custodio` — um mentor do hackathon (citado na transcrição de kickoff, `docs/transcricao.md`), **não** um membro do Squad 02 listado no BRD oficial (Barbara Lopes, Paulo Carvalho, Inaldo Junior, Gabriel Moraes).
- Também confirmado que Person Accounts foi habilitado na org (ver [ADR 0003](0003-account-sem-record-type-tipopessoa.md)) — mudança irreversível, também fora do fluxo Claude.
- Nenhuma dessas alterações tinha `evidencias/log.md` correspondente, nem metadata retrieved para `force-app/`.

## Problema

Essas alterações contam para o critério de 25% da nota (uso do Claude/IA) apenas se puderem ser justificadas como exceção registrada — caso contrário, representam configuração manual não declarada, o que a regra central 1 trata como falha grave de processo, não como detalhe menor.

## Decisão

**Reconciliar, não descartar.** O conteúdo dos Permission Sets é tecnicamente compatível com o Security Model especificado em `architecture.md` (CRUD correto, `ViewAllRecords`/`ModifyAllRecords` desligados) — descartar e recriar do zero destruiria trabalho correto sem ganho real, numa janela de tempo curta de hackathon.

Ações tomadas:

1. Retrieve direcionado de `PermissionSet:Vendedor` e `PermissionSet:Laboratorio` para `force-app/main/default/permissionsets/`, trazendo a metadata da org para o repositório.
2. Registro retroativo em `evidencias/log.md` (linha "02"), explicando a origem (mentor, fora do fluxo padrão) — nunca silenciosamente.
3. Habilitação de Person Accounts: registrada como fato consumado e irreversível (ver ADR 0003) — não há reconciliação possível além de documentar e decidir não usar a feature.

## Consequências

- A partir de agora, qualquer nova metadata encontrada na org sem correspondência em `evidencias/log.md` deve passar por este mesmo processo: reconciliar via retrieve + registro retroativo, nunca ignorar nem descartar sem necessidade.
- Falta ainda: Permission Set do terceiro perfil (`Administrador Comercial`, conforme nomenclatura do BRD — substitui o nome "Gestor" usado em `architecture.md` antes do BRD existir), Queue "Laboratório", e atribuição de usuários aos Permission Sets já criados (`PermissionSetAssignment` = 0 registros no momento da reanálise).
- `architecture.md` deve ser atualizado para usar a nomenclatura do BRD (`Administrador Comercial`) em vez de `Gestor`.

## Alternativas descartadas

| Alternativa | Por que foi descartada |
| --- | --- |
| Descartar e recriar via Claude do zero | Destruiria trabalho tecnicamente correto; não há evidência de que o conteúdo esteja errado, só de que o processo de registro falhou |
| Ignorar silenciosamente | Viola a regra central 1 (registrar sempre exceções) e deixaria o tech lead sem visibilidade real do estado da org via Git |
