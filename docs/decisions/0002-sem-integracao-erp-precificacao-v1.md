---
title: "ADR 0002 — Sem integração de ERP nem motor de precificação automático no v1"
category: "decision"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# ADR 0002 — Sem integração de ERP nem motor de precificação automático no v1

## Contexto

O preço final dos produtos da Cromatta Química é volátil: depende do custo de matéria-prima importada e do câmbio (USD/BRL), que mudam com frequência. O cliente tem um ERP com dados de custo, mas hoje **não olha nem analisa** esses dados — o ajuste de preço é feito manualmente pelo próprio dono. Ver [business-scenario.md](../business-scenario.md).

Na reunião de levantamento de requisitos, ao ser perguntado diretamente se o Salesforce deveria calcular o preço automaticamente a partir da variação do dólar (sugestão de um objeto relacionado guardando a cotação), o cliente respondeu explicitamente que **isso não é necessário no v1** — apenas um fluxo comercial até a definição do preço, que continua sendo feita fora do sistema.

## Problema

Construir uma integração com o ERP (para trazer custo de produção) e/ou um motor automático de precificação vinculado a cotação de câmbio, dentro de um hackathon de 1 dia, consumiria tempo desproporcional ao valor demonstrado — e não foi pedido pelo cliente para o v1.

## Decisão

**Não implementar integração com ERP nem motor de precificação automático no v1.**

- O preço final de venda é um **campo simples na Opportunity**, preenchido manualmente pelo time comercial (o cálculo de custo/margem continua acontecendo fora do Salesforce).
- Se for necessário ter custo de produto no Salesforce para outro fim (ex.: exibir referência ao vendedor), o caminho aceito é **upload manual de planilha**, nunca uma integração viva com o ERP.
- Aprovação de preço/desconto (sempre do dono da empresa) é modelada como Approval Process normal, independente de qualquer cálculo automático de custo.

## Consequências

- Nenhum Named Credential, Apex de integração ou Platform Event para o ERP deve ser criado neste hackathon — se um agente executor identificar essa necessidade, é escopo novo e exige reabrir esta decisão, não implementar por conta própria.
- A oportunidade de "V2" (motor de precificação automático por câmbio/matéria-prima, com objeto de cotação diária, como sugerido por um dos devs na reunião) fica registrada aqui para não ser esquecida, mas **não deve ser construída neste hackathon**.
- Reajustes de preço no catálogo de produtos continuam sendo um processo manual do dono da empresa.

## Alternativas descartadas

| Alternativa | Por que foi descartada |
| --- | --- |
| Integração em tempo real com o ERP para custo | Não solicitada pelo cliente para o v1; complexidade/risco incompatível com 1 dia de hackathon |
| Objeto de cotação de câmbio + fórmula de preço automática | Ideia validada como "V2" pelo próprio cliente durante a reunião, não como requisito atual |
