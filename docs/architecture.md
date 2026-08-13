---
title: "Arquitetura — quimicahackaton"
category: "architecture"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Paulo Carvalho"
applies_to:
  - quimicahackaton
source_of_truth: true
---

# Arquitetura

## Clouds envolvidas

- **Sales Cloud** — Lead, Opportunity, Product2/PriceBook2, Quote (se licença disponível).
- **Service Cloud** — Case, Queue/Omni-Channel (se licença disponível), Knowledge (se licença disponível), Entitlement (se licença disponível).

Licenças de Knowledge, Omni-Channel e Entitlements **não são garantidas** em todo Developer Edition/Trailhead Playground — cada prompt que depende delas traz um caminho alternativo declarativo mais simples, para não bloquear o hackathon por licenciamento.

## Modelo de dados — visão geral

```text
Account (Record Type: Business Account | Individual Customer)
  │
  ├── Contact (1:N em Business Account · 1:1 em Individual Customer)
  ├── Opportunity (Record Type: B2B Sale | B2C Sale)
  │      └── OpportunityLineItem → Product2 / PricebookEntry
  └── Case (Record Type: Suporte Técnico B2B | Atendimento ao Consumidor B2C)

Product2 (Grupo: Insumo a granel | Consumo) → PricebookEntry → Standard Price Book
```

Decisão de usar Record Type em Account em vez de Person Accounts: ver [ADR 0001](decisions/0001-modelo-conta-b2b-b2c-sem-person-accounts.md).

## Segurança — nível de ambição para 1 dia

Dado o prazo, o modelo de segurança **não** tenta separar visibilidade de dados entre times B2B e B2C (isso exigiria sharing rules, papéis de fila e OWD restritivo, consumindo tempo desproporcional ao valor demonstrado). Assume-se:

- OWD padrão (ou Public Read/Write) para os objetos envolvidos.
- Dois Permission Sets simples: "Vendedor" e "Atendimento", cada um com acesso a Objects/Fields relevantes ao seu processo — o suficiente para a demo mostrar perfis diferentes, sem construir um modelo de sharing completo.

Se o hackathon exigir isolamento real de dados entre B2B e B2C, isso é uma decisão arquitetural nova, fora do escopo assumido aqui — registrar como ADR à parte antes de implementar.

## Automação — critério de escolha

Ordem de preferência, do mais simples ao mais custoso, seguida em todos os prompts:

```text
1. Configuração declarativa (campo, record type, layout, list view)
2. Flow (Screen Flow, Record-Triggered Flow)
3. Approval Process
4. Apex/LWC — apenas quando 1–3 forem comprovadamente insuficientes
```

## Rastreabilidade — como o tech lead revisa sem acesso à org

```text
Dev executor cria repositório Git (Prompt 00)
        ↓
Cada prompt concluído → retrieve da metadata alterada → commit → push
        ↓
Paulo revisa via git log / git diff / Pull Request — nunca logando na org
```

Sem esse fluxo, o hackathon fica sem nenhum ponto de verificação para o tech lead — por isso essa exigência aparece em todo prompt de `docs/demands/`, não apenas no primeiro.
