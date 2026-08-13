---
title: "Cenário de negócio — quimicahackaton"
category: "context"
status: "active"
version: "2.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
source_of_truth: true
---

# Cenário de negócio

> **Este cenário é REAL**, levantado com o cliente simulado do hackathon (role-play) na reunião de kickoff. Fonte completa, com todo o contexto e citações originais: [docs/transcricao.md](docs/transcricao.md). Este documento aqui é o resumo estruturado para uso direto pelos prompts/execução — se algo parecer incompleto ou ambíguo, checar a transcrição antes de assumir.

## Empresa

**Cromatta Química** — indústria química no interior do Ceará, no mercado desde 1980. 80% fabricação própria; matéria-prima importada (China, EUA, Europa) — preço final volátil por câmbio (USD) e custo de matéria-prima.

## Linhas de produto

1. **Cromata** — tintas e vernizes, e dispersão de pigmento (matéria-prima para outros fabricantes de tinta).
2. **Flecha** — produtos de manutenção de couros e calçados (hidratação de couro, limpeza de calçado/tênis/veludo).
3. **Jato** — tintas para impressão a jato de tinta (impressoras).

Cada Lead/Oportunidade/Produto está associado a uma dessas três linhas.

## Clientes

- **PJ (pessoa jurídica):** maior parte do negócio — outras indústrias, fábricas, marcas que revendem (ex.: marca "Democrata" revende kits de limpeza de calçado da linha Flecha).
- **PF (pessoa física):** venda direta via site próprio — volume menor, mas existe.

Mapeamento para o modelo de Account já decidido: PJ → **Business Account**, PF → **Individual Customer** (ver [ADR 0001](decisions/0001-modelo-conta-b2b-b2c-sem-person-accounts.md)).

## Time comercial

6 vendedores, sem carteira fixa por padrão — o cliente fica com quem o trouxe (vendedor que prospectou), dentro da linha correspondente:

| Vendedor | Linha | Vínculo | Meta de novos clientes |
| --- | --- | --- | --- |
| Camila | Flecha | Interna | 2/mês |
| Ronaldo | Cromata | Representante externo (não CLT, atende outras empresas também) | 1/trimestre |
| Marcelo | Cromata | Interna, foco em abrir contas | 2/mês |
| Diego | Jato | Interna | 2/mês |
| Bruno | Jato | Interna | 2/mês |
| Thiago | Jato | Interna | 2/mês |

Dois químicos respondem pela fila do laboratório (nomes a confirmar — ver pendências).

## Dores atuais do negócio (ditas pelo cliente)

- Faturamento em queda recente.
- **Concentração de receita:** Camila (Flecha) responde por ~60% da receita — risco alto se ela saísse ou o cliente cancelasse. O cliente quer ser **avisado** quando um vendedor/cliente concentrar risco alto demais.
- Nenhuma gestão comercial formal (sem metas, sem ritual de acompanhamento).
- ERP existente tem dados, mas não é analisado/usado.
- Processo de amostra/teste sem rastro — hoje é feito "de boca a boca"/WhatsApp, sem prazo, sem histórico de tentativas, sem visibilidade de custo por amostra.

## Regras de negócio — preço

- Preço calculado internamente pelas vendedoras, mas a **aprovação final é sempre do cliente (dono da empresa)** — nunca do vendedor.
- Aprovação necessária em dois níveis: **preço-base do produto** (ex.: valor por m³) e **desconto por oportunidade** (varia por volume negociado).
- Margem mínima: **15% sobre o custo de produção**.
- Reajuste de preço ocorre quando o custo de matéria-prima ou o câmbio (USD) mudam — hoje feito manualmente, sem sistema.
- **v1 NÃO terá** motor de precificação automático vinculado a câmbio/matéria-prima — apenas um campo de valor final de venda, preenchido manualmente pelo time comercial. Motor automático é ideia de v2 (ver [ADR 0002](decisions/0002-sem-integracao-erp-precificacao-v1.md)).
- Sem integração com o ERP para custo — se necessário, upload manual de planilha, nunca integração viva no v1.
- Sem quantidade mínima de compra para fechar contrato, mas é possível negociar **compromisso de volume recorrente** (contrato mensal) com clientes grandes.

## Processo comercial (funil de vendas)

1. **Prospecção:** pesquisa online, feiras do setor, indicação, ou abordagem ativa porta a porta — ou inbound quando o cliente está insatisfeito com o fornecedor atual (fecha mais rápido; ex. real: recuperação do maior cliente da empresa, que havia saído por atraso de entrega do concorrente).
2. Vendedor apresenta **catálogo técnico** do produto (especificações completas) — o vendedor precisa ser tecnicamente capacitado, pois vende para o time técnico do cliente.
3. Dois caminhos possíveis a partir daqui:
   - **Caminho A — produto já existe, custo conhecido:** cota preço direto → se aceito, envia amostra para validação do cliente → fecha ou perde.
   - **Caminho B — produto novo, sem custo definido:** desenvolvimento interno do produto primeiro → ciclos de amostra/teste com o cliente até funcionar → só então define preço e oferece.
4. **Motivo de perda** deve ser registrado sempre que uma oportunidade for marcada como perdida (ex.: preço alto, prazo incompatível).

## Metas e gestão comercial (estrutura em 3 camadas)

1. **Resultado (empresa):** crescimento de faturamento mensal, número de clientes novos, clientes inativos reativados/mês.
2. **Comercial (time, medido no CRM):** oportunidades abertas por semana/mês, propostas enviadas, amostras enviadas, taxa de conversão, tempo médio de ciclo.
3. **Atividade (individual):** visitas/contatos por semana, amostras enviadas por semana/mês, clientes inativos reativados por semana.

**Rituais de gestão desejados dentro do Salesforce:**
- Reunião diária: o que cada vendedor fechou desde o dia anterior, oportunidades travadas, prioridades do dia.
- Reunião mensal de resultados: faturamento vs. meta, ranking por vendedor e por linha de produto, status dos clientes mais estratégicos, meta do mês seguinte já definida.

## Acessos

Vendedores **veem todos os registros, mas só editam os próprios**. O dono da empresa (cliente) tem acesso total (visualização + validação de relatórios e preços).

## Pós-venda / atendimento (Service Cloud)

- **Caso de amostra (pré-venda):** aberto quando uma amostra é reprovada na primeira tentativa, para registrar histórico que hoje só existe na memória do vendedor/químico. Roteado para fila do laboratório, atribuído ao químico responsável.
- **Caso de pós-venda:** tipo separado, para clientes recorrentes já ativos — reclamação de produto, lote entregue com defeito, etc. (raro, mas existe).
- Sem time formal de atendimento ao cliente — hoje o próprio vendedor responde dúvidas via WhatsApp, baixo volume, não é prioridade modelar como fluxo formal no v1.
- Prazos de referência dados pelo cliente: ~15 dias para produção de amostra (meta interna); cobrança ao cliente a cada 10 dias úteis sem retorno de teste; ~5 dias úteis para retorno sobre amostra reprovada.
- Priorização entre chamados comerciais e técnicos: **não definida pelo cliente** — tratar como fila única até definição contrária (ver pendências).

## Fora de escopo do v1 (ideias explícitas para v2)

- Motor de precificação automático vinculado a câmbio (USD) e custo de matéria-prima.
- Integração em tempo real com o ERP do cliente.
- Time formal de customer service.
- Person Accounts — deliberadamente descartado, ver [ADR 0001](decisions/0001-modelo-conta-b2b-b2c-sem-person-accounts.md).
- Portal self-service (Experience Cloud) — fora do prazo de 1 dia, a menos que sobre tempo.

## Pendências a confirmar com o cliente

- Nomes exatos dos dois químicos responsáveis pela fila do laboratório (transcrição ambígua).
- Lista de produtos (hoje só no ERP) e lista de vendedores com papéis/acessos detalhados — cliente combinou compartilhar, ainda não recebido.
- Regra de priorização entre chamados comerciais vs. técnicos no Service Cloud.
- Identidade visual: cliente não tinha nenhuma pronta no momento da reunião e autorizou o squad a criar — assets já criados estão na pasta `imgs/` (raiz do repositório).
