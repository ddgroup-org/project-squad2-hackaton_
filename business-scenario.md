---
title: "Cenário de negócio — quimicahackaton"
category: "context"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Paulo Carvalho"
applies_to:
  - quimicahackaton
source_of_truth: true
---

# Cenário de negócio

> **Este cenário é fictício e foi assumido por ausência de um desafio de negócio detalhado.** Se o hackathon já define uma empresa, produto ou desafio real, substituir todo o conteúdo abaixo antes de enviar qualquer prompt em `docs/demands/` — eles citam estes nomes e estas regras diretamente.

## Empresa fictícia

**Quimtech Distribuidora Química Ltda.** — distribuidora brasileira de produtos químicos com dois canais de venda distintos, atendidos por um único time comercial e um único time de suporte.

## Canal B2B — empresas

- **Clientes:** fábricas, laboratórios, indústrias de pequeno e médio porte que compram insumos químicos a granel (solventes industriais, ácidos, matérias-primas para formulação).
- **Ciclo de venda:** técnico, mais longo, envolve cotação, ficha técnica/segurança do produto, negociação de volume e prazo, aprovação de desconto acima de um limite.
- **Pós-venda:** suporte técnico — dúvidas de manuseio, ficha de segurança (FISPQ/SDS), incidentes de uso, relacionamento contínuo.
- **Papel comercial:** vendedor técnico (account executive) com carteira de contas.

## Canal B2C — consumidores finais

- **Clientes:** pessoas físicas compradoras de produtos de limpeza doméstica, produtos para piscina e produtos para jardim.
- **Ciclo de venda:** simples, autoatendimento ou venda rápida, sem negociação técnica.
- **Pós-venda:** atendimento ao consumidor — dúvidas de uso, reclamações, trocas.
- **Papel comercial:** atendente/vendedor de varejo.

## Por que este cenário serve ao hackathon

Ele justifica, de forma simples e demonstrável em 1 dia:

- Dois **Record Types de Account** (Business Account / Individual Customer) em vez de Person Accounts — ver [ADR 0001](decisions/0001-modelo-conta-b2b-b2c-sem-person-accounts.md).
- Dois **Record Types de Opportunity** e de **Case**, com processos diferentes por segmento.
- Um catálogo de produto simples com dois grupos: insumos a granel (B2B) e produtos de consumo (B2C).
- Regras de negócio concretas o bastante para dar automação (Flow) e relatório (Dashboard) sem precisar de mais contexto do que este documento fornece.

## Dados de exemplo sugeridos (usar como base, ajustável)

**Contas B2B (Business Account):**

| Nome | Segmento | Setor |
| --- | --- | --- |
| Indústria Fortex Ltda. | B2B | Metalurgia |
| Laboratório Vitallab | B2B | Farmacêutico |
| Confecções Rio Têxtil | B2B | Têxtil |

**Contas B2C (Individual Customer):**

| Nome | Segmento |
| --- | --- |
| Mariana Souza | B2C |
| Carlos Andrade | B2C |
| Beatriz Lima | B2C |

**Produtos:**

| Produto | Grupo | Canal |
| --- | --- | --- |
| Solvente Industrial X-40 | Insumo a granel | B2B |
| Ácido Clorídrico Técnico | Insumo a granel | B2B |
| Cloro Granulado para Piscina | Consumo | B2C |
| Multiuso Concentrado Bio | Consumo | B2C |
| Fertilizante Líquido Jardim Verde | Consumo | B2C |

## Fora de escopo do cenário (por ora)

- Portal self-service (Experience Cloud) para B2B ou B2C — fora do prazo de 1 dia, a menos que sobre tempo depois do Prompt 06.
- Integração com e-commerce real ou ERP — tratada apenas como automação interna simulada, se necessário.
- Person Accounts — deliberadamente descartado, ver ADR 0001.
