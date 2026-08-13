---
title: "Decisões arquiteturais — quimicahackaton"
category: "decisions"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# Decisões arquiteturais (ADRs)

Cada decisão relevante que não pode ser revertida sem custo, ou que um agente executor precisa conhecer para não refazer a mesma pergunta, vira um arquivo aqui: `NNNN-titulo-curto.md`.

## Índice

| ADR | Decisão | Status |
| --- | --- | --- |
| [0001](0001-modelo-conta-b2b-b2c-sem-person-accounts.md) | Modelo de Account B2B/B2C via Record Type, sem Person Accounts | **Substituída pela 0003** |
| [0002](0002-sem-integracao-erp-precificacao-v1.md) | Sem integração de ERP nem motor de precificação automático no v1 | Ativa |
| [0003](0003-account-sem-record-type-tipopessoa.md) | Account como objeto único com TipoPessoa__c, sem Record Type (segue o BRD oficial) | Ativa |
| [0004](0004-reconciliacao-permissionsets-fora-do-fluxo.md) | Correção: Permission Sets da demanda 02 foram criados via Claude, não fora do fluxo | Retificada |
