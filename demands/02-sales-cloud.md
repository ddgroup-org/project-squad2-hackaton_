# Prompt 02 — Sales Cloud B2B/B2C (quimicahackaton)

## Contexto do projeto (ler antes de tudo)

- **Projeto:** hackathon de 1 dia, Sales Cloud + Service Cloud, para **Quimtech Distribuidora Química Ltda.** (nome fictício — use o nome real se outro tiver sido informado), com dois canais:
  - **B2B:** empresas compram insumos químicos a granel. Ciclo técnico, mais longo: cotação, ficha de segurança, negociação de volume/prazo, aprovação de desconto acima de um limite.
  - **B2C:** consumidores finais compram produtos de limpeza, piscina e jardim. Ciclo simples e rápido.
- **Seu papel:** Salesforce solution builder sênior, autônomo, sem supervisão em tempo real. Decida dentro do escopo autorizado; registre a decisão.
- **Você não tem acesso a nenhum vault ou prompt anterior.** Assuma que já existem, de etapas anteriores:
  - Uma org de hackathon (nunca produção) com repositório Git do projeto já configurado.
  - Record Types "Business Account" e "Individual Customer" em Account, com contas e contatos de exemplo já carregados.
  - Produtos (`Product2`) já criados, com campo `Grupo_de_Produto__c` ("Insumo a granel" / "Consumo") e Price Book Entries ativas.
  Confirme que esses elementos existem antes de prosseguir; se não existirem, pare e reporte — não recrie do zero sem confirmar, para não gerar duplicidade.
- **Prioridade de automação:** declarativo (campo, layout, Flow) antes de código. Use Apex/LWC apenas se comprovadamente necessário, com justificativa registrada.
- **Rastreabilidade:** ao final, faça retrieve da metadata alterada e commit/push no repositório do projeto. **O tech lead não tem acesso à org — sem commit e push, este trabalho é invisível para ele.**

## Objetivo deste prompt

Configurar o pipeline de vendas para os dois canais, com processo e automação mínima que diferencie B2B de B2C.

## Passo a passo

### 1. Lead

- Campo `Segmento__c` (picklist: B2B, B2C) em Lead, preenchido na captura.
- Processo de conversão padrão do Salesforce, mapeando o Lead convertido para o Record Type de Account correto (Business Account se B2B, Individual Customer se B2C).

### 2. Opportunity

- Dois Record Types: **"B2B Sale"** e **"B2C Sale"**.
- Sales Path habilitado para ambos, com estágios adaptados:
  - **B2B Sale:** Qualificação → Cotação Técnica → Negociação → Fechamento (Ganha/Perdida).
  - **B2C Sale:** Qualificação → Fechamento (Ganha/Perdida) — ciclo curto, sem estágio técnico.
- Campo `Desconto_Solicitado__c` (percentual) em Opportunity, aplicável principalmente ao fluxo B2B.
- `OpportunityLineItem` habilitado, usando os produtos já cadastrados (insumos a granel para Opportunity B2B, produtos de consumo para Opportunity B2C — não é uma regra de validação obrigatória neste prompt, apenas o padrão esperado nos dados de exemplo).

### 3. Approval Process (B2B)

- Approval Process simples em Opportunity: quando `Desconto_Solicitado__c` for maior que 15%, requer aprovação (aprovador: qualquer usuário com perfil de gestor disponível na org, ou o próprio usuário admin caso não haja outro perfil — registrar a limitação se for o caso).
- Aplicável apenas a Opportunities de Record Type "B2B Sale".

### 4. Atribuição automática (Flow)

- Record-Triggered Flow em Opportunity (ou em Lead, o que for mais adequado): ao criar um registro com `Segmento__c` = B2B, garantir que o Owner seja um usuário/fila de "Vendas B2B"; se B2C, "Vendas B2C". Se a org tiver um único usuário disponível (comum em Developer Edition), simular com Queues em vez de usuários reais, e registrar essa adaptação.

### 5. Dados de exemplo

Criar ao menos:
- 2 Opportunities "B2B Sale" (uma em estágio de Cotação Técnica, outra Fechada/Ganha), vinculadas às contas B2B já existentes, com produtos de insumo a granel.
- 2 Opportunities "B2C Sale" (uma em Qualificação, outra Fechada/Ganha), vinculadas às contas B2C já existentes, com produtos de consumo.

### 6. Interface

- List views separadas por Record Type ("Oportunidades B2B", "Oportunidades B2C").
- Kanban/Path visível e funcional para os dois Record Types.

## Critérios de aceite

- [ ] Record Types "B2B Sale" e "B2C Sale" criados em Opportunity, com estágios distintos e Path habilitado.
- [ ] Approval Process funcional para desconto acima de 15% em Opportunities B2B (testado manualmente com um registro real).
- [ ] Flow de atribuição automática criado e testado (criar um registro novo e confirmar o Owner/Queue resultante).
- [ ] Dados de exemplo (4 Opportunities) criados conforme especificado, com produtos associados.
- [ ] List views por segmento criadas.
- [ ] Metadata recuperada e commitada/pushada no repositório do projeto.

## Fora de escopo

- Case, Service Cloud — Prompt 03.
- Automação cruzando Sales e Service — Prompt 04.
- Relatórios/dashboards — Prompt 05.

## Quando parar e perguntar

- Se os Record Types de Account ou os produtos do Prompt 01 não existirem.
- Se não houver nenhum perfil/usuário adicional para simular aprovação, e não for óbvio como adaptar sem inventar uma estrutura de usuários fictícia arriscada.

## Formato da entrega

- Lista de componentes criados (Record Types, campos, Flow, Approval Process).
- Resultado do teste manual do Approval Process e do Flow de atribuição.
- Qualquer adaptação feita por limitação da org (ex: fila em vez de usuário real).
- Link do commit/push correspondente.
- Pendências ou riscos identificados.
