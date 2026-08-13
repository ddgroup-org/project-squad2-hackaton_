---
title: "ADR 0001 — Modelo de Account B2B/B2C via Record Type, sem Person Accounts"
category: "decision"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# ADR 0001 — Modelo de Account B2B/B2C sem Person Accounts

## Contexto

O cenário do hackathon precisa distinguir clientes **B2B** (empresas) de clientes **B2C** (consumidores finais). A forma "nativa" da Salesforce para representar consumidores finais é **Person Accounts**.

## Problema

Habilitar Person Accounts:

- é uma mudança **irreversível** na org;
- em muitas orgs (incluindo Developer Edition e Trailhead Playground) exige abertura de caso com o Salesforce Support para habilitação, o que **não é viável dentro de um hackathon de 1 dia**;
- em Scratch Org é possível declarar via `scratch-org-definition` na criação — mas ainda assim adiciona complexidade e risco de bloqueio se a definição não for aceita a tempo.

## Decisão

**Não habilitar Person Accounts.** Usar dois Record Types em Account:

- **Business Account** — para clientes B2B, com Contacts relacionados normalmente (1:N).
- **Individual Customer** — para clientes B2C: um Account por pessoa física, com um único Contact relacionado, simulando o comportamento de Person Account sem depender do recurso.

## Consequências

- Relatórios e Flows tratam `Account.RecordType.DeveloperName` como o campo de segmentação primário, em vez de `Account.IsPersonAccount`.
- Criação de conta B2C exige criar Account + Contact (2 registros) em vez de 1 — aceitável para o volume de dados de demonstração de um hackathon.
- Caso a organização do hackathon já disponibilize uma org com Person Accounts habilitado **antes** da execução, esta decisão pode ser revista — mas não deve ser tomada como iniciativa do agente executor a meio da implementação; exige nova ADR.

## Alternativas descartadas

| Alternativa | Por que foi descartada |
| --- | --- |
| Person Accounts | irreversível, dependente de Salesforce Support, risco de não ser aprovado a tempo do hackathon |
| Contact sem Account (Private/sem Account) | perde a simetria de modelo com B2B, dificulta relatório único por "cliente" |
