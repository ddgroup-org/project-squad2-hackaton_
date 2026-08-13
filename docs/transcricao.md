# Reunião de kickoff + levantamento de requisitos — HACKATON DDGROUP

- **Data:** 13/08/2026, 07:57 (duração 87 min)
- **Cliente simulado (role-play):** Gabriel Jacob, no papel de dono da **Cromatta Química**
- **Condução:** Leonardo Alves (regras do hackathon), squad "GP" fazendo o levantamento (Caio Migano, Julio Gabriel, Ismael Alves, Barbara Lopes, Manuella Cypriano, André Nascimento, Erick Freitas)
- **Transcrição original (íntegra):** [link Tactiq](https://app.tactiq.io/api/2/u/m/r/YedwPAaRRWvKuNrPw7Ms?o=txt)

> Este arquivo é uma versão condensada da transcrição, organizada por tema. A conversa informal, problemas de Slack/câmera e brincadeiras foram removidos — só ficou o que é relevante para regras do hackathon e levantamento de requisitos do cliente.

---

## 1. Regras do hackathon

- **Formato:** um cliente hipotético (Jacob/Cromatta Química) é atendido por 4 squads, cada squad implementando Sales Cloud + Service Cloud com base no que o cliente pedir.
- **Regra principal: nenhuma configuração manual no Salesforce.** Tudo deve ser feito via Claude/IA. Só fazer manual o que for comprovadamente impossível via IA (ex.: configuração de bot fora do Salesforce).
- **Duração:** 1 dia. Agenda: 8h–9h/9h30 abertura + briefing com o cliente; 9h–17h execução; 17h30–18h30 apresentações (15 min por squad, 4 squads).
- **Papéis por squad:** GP, Tech Lead (referência técnica/arquiteto — não desenvolve, orienta o time), Dev(s) (implementam), e uma pessoa focada em uso de IA por squad.
- **Squads e responsáveis por IA:** Squad 1, Squad 2 (**Inaldo** — nosso squad, repositório `Squad2-Cromatta-quimica`), Squad 3 (Kadu), Squad 4 (Raquel).
- **Mentores** (Diogo Vidal, Anna Pasolini, Letícia Silveira, João) — não vinculados a um squad específico, disponíveis a todos via canal de dúvidas no Slack.
- **Dúvidas para o cliente:** centralizadas em canal único de dúvidas, para que todos os squads recebam a mesma informação ao mesmo tempo (o cliente não quer responder a mesma coisa diferente para squads diferentes).
- **Governança de uso de IA/tokens:** cada squad deve gerenciar seu próprio consumo (plano pago com limite de tokens). Dica dada: limpar o contexto da sessão periodicamente para economizar; documentar na apresentação final como o squad geriu esse consumo.

## 2. Entregáveis esperados

- **BRD** — documento de levantamento de requisitos (com base nas perguntas feitas ao cliente).
- **Solution Design** — arquitetura do que será implementado.
- **Repositório GitHub** — todos precisam de conta no GitHub (convite enviado pela organização); deve conter evidência do uso do Claude (documento ou referência/histórico no próprio repositório).
- **Apresentação final** — PPT + demo ao vivo dos principais fluxos (ex.: fluxo de oportunidade, fluxo de cases).
- **Backlog organizado** na ferramenta "Tarefai" (gestão ágil), com as demandas bem estruturadas.
- BRD e Solution Design, quando finalizados, devem ser enviados por e-mail para Jacob, Ana, Letícia, Diogo e João.

## 3. Critérios de avaliação

- **25%** — aderência: os requisitos foram implementados corretamente.
- **25%** — uso do Claude/IA na implementação (extrema importância, segundo o cliente).
- Qualidade de implementação — validação de todos os fluxos entregues.
- Organização ágil — backlog no Tarefai bem estruturado.
- **15%** — apresentação final (clareza, didática, demo ao vivo).

## 4. Premiação

- Premiação em dinheiro: **R$2.000 por membro**, para os membros das equipes que participaram.
- Certificado de participação para todos.

---

## 5. Perfil do cliente simulado — Cromatta Química

- Indústria química no interior do Ceará, no mercado desde 1980.
- **Linhas de produto:**
  1. **Cromata** — tintas e vernizes, e dispersão de pigmento (matéria-prima para outros fabricantes de tinta).
  2. **Flecha** — produtos para manutenção de couros e calçados (hidratação de couro, limpeza de calçado/tênis/veludo).
  3. **Jato** — tintas para impressão a jato de tinta (impressoras).
- **Clientes:** atende tanto **PJ** (outras indústrias, marcas — ex.: revenda para a marca "Democrata") quanto **PF** (venda direta via site próprio). O foco maior é PJ.
- **Produção:** 80% fabricação própria; matéria-prima importada (China, EUA, Europa). Preço final é volátil por câmbio (USD) e custo de matéria-prima.
- **Dores atuais do negócio (ditas pelo próprio cliente):**
  - Faturamento em queda recente.
  - Concentração de receita em poucos clientes grandes — uma vendedora (Camila, linha Flecha) responde por ~60% da receita: risco alto se ela saísse ou o cliente cancelasse.
  - Nenhuma gestão comercial formal: sem metas, sem ritual de acompanhamento.
  - ERP existente tem dados, mas não é analisado/usado.
  - Processo de amostra/teste sem rastro: hoje é feito "de boca a boca"/WhatsApp, sem prazo, sem histórico de tentativas, sem visibilidade de custo por amostra.

## 6. Regras de negócio — Comercial / Precificação

- **Times de venda por linha de produto:**
  - **Camila** — linha Flecha (couro/calçados). Meta: 2 novos clientes/mês.
  - **Ronaldo** — linha Cromata. É representante externo (não é CLT, atende outras empresas também), ticket médio mais alto, menos volume de fechamentos. Meta: 1 nova conta/trimestre.
  - **Marcelo** — linha Cromata, interno, foco em abrir novas contas. Meta: 2 novos clientes/mês.
  - **Diego, Bruno e Thiago** — linha Jato, foco 100% em abrir novos clientes + atender a pequena carteira já existente. Meta: 2 novos clientes/mês cada.
  - Carteira de cliente não é fixa por padrão — o cliente fica com quem trouxe (vendedor que prospectou), dentro da linha de produto correspondente.
- **Preço:**
  - Calculado internamente pelas vendedoras, mas **aprovação final do preço é sempre do cliente (Jacob)** — nunca do vendedor.
  - Aprovação necessária tanto no **preço-base do produto** (ex.: valor por m³) quanto no **desconto por oportunidade** (varia por volume negociado).
  - Margem mínima: **15% sobre o custo de produção**.
  - Reajuste de preço ocorre sempre que o custo de matéria-prima ou o câmbio (USD) mudam — hoje feito manualmente, sem sistema.
  - **Fora de escopo do v1:** motor automático de precificação vinculado a câmbio/matéria-prima (ideia para "v2"). Para o v1, basta um campo de valor final de venda, preenchido manualmente pelo time comercial.
  - Não há integração com o ERP para custo — se necessário, custo dos produtos seria carregado manualmente (ex.: upload de planilha), sem integração viva.
- **Sem quantidade mínima de compra** para fechar contrato, mas há margem mínima (15%) e é possível negociar **compromisso de volume recorrente** (contrato mensal) com clientes grandes.

## 7. Processo comercial (funil de vendas)

1. **Prospecção:** vendedores pesquisam empresas na internet, vão a feiras do setor, ou recebem indicação. Primeiro contato por e-mail/telefone/WhatsApp — inclui abordagem ativa porta a porta. Fluxo alternativo mais rápido: cliente insatisfeito com fornecedor atual busca a Cromatta diretamente (ex.: recuperação do maior cliente da empresa, que havia saído por atraso de entrega do concorrente).
2. Vendedor apresenta **catálogo técnico** do produto (especificações completas) — o vendedor precisa ser tecnicamente capacitado, pois vende para o time técnico do cliente.
3. A partir daqui, dois caminhos possíveis:
   - **Caminho A — produto já existe/custo conhecido:** cotar preço direto; se aceito, envia amostra para validação do cliente; se recusado (preço alto), oportunidade é perdida.
   - **Caminho B — produto novo, sem custo definido:** desenvolvimento interno do produto primeiro, ciclo de amostras/testes com o cliente até funcionar, só então define preço e oferece.
4. **Motivo de perda** deve ser registrado (ex.: preço alto, prazo incompatível).
5. Cliente recorrente = contrato com compromisso de volume mínimo mensal.

## 8. Metas e gestão comercial (estrutura em 3 camadas)

1. **Resultado (empresa):** crescimento de faturamento mensal, número de clientes novos, clientes inativos reativados/mês.
2. **Comercial (time, medido no CRM):** oportunidades abertas por semana/mês, propostas enviadas, amostras enviadas, taxa de conversão, tempo médio de ciclo.
3. **Atividade (individual):** visitas/contatos por semana, amostras enviadas por semana/mês, clientes inativos reativados por semana.

**Rituais de gestão desejados dentro do Salesforce:**
- Reunião diária: o que cada vendedor fechou desde o dia anterior, oportunidades travadas, prioridades do dia.
- Reunião mensal de resultados: faturamento vs. meta, ranking por vendedor e por linha de produto, status dos clientes mais estratégicos (ex.: tempo desde o último pedido), meta do mês seguinte já definida.

**Acessos:** vendedores veem todos os registros, mas só editam os próprios. Jacob tem acesso total (visualização + validação de relatórios).

---

## 9. Requisitos — Sales Cloud

- Cadastro de **Lead** com campo de origem (feira, indicação, prospecção ativa/porta a porta, internet), nome da empresa, CNPJ, contato.
- Conversão de Lead em Conta/Contato/Oportunidade, associando qual(is) linha(s) de produto o lead vai comprar (Cromata / Flecha / Jato).
- **Funil de Oportunidade** com suporte aos dois caminhos comerciais (produto existente vs. produto a desenvolver).
- Registro de **motivo de perda** da oportunidade.
- Registro de **amostras enviadas** dentro da oportunidade: produto, quantidade/peso, data de envio, resultado, número de tentativas, custo estimado da amostra.
- **Indicador de urgência** na oportunidade (ex.: cliente com problema no fornecedor atual — fechamento mais rápido).
- **Compromisso de volume** para clientes grandes (contrato recorrente com mínimo mensal).
- Fluxo de **aprovação de preço/desconto** — sempre por Jacob, no preço-base do produto e no desconto por oportunidade.
- Relatório de **clientes inativos** (sem pedido há 60+ dias).
- Dashboards de gestão comercial (diário e mensal) conforme seção 8.
- Permissão: vendedores leem tudo, editam só os próprios registros.

## 10. Requisitos — Service Cloud

- **Abertura de caso quando uma amostra é reprovada** na primeira tentativa, para registrar histórico (hoje só existe na memória do vendedor/químico).
- Casos de amostra roteados para **fila do laboratório**, atribuídos ao químico responsável (químicos: Sérgio e André — confirmar nomes exatos com o cliente).
- Campo de **causa técnica de reprovação** (picklist): incompatibilidade com substrato, incompatibilidade com a base do cliente, instabilidade do produto, entupimento de cabeçote, aspecto/aparência fora do esperado, entre outras.
- **Histórico de tentativas de formulação** vinculado ao caso — sinalizar quando já passou de 2 tentativas.
- **Marcação de visita técnica** do químico ao cliente, registrada no Service Cloud.
- **Caso de pós-venda** (tipo separado do caso de amostra): reclamações de cliente recorrente já ativo — produto com problema, lote entregue com defeito, etc.
- Prazos de referência: meta interna de ~15 dias para produção de amostra; cobrança ao cliente a cada 10 dias úteis sem retorno de teste; ~5 dias úteis para retorno sobre amostra reprovada.
- **Priorização entre chamados comerciais e técnicos:** não há regra definida hoje pelo cliente — ponto aberto, tratar como fila única (FIFO) até definição contrária.

## 11. Explicitamente fora de escopo do v1 (ideias para "v2")

- Motor de precificação automático vinculado a câmbio (USD) e custo de matéria-prima.
- Integração em tempo real com o ERP do cliente (custo de produtos) — no máximo upload manual de planilha.
- Time formal de atendimento ao cliente (customer service) — hoje o próprio vendedor responde dúvidas via WhatsApp, baixo volume, não é prioridade modelar.

## 12. Pendências / pontos a confirmar com o cliente

- Confirmar nomes exatos dos dois químicos responsáveis pela fila do laboratório (transcrição ambígua: "Sérgio e André").
- Cliente ainda vai compartilhar a lista de produtos (hoje só no ERP) e a lista de vendedores com papéis/acessos detalhados — combinado em reunião, não recebido ainda.
- Regra de priorização entre chamados comerciais vs. técnicos no Service Cloud não foi definida pelo cliente.
- **Branding:** perguntado explicitamente se havia identidade visual (cores, logo) — cliente confirmou que não tinha nada além do nome "CROMATTA QUÍMICA", e que o squad pode criar/inventar a identidade visual. (Assets de marca foram criados depois e já estão em `imgs/`.)
