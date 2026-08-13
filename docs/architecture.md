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

> Baseada nos requisitos reais levantados com o cliente (Cromatta Química) — ver [business-scenario.md](business-scenario.md), a fonte completa em [transcricao.md](transcricao.md), e o **BRD oficial aprovado** em [entregaveis/BRD_Cromatta_Quimica_Squad02_final.pdf](entregaveis/BRD_Cromatta_Quimica_Squad02_final.pdf) — o BRD prevalece onde houver divergência com versões anteriores deste documento (ver [ADR 0003](decisions/0003-account-sem-record-type-tipopessoa.md)).

## Regra de implementação (herdada das regras do hackathon)

**Tudo via Claude/IA, como padrão** (declarativo via Flow/metadata deployado, nunca clique-clique na org). Essa é a regra de maior peso na avaliação do hackathon (25% da nota).

**Exceção explícita:** o que não for possível fazer via Claude pode ser feito direto na org — a exceção é sobre viabilidade técnica, não preferência. Registrar sempre o que foi feito manualmente e por quê (nota ou ADR), nunca silenciosamente.

## Clouds envolvidas

- **Sales Cloud** — Lead, Opportunity, Product2/PriceBook2.
- **Service Cloud** — Case, Queue (fila do laboratório).

Knowledge, Omni-Channel e Entitlements **não são requisitos do cliente** — não usar a menos que surja necessidade nova (não inventar escopo).

## Modelo de dados

```text
Account (TipoPessoa__c: PF | PJ — sem Record Type, ver ADR 0003)
  │
  ├── Contact (1:N, tanto para PF quanto PJ — ver BRD 3.3)
  │
  ├── Lead
  │     campos: OrigemCadastro__c/LeadSource (Internet | Feira do Setor |
  │             Indicação | Prospecção Ativa), LinhaDeInteresse__c
  │             (Cromata | Flexa | Jato), CNPJ_CPF__c
  │     → convertido em Account + Contact + Opportunity
  │
  ├── Opportunity (RecordType: Caminho A — Produto Existente |
  │     Caminho B — Produto Novo — ver BRD 3.4.1 para os estágios de cada)
  │     campos próprios:
  │       - LinhaDeProduto__c (Cromata | Flexa | Jato)
  │       - IndicadorDeUrgencia__c (ex.: problema com fornecedor atual)
  │       - MotivoDaPerda__c (picklist, obrigatório ao marcar Closed Lost)
  │       - PossuiContratoRecorrente__c + VolumeMinimoMensal__c
  │       - Amount/PrecoVendido__c (preenchido manualmente pelo comercial —
  │           sem cálculo automático via câmbio no v1, ver ADR 0002)
  │     ├── OpportunityLineItem → Product2 / PricebookEntry
  │     └── Amostra__c (objeto customizado, **Lookup** em Opportunity e em
  │           Product2 — não Master-Detail; ver BRD 3.5.2) — peso/volume
  │           enviado, data de envio, nº da tentativa (auto-incremento),
  │           resultado (Em Teste | Aprovada | Reprovada), custo estimado
  │
  └── Case (RecordType: Envio e Teste de Amostra | Pós-Venda/Reclamação de
        Qualidade de Lote — ver BRD 3.7)
        - Envio e Teste de Amostra: criado quando uma amostra é registrada
          como Reprovada; roteado para Queue "Laboratório" (Sérgio e André)
        - Pós-Venda: reclamação/qualidade em cliente recorrente já ativo
        campos:
          - AmostraId__c (Lookup em Amostra__c, quando aplicável)
          - CausaTecnicaDeReprovacao__c (picklist): incompatibilidade com
            substrato, incompatibilidade com a base do cliente, instabilidade
            do produto, entupimento de cabeçote, aspecto/aparência fora do
            esperado
          - MarcacaoDeVisitaTecnica__c (checkbox + data)
          - PrazoDeResposta__c: 10 dias úteis (amostra) | 5 dias (pós-venda)

Product2 (LinhaDeProduto__c: Cromata | Flexa | Jato) → PricebookEntry → Standard Price Book
```

Decisões que sustentam este modelo:
- Account como objeto único com `TipoPessoa__c`, sem Record Type — [ADR 0003](decisions/0003-account-sem-record-type-tipopessoa.md) (substitui a [ADR 0001](decisions/0001-modelo-conta-b2b-b2c-sem-person-accounts.md)).
- Sem integração de ERP nem motor de precificação automático no v1 — [ADR 0002](decisions/0002-sem-integracao-erp-precificacao-v1.md).
- Correção de registro sobre a origem dos Permission Sets (demanda 02, executada corretamente via Claude por Inaldo Junior) — [ADR 0004](decisions/0004-reconciliacao-permissionsets-fora-do-fluxo.md).

**Pontos reais em aberto (não relacionados ao engano corrigido na ADR 0004):**
- Record Type `Business_Account` existe na org, origem não identificada em nenhuma demanda registrada — órfão desde a ADR 0003, não usar em nova automação.
- `User.Linha_de_Produto__c` (já deployado, demanda 02) usa a grafia "Flecha/Cromata"; o BRD oficial usa "Flexa/Cromata" — precisa de uma demanda de correção do picklist antes de mais dados serem cadastrados.

## Segurança e acessos

Requisito do cliente: **vendedores veem todos os registros, mas só editam os próprios**; o dono da empresa vê e valida tudo.

- **OWD: Public Read Only** em Account, Opportunity, Case e Amostra__c — isso já entrega "lê tudo, edita só o próprio" nativamente (owner mantém edição), sem precisar de sharing rules extras. Amostra__c precisa de OWD próprio (não herda de ninguém, pois a relação com Opportunity é Lookup, não Master-Detail).
- **Permission Sets (nomenclatura do BRD, seção 2.2):**
  - **Vendedor** — Camila, Ronaldo, Marcelo, Diego, Bruno, Thiago. CRUD em Lead/Account/Opportunity/Case que possui, leitura nos demais, sem acesso a aprovação de preço. **Já existe na org** (ver ADR 0004).
  - **Laboratório / Químico** — Sérgio e André. Acesso à fila de Case "Laboratório", CRUD em Case, leitura em Opportunity/Account relacionados. **Já existe na org** (API name `Laboratorio`, ver ADR 0004).
  - **Administrador Comercial** — Gabriel Jacob (dono da empresa). Acesso total, aprovador do fluxo de preço/desconto, visão de todos os relatórios/dashboards. **Já existe na org** (demanda 02) — este nome substitui "Gestor", usado em versões anteriores deste documento antes do BRD existir.

Todos os 9 usuários (6 vendedores + 2 químicos + Gabriel Jacob) já estão cadastrados com o Permission Set correspondente atribuído (demanda 02). Queue "Laboratório" também já existe, com Sérgio e André como membros. Pendente do critério de aceite da demanda 02: teste de login real como Vendedor confirmando "lê tudo, edita só o próprio" na UI (manual, não é etapa de configuração via Claude).

## Automação — o que precisa existir (derivado dos requisitos)

Ordem de preferência sempre: 1) configuração declarativa → 2) Flow → 3) Approval Process → 4) Apex/LWC só se 1–3 forem comprovadamente insuficientes. Tudo via Claude/IA (ver regra no topo).

1. **Approval Process de preço/desconto** na Opportunity — aprovação sempre do Administrador Comercial (Gabriel Jacob), tanto no preço-base do produto quanto no desconto por volume da oportunidade (BRD 4.3).
2. **Validation Rule / Flow** exigindo `MotivoDaPerda__c` ao marcar Opportunity como Closed Lost.
3. **Record-Triggered Flow** (em `Amostra__c`): quando uma amostra registrada é marcada como Reprovada → cria Case (RecordType "Envio e Teste de Amostra"), atribuído à Queue "Laboratório", roteado ao químico da linha correspondente (BRD 3.5.1, 4.6).
4. **Status de carteira do cliente** (`StatusCarteira__c`): Ativo (compra nos últimos 60 dias) / Inativo (mais de 60 dias) — alimenta o relatório de clientes inativos (BRD 3.1.2, 4.2).
5. **Alerta de concentração de receita**: quando um vendedor ou cliente ultrapassa **40%** do volume total de vendas da carteira, notificar o Administrador Comercial (Chatter/e-mail) — limite oficial confirmado no BRD 4.1, não é mais estimativa.
6. **SLA de resposta por tipo de Case**: cobrança automática ao cliente em 10 dias úteis sem retorno de teste de amostra; prazo de resposta de 5 dias para casos de pós-venda (BRD 4.4).
7. **Dashboards de gestão comercial** (BRD Parte 6):
   - Diário: o que cada vendedor fechou desde ontem, oportunidades travadas, amostras pendentes de retorno.
   - Mensal: faturamento vs. meta, ranking por vendedor e por linha de produto, status dos clientes mais estratégicos.
   - Metas por vendedor, nas 3 camadas (resultado / comercial / atividade — BRD 4.7).

Priorização entre caso comercial e caso técnico simultâneos: **A CONFIRMAR** com o cliente — premissa assumida no BRD é ordem de chegada combinada ao Indicador de Urgência (BRD 4.6), não uma regra definitiva.

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
