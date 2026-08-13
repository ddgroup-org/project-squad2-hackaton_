# Prompt 06 — Preparação de demo e pitch (quimicahackaton)

## Contexto do projeto (ler antes de tudo)

- **Projeto:** hackathon de 1 dia, Sales Cloud + Service Cloud, para **Quimtech Distribuidora Química Ltda.** (nome fictício — use o nome real se outro tiver sido informado), com canais B2B (empresas, insumos a granel) e B2C (consumidores finais, produtos de consumo).
- **Seu papel:** Salesforce solution builder sênior, autônomo, sem supervisão em tempo real. Esta é a **última etapa** do dia — o foco agora é deixar tudo pronto para apresentar, não construir mais funcionalidade nova.
- **Você não tem acesso a nenhum vault ou prompt anterior.** Assuma que todas as etapas anteriores (modelo de dados, Sales Cloud, Service Cloud, automação cross-cloud, relatórios e dashboard) já foram executadas na mesma org. Confirme rapidamente que os principais componentes existem antes de prosseguir; se algo essencial estiver faltando, registre como risco em vez de tentar reconstruir tudo agora — o tempo é curto.
- **Rastreabilidade:** ao final, faça retrieve de qualquer metadata nova (perfis/permission sets) e commit/push final no repositório do projeto, com um resumo completo do hackathon no README desse repositório. **O tech lead não tem acesso à org — o commit final e o README são a única entrega que ele vai revisar.**

## Objetivo deste prompt

Preparar o ambiente para demonstração ao vivo e produzir o material de apoio para o pitch.

## Passo a passo

### 1. Usuários/perfis de demonstração

- Criar dois Permission Sets simples: **"Vendedor"** (acesso a Lead, Opportunity, Account, Contact) e **"Atendimento"** (acesso a Case, Knowledge se existir, Account, Contact).
- Se houver mais de um usuário disponível na org, atribuir os Permission Sets adequadamente. Se houver apenas o usuário admin (comum em Developer Edition), atribuir ambos ao mesmo usuário e registrar essa limitação — não é necessário criar usuários fictícios adicionais.

### 2. Roteiro de demonstração

Escrever, em `docs/roteiro-demo.md` no repositório do projeto, um roteiro passo a passo cobrindo:

1. Abertura: contexto da Quimtech (ou nome real), os dois canais B2B e B2C, o problema que a solução resolve.
2. Fluxo B2B ao vivo: abrir uma Business Account → mostrar Opportunity em Cotação Técnica → mostrar o Approval Process de desconto → fechar como Ganha → mostrar o Case de onboarding técnico criado automaticamente.
3. Fluxo B2C ao vivo: abrir uma Individual Customer → mostrar Opportunity simples → mostrar um Case de atendimento ao consumidor e seu roteamento.
4. Fechamento: mostrar o dashboard executivo, destacando pipeline por segmento e indicadores de atendimento.
5. Tempo estimado por bloco, para caber no tempo de pitch do hackathon (se o tempo de pitch não for conhecido, assumir 5 minutos e registrar como pendência a confirmar).

### 3. Checklist final de qualidade

Antes de considerar pronto, verificar e registrar o resultado de cada item:

- [ ] Todos os dados de exemplo dos prompts anteriores existem e estão visíveis.
- [ ] O Flow de onboarding técnico (Prompt 04) foi testado nesta sessão e funciona.
- [ ] O dashboard (Prompt 05) carrega sem erro e sem componente vazio.
- [ ] Nenhum erro visível em Setup (ex: Flow inativo, Validation Rule mal configurada).
- [ ] Toda a metadata da org está commitada e pushada — `git status` limpo no repositório do projeto.

### 4. Relato final ao tech lead

Atualizar o README do repositório do projeto Salesforce com uma seção final "Resumo do hackathon", contendo:

- O que foi entregue (lista objetiva por área: dados, Sales Cloud, Service Cloud, automação, relatórios).
- Limitações e adaptações feitas por licenciamento da org (reunir o que foi registrado nos Prompts 00, 02 e 03).
- Riscos conhecidos e o que faria parte de uma próxima iteração fora do hackathon.
- Link do commit final.

## Critérios de aceite

- [ ] Permission Sets criados e atribuídos (ou limitação registrada).
- [ ] `docs/roteiro-demo.md` criado no repositório do projeto, cobrindo os dois fluxos (B2B e B2C) e o dashboard.
- [ ] Checklist final executado, com o resultado real de cada item (não presumido).
- [ ] README do repositório atualizado com o resumo do hackathon.
- [ ] Commit/push final realizado, `git status` limpo.

## Fora de escopo

- Qualquer funcionalidade nova não coberta pelos prompts anteriores — se surgir a tentação de adicionar algo a mais, registrar como sugestão para depois do hackathon, não implementar agora.

## Quando parar e perguntar

- Se o checklist final revelar algo quebrado que não seja possível corrigir rapidamente — reportar o problema exato em vez de ocultá-lo ou contornar silenciosamente.

## Formato da entrega

- Resultado do checklist final, item a item.
- Confirmação de que o roteiro de demo foi escrito e onde está.
- Link do commit/push final.
- Resumo do que ficou pendente ou arriscado, para o tech lead decidir o que fazer no tempo restante do hackathon.
