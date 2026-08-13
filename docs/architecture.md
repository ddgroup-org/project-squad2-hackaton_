---
title: "Arquitetura — quimicahackaton"
category: "architecture"
status: "active"
version: "2.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
source_of_truth: true
---

# Arquitetura

> Baseada nos requisitos reais levantados com o cliente (Cromatta Química) — ver [business-scenario.md](business-scenario.md) e a fonte completa em [transcricao.md](transcricao.md).

## Regra de implementação (herdada das regras do hackathon)

**Tudo via Claude/IA, como padrão** (declarativo via Flow/metadata deployado, nunca clique-clique na org). Essa é a regra de maior peso na avaliação do hackathon (25% da nota).

**Exceção explícita:** o que não for possível fazer via Claude pode ser feito direto na org — a exceção é sobre viabilidade técnica, não preferência. Registrar sempre o que foi feito manualmente e por quê (nota ou ADR), nunca silenciosamente.

## Clouds envolvidas

- **Sales Cloud** — Lead, Opportunity, Product2/PriceBook2.
- **Service Cloud** — Case, Queue (fila do laboratório).

Knowledge, Omni-Channel e Entitlements **não são requisitos do cliente** — não usar a menos que surja necessidade nova (não inventar escopo).

## Modelo de dados

```text
Account (Record Type: Business Account [PJ] | Individual Customer [PF])
  │                                            — ver ADR 0001
  ├── Contact (1:N em Business Account · 1:1 em Individual Customer)
  │
  ├── Lead
  │     campos: origem (feira | indicação | prospecção ativa/porta a porta | internet),
  │             linha de interesse (Cromata | Flecha | Jato)
  │     → convertido em Account + Contact + Opportunity
  │
  ├── Opportunity (Record Type: Produto Existente | Produto Novo/Em Desenvolvimento)
  │     campos próprios:
  │       - Linha de Produto (Cromata | Flecha | Jato)
  │       - Indicador de urgência (ex.: problema com fornecedor atual)
  │       - Motivo de perda (picklist, obrigatório ao marcar Closed Lost)
  │       - Compromisso de volume recorrente (checkbox + volume mínimo mensal)
  │       - Valor final de venda (preenchido manualmente pelo comercial — sem cálculo automático via câmbio no v1)
  │     ├── OpportunityLineItem → Product2 / PricebookEntry
  │     └── Amostra__c (objeto customizado, Master-Detail em Opportunity,
  │           Lookup em Product2) — produto, quantidade, data de envio,
  │           resultado, nº da tentativa, custo estimado — decisão fechada
  │           no Solution Design (entregaveis/02_Solution_Design_*.pdf)
  │
  └── Case (Record Type: Amostra/Teste | Pós-venda)
        - Amostra/Teste: criado quando uma amostra é reprovada; roteado para
          Queue "Laboratório", atribuído ao químico responsável pela linha
        - Pós-venda: reclamação/qualidade em cliente recorrente já ativo
        campos:
          - Causa técnica de reprovação (picklist): incompatibilidade com
            substrato, incompatibilidade com a base do cliente, instabilidade
            do produto, entupimento de cabeçote, aspecto/aparência fora do
            esperado, outra
          - Histórico de tentativas (contador ou relação a registros de amostra)
          - Visita técnica agendada (checkbox + data)

Product2 (Linha: Cromata | Flecha | Jato) → PricebookEntry → Standard Price Book
```

Decisões que sustentam este modelo:
- Contas B2B/B2C via Record Type, sem Person Accounts — [ADR 0001](decisions/0001-modelo-conta-b2b-b2c-sem-person-accounts.md).
- Sem integração de ERP nem motor de precificação automático no v1 — [ADR 0002](decisions/0002-sem-integracao-erp-precificacao-v1.md).

## Segurança e acessos

Requisito do cliente: **vendedores veem todos os registros, mas só editam os próprios**; o dono da empresa vê e valida tudo.

- **OWD: Public Read Only** em Account, Opportunity e Case — isso já entrega "lê tudo, edita só o próprio" nativamente (owner mantém edição), sem precisar de sharing rules extras.
- **Permission Sets:**
  - **Vendedor** — CRUD em Lead/Account/Opportunity/Case que possui, leitura nos demais, sem acesso a aprovação de preço.
  - **Químico/Laboratório** — acesso à fila de Case "Laboratório", CRUD em Case, leitura em Opportunity/Account relacionados.
  - **Gestor** (dono da empresa) — acesso total, aprovador do fluxo de preço/desconto, visão de todos os relatórios/dashboards.

## Automação — o que precisa existir (derivado dos requisitos)

Ordem de preferência sempre: 1) configuração declarativa → 2) Flow → 3) Approval Process → 4) Apex/LWC só se 1–3 forem comprovadamente insuficientes. Tudo via Claude/IA (ver regra no topo).

1. **Approval Process de preço/desconto** na Opportunity — aprovação sempre do Gestor, tanto no preço-base do produto quanto no desconto por volume da oportunidade.
2. **Validation Rule / Flow** exigindo Motivo de Perda ao marcar Opportunity como Closed Lost.
3. **Record-Triggered Flow** (em `Amostra__c`): quando uma amostra registrada é marcada como reprovada → cria Case (Record Type Amostra/Teste), atribuído à Queue Laboratório, roteado ao químico da linha correspondente; se já for a 3ª+ tentativa, sinalizar (ex.: campo ou flag de atenção).
4. **Assignment/roteamento** de Case por linha de produto → químico responsável.
5. **Relatório/Dashboard de clientes inativos** — sem pedido há 60+ dias.
6. **Alerta de concentração de risco** — quando um vendedor (ou cliente) concentra uma fatia desproporcional da receita (ex.: >50%), notificar o Gestor. Caminho mais simples: Flow agendado (scheduled) que calcula a % por vendedor/período e dispara Email Alert quando o limite é ultrapassado — validar esse limite com o cliente antes de fixar um número (hoje só sabemos que 60% já é tratado como alarmante).
7. **Dashboards de gestão comercial:**
   - Diário: o que cada vendedor fechou desde o dia anterior, oportunidades travadas, prioridades do dia.
   - Mensal: faturamento vs. meta, ranking por vendedor e por linha de produto, status dos clientes mais estratégicos, meta do mês seguinte.

## Rastreabilidade — como o tech lead revisa sem acesso à org

```text
Repositório Git já existe (este mesmo repositório, force-app/ + manifest/)
        ↓
Antes de cada push: sf project retrieve start (nunca commitar às cegas)
        ↓
commit → push
        ↓
Tech lead revisa via git log / git diff / Pull Request — nunca logando na org
```

Sem esse fluxo, o hackathon fica sem nenhum ponto de verificação para o tech lead — por isso retrieve-antes-de-push é regra em toda a execução, não apenas na primeira etapa.
