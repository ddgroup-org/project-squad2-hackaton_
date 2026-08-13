# Prompt 04 — Automação cruzando Sales e Service (quimicahackaton)

## Contexto do projeto (ler antes de tudo)

- **Projeto:** hackathon de 1 dia, Sales Cloud + Service Cloud, para **Quimtech Distribuidora Química Ltda.** (nome fictício — use o nome real se outro tiver sido informado), com canais B2B (empresas, insumos a granel) e B2C (consumidores finais, produtos de consumo).
- **Seu papel:** Salesforce solution builder sênior, autônomo, sem supervisão em tempo real. Decida dentro do escopo autorizado; registre a decisão.
- **Você não tem acesso a nenhum vault ou prompt anterior.** Assuma que já existem, de etapas anteriores:
  - Org de hackathon com repositório Git do projeto configurado.
  - Record Types de Account (Business Account / Individual Customer), Opportunity (B2B Sale / B2C Sale) e Case (Suporte Técnico B2B / Atendimento ao Consumidor B2C) já criados.
  Confirme isso antes de prosseguir; se algum desses elementos não existir, pare e reporte — este prompt depende diretamente deles.
- **Prioridade de automação:** declarativo (Flow, Validation Rule) antes de código.
- **Rastreabilidade:** ao final, faça retrieve da metadata alterada e commit/push no repositório do projeto. **O tech lead não tem acesso à org — sem commit e push, este trabalho é invisível para ele.**

## Objetivo deste prompt

Conectar Sales Cloud e Service Cloud, para que o hackathon demonstre um fluxo de cliente completo, não duas áreas isoladas.

## Passo a passo

### 1. Onboarding técnico automático (B2B)

- Record-Triggered Flow em Opportunity: quando uma Opportunity de Record Type "B2B Sale" for atualizada para estágio "Fechada/Ganha", criar automaticamente um Case de Record Type "Suporte Técnico B2B", com:
  - Subject: "Onboarding técnico — {Nome da Conta}".
  - Account e Contact preenchidos a partir da Opportunity.
  - Tipo de incidente: "Ficha de segurança" (como ponto de partida do relacionamento técnico).
  - Prioridade: Média.

### 2. Visão 360 do cliente

- Adicionar à página do Account (Lightning App/Home Page ou Related Lists no Page Layout) componentes mostrando, lado a lado: Opportunities relacionadas e Cases relacionados — para que, ao abrir uma conta, o vendedor ou atendente veja o histórico comercial e de suporte juntos.
- Isso deve valer tanto para Business Account quanto para Individual Customer.

### 3. Validation Rule de consistência

- Impedir que um Case de Record Type "Suporte Técnico B2B" seja criado vinculado a uma Account de Record Type "Individual Customer", e vice-versa para "Atendimento ao Consumidor B2C" com "Business Account". Mensagem de erro clara explicando a incompatibilidade.

### 4. Teste manual

- Fechar como "Ganha" uma das Opportunities B2B de exemplo (criadas no Prompt 02) e confirmar que o Case de onboarding foi criado automaticamente, com os dados corretos.
- Tentar criar deliberadamente um Case incompatível (B2B em Individual Customer) e confirmar que a Validation Rule bloqueia, com a mensagem correta.

## Critérios de aceite

- [ ] Flow de onboarding técnico criado e testado com um caso real (Opportunity fechada gerando Case).
- [ ] Componentes de visão 360 (Opportunities + Cases) visíveis na página de Account, para os dois Record Types.
- [ ] Validation Rule criada e testada (bloqueio confirmado com tentativa deliberada).
- [ ] Metadata recuperada e commitada/pushada no repositório do projeto.

## Fora de escopo

- Novos objetos ou Record Types — usar apenas os já criados nos Prompts 01–03.
- Relatórios/dashboards — Prompt 05.

## Quando parar e perguntar

- Se Opportunity, Case ou os Record Types dos prompts anteriores não existirem.
- Se o teste manual do Flow não produzir o Case esperado após duas tentativas — reporte o comportamento observado em vez de insistir silenciosamente.

## Formato da entrega

- Confirmação do teste manual do Flow (com o Case gerado).
- Confirmação do teste da Validation Rule (bloqueio funcionando).
- Link do commit/push correspondente.
- Pendências ou riscos identificados.
