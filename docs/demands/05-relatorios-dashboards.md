# Prompt 05 — Relatórios e dashboards (quimicahackaton)

## Contexto do projeto (ler antes de tudo)

- **Projeto:** hackathon de 1 dia, Sales Cloud + Service Cloud, para **Quimtech Distribuidora Química Ltda.** (nome fictício — use o nome real se outro tiver sido informado), com canais B2B (empresas, insumos a granel) e B2C (consumidores finais, produtos de consumo).
- **Seu papel:** Salesforce solution builder sênior, autônomo, sem supervisão em tempo real. Decida dentro do escopo autorizado; registre a decisão.
- **Você não tem acesso a nenhum vault ou prompt anterior.** Assuma que já existem, de etapas anteriores: Account, Opportunity e Case com os Record Types B2B/B2C já criados e populados com dados de exemplo, incluindo o Case de onboarding automático do Prompt 04. Confirme isso antes de prosseguir.
- **Rastreabilidade:** ao final, faça retrieve da metadata alterada e commit/push no repositório do projeto. **O tech lead não tem acesso à org — sem commit e push, este trabalho é invisível para ele.**

## Objetivo deste prompt

Criar os relatórios e o dashboard que serão usados na demo/pitch final (Prompt 06), mostrando o valor da solução de forma visual.

## Passo a passo

### 1. Relatórios

Criar uma pasta de relatórios "Quimtech Hackathon" e, dentro dela:

- **Pipeline por segmento** — Opportunities agrupadas por Record Type (B2B Sale / B2C Sale) e por estágio, com valor somado.
- **Taxa de conversão de Lead** — Leads por `Segmento__c`, convertidos vs. não convertidos.
- **Casos por tipo e status** — Cases agrupados por Record Type e por Status (Aberto/Fechado), com contagem.
- **Tempo médio de resolução de Case** — usando `ClosedDate` menos `CreatedDate` (ou campo de duração padrão, se disponível), agrupado por Record Type.

### 2. Dashboard

Criar um dashboard "Quimtech — Visão Executiva" com:

- Gráfico de pipeline por segmento (do relatório correspondente).
- Gráfico de conversão de Lead.
- Gráfico de casos por tipo/status.
- Indicador (métrica única) de tempo médio de resolução de Case.

Layout simples, uma coluna ou duas, priorizando legibilidade em apresentação de tela cheia — este dashboard será mostrado ao vivo no Prompt 06.

### 3. Verificação

- Abrir o dashboard e confirmar que todos os componentes carregam dados reais (não vazios) — os dados de exemplo dos Prompts 01–04 devem ser suficientes para isso.
- Se algum componente aparecer vazio, verificar se o filtro do relatório está coerente com os Record Types e dados existentes antes de reportar como bloqueio.

## Critérios de aceite

- [ ] 4 relatórios criados conforme especificado, todos retornando dados.
- [ ] Dashboard criado com os 4 componentes, todos exibindo dados reais.
- [ ] Metadata recuperada e commitada/pushada no repositório do projeto.

## Fora de escopo

- Novos dados de exemplo além dos já criados — se os dados existentes não forem suficientes para um relatório ficar visualmente interessante, registrar isso como observação para o Prompt 06, não criar dados novos silenciosamente aqui.

## Quando parar e perguntar

- Se os objetos/Record Types dos prompts anteriores não existirem ou estiverem vazios.

## Formato da entrega

- Lista dos relatórios e do dashboard criados, com link/caminho.
- Confirmação de que todos os componentes exibem dados reais.
- Observação sobre qualquer dado insuficiente para uma boa visualização (a decidir no Prompt 06 se vale a pena complementar).
- Link do commit/push correspondente.
- Pendências ou riscos identificados.
