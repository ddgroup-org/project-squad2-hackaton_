# Prompt 03 — Service Cloud B2B/B2C (quimicahackaton)

## Contexto do projeto (ler antes de tudo)

- **Projeto:** hackathon de 1 dia, Sales Cloud + Service Cloud, para **Quimtech Distribuidora Química Ltda.** (nome fictício — use o nome real se outro tiver sido informado), com dois canais:
  - **B2B:** empresas compram insumos químicos a granel. Pós-venda = suporte técnico: dúvidas de manuseio, ficha de segurança (FISPQ/SDS), incidentes de uso, relacionamento contínuo.
  - **B2C:** consumidores finais compram produtos de limpeza, piscina e jardim. Pós-venda = atendimento ao consumidor: dúvidas de uso, reclamações, trocas.
- **Seu papel:** Salesforce solution builder sênior, autônomo, sem supervisão em tempo real. Decida dentro do escopo autorizado; registre a decisão.
- **Você não tem acesso a nenhum vault ou prompt anterior.** Assuma que já existem, de etapas anteriores:
  - Uma org de hackathon (nunca produção) com repositório Git do projeto já configurado.
  - Record Types "Business Account" e "Individual Customer" em Account, com contas e contatos de exemplo já carregados.
  Confirme isso antes de prosseguir; se não existir, pare e reporte.
- **Licenças podem variar entre orgs.** Antes de usar Omni-Channel, Knowledge ou Entitlements, **verifique se estão disponíveis nesta org**. Cada item abaixo tem um caminho alternativo declarativo caso a licença não exista — use o alternativo sem bloquear a entrega, e registre qual caminho foi usado.
- **Prioridade de automação:** declarativo antes de código.
- **Rastreabilidade:** ao final, faça retrieve da metadata alterada e commit/push no repositório do projeto. **O tech lead não tem acesso à org — sem commit e push, este trabalho é invisível para ele.**

## Objetivo deste prompt

Configurar o atendimento para os dois canais, com processo, roteamento e uma base mínima de conhecimento.

## Passo a passo

### 1. Case — Record Types

- **"Suporte Técnico B2B"** — campos relevantes: produto envolvido, tipo de incidente (Dúvida de manuseio / Ficha de segurança / Incidente de uso / Outro), urgência.
- **"Atendimento ao Consumidor B2C"** — campos relevantes: produto envolvido, motivo (Dúvida de uso / Reclamação / Troca / Outro).
- Campo `Origem__c` (ou usar o campo padrão `Origin`): Telefone, E-mail, Web.
- Page Layouts distintos por Record Type.

### 2. Roteamento

- **Se Omni-Channel estiver disponível:** configurar duas Routing Configurations simples ("Atendimento B2B", "Atendimento B2C") e uma Queue para cada, associadas ao Record Type do Case.
- **Se Omni-Channel não estiver disponível:** usar Case Assignment Rules direcionando por Record Type para duas Queues equivalentes ("Fila Suporte B2B", "Fila Suporte B2C"). Registrar qual caminho foi usado.

### 3. Base de conhecimento

- **Se Knowledge estiver disponível:** criar 2–3 artigos simples (ex: "Como interpretar a Ficha de Segurança de um produto químico", "Procedimento de troca para produtos B2C", "Cuidados no manuseio de solventes industriais"), publicados e associados aos Record Types de Case correspondentes.
- **Se Knowledge não estiver disponível:** criar esse conteúdo como um campo de texto rico (`Instrucoes_Padrao__c`, texto longo) em um objeto simples ou como Case Comments padrão em casos de exemplo, e registrar a limitação.

### 4. SLA simples

- **Se Entitlements/Milestones estiver disponível:** configurar um Entitlement Process básico com um milestone de "Primeira resposta" (ex: 4h para B2B, 24h para B2C).
- **Se não estiver disponível:** usar um campo `Prioridade__c` (Alta/Média/Baixa) e um Record-Triggered Flow que sinalize (ex: campo `Vencido__c` ou tarefa) quando o Case estiver aberto há mais tempo que o esperado, como aproximação declarativa de SLA. Registrar a limitação.

### 5. Dados de exemplo

Criar ao menos:
- 2 Cases "Suporte Técnico B2B" (um aberto, um fechado), vinculados às contas B2B existentes.
- 2 Cases "Atendimento ao Consumidor B2C" (um aberto, um fechado), vinculados às contas B2C existentes.

## Critérios de aceite

- [ ] Record Types "Suporte Técnico B2B" e "Atendimento ao Consumidor B2C" criados em Case, com layouts distintos.
- [ ] Roteamento funcional (Omni-Channel ou Assignment Rules, conforme licença), testado com um Case novo de cada tipo.
- [ ] Conteúdo de base de conhecimento criado (Knowledge ou alternativa), com pelo menos 2 itens.
- [ ] SLA básico configurado (Entitlement ou alternativa declarativa), com a limitação registrada se aplicável.
- [ ] 4 Cases de exemplo criados conforme especificado.
- [ ] Metadata recuperada e commitada/pushada no repositório do projeto.

## Fora de escopo

- Opportunity, Sales Cloud — Prompt 02 (se ainda não executado, não recriar aqui).
- Automação cruzando Sales e Service — Prompt 04.
- Relatórios/dashboards — Prompt 05.

## Quando parar e perguntar

- Se os Record Types de Account do Prompt 01 não existirem.
- Se nenhuma das licenças (Omni-Channel, Knowledge, Entitlements) estiver disponível e não for óbvio como adaptar sem perder o valor demonstrado — reporte antes de simplificar demais.

## Formato da entrega

- Lista de componentes criados (Record Types, campos, roteamento, base de conhecimento, SLA).
- Qual caminho foi usado em cada item dependente de licença (nativo ou alternativo), e por quê.
- Resultado do teste manual de roteamento.
- Link do commit/push correspondente.
- Pendências ou riscos identificados.
