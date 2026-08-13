# Prompt 01 — Modelo de dados B2B/B2C (quimicahackaton)

## Contexto do projeto (ler antes de tudo)

- **Projeto:** hackathon de 1 dia, Sales Cloud + Service Cloud, para **Quimtech Distribuidora Química Ltda.** (nome fictício — use o nome real se outro tiver sido informado), com dois canais de cliente:
  - **B2B:** empresas (fábricas, laboratórios, indústrias) compram insumos químicos a granel (solventes, ácidos, matérias-primas). Ciclo técnico e mais longo.
  - **B2C:** consumidores finais compram produtos de limpeza, piscina e jardim. Ciclo simples e rápido.
- **Seu papel:** Salesforce solution builder sênior, autônomo, sem supervisão em tempo real. Decida dentro do escopo autorizado; registre a decisão.
- **Você não tem acesso a nenhum vault ou prompt anterior.** Assuma que o Prompt 00 já foi executado: existe uma org de hackathon (Developer Edition/Trailhead Playground/Scratch Org, nunca produção), autenticada, com um repositório Git do projeto já criado e configurado. **Confirme isso antes de prosseguir**; se não existir, pare e peça para o Prompt 00 ser executado primeiro.
- **Decisão arquitetural já tomada, não reabrir:** este projeto **não usa Person Accounts** — são irreversíveis e dependem de aprovação do Salesforce Support, inviável em 1 dia. Em vez disso, o modelo de cliente B2C usa um **Record Type "Individual Customer" em Account**, com um Account por pessoa física e um único Contact relacionado. Se a org já tiver Person Accounts habilitado por algum motivo anterior a este hackathon, pare e reporte antes de decidir qual caminho seguir — não decida sozinho reverter essa premissa.
- **Rastreabilidade:** ao final, faça `sf project retrieve start` (ou equivalente) da metadata criada e `git add` + `commit` + `push` para o repositório do projeto. **O tech lead não tem acesso à org — sem commit e push, este trabalho é invisível para ele.**

## Objetivo deste prompt

Criar o modelo de dados que sustenta os dois canais: contas, contatos e catálogo de produto.

## Passo a passo

### 1. Record Types em Account

- **Business Account** — para clientes B2B.
- **Individual Customer** — para clientes B2C.
- Campos customizados em Account (nomes de API sugeridos, ajustar prefixo conforme padrão da org):
  - `Segmento__c` (picklist: B2B, B2C) — preenchido automaticamente conforme o Record Type, ou mantido coerente com ele.
  - `Setor_Industrial__c` (texto ou picklist, aplicável a Business Account: ex. Metalurgia, Farmacêutico, Têxtil).
  - `Documento__c` (texto, CNPJ para Business Account, CPF para Individual Customer — não validar formato real de CPF/CNPJ, é dado fictício de demonstração).
- Page Layouts distintos por Record Type, mostrando apenas os campos relevantes a cada um.

### 2. Contact

- Para Business Account: relação normal 1:N (uma conta empresarial pode ter vários contatos).
- Para Individual Customer: um único Contact por Account, representando a própria pessoa física.

### 3. Catálogo de produto

- `Product2` com um campo customizado `Grupo_de_Produto__c` (picklist: "Insumo a granel", "Consumo").
- Standard Price Book ativado, com `PricebookEntry` para cada produto.
- Produtos de exemplo (criar exatamente estes, para consistência com os próximos prompts e com a demo final):

  | Nome | Grupo | Canal |
  | --- | --- | --- |
  | Solvente Industrial X-40 | Insumo a granel | B2B |
  | Ácido Clorídrico Técnico | Insumo a granel | B2B |
  | Cloro Granulado para Piscina | Consumo | B2C |
  | Multiuso Concentrado Bio | Consumo | B2C |
  | Fertilizante Líquido Jardim Verde | Consumo | B2C |

### 4. Dados de exemplo

Criar os seguintes registros (nomes fictícios, coerentes com os próximos prompts):

**Business Account:**

| Nome | Setor | Documento |
| --- | --- | --- |
| Indústria Fortex Ltda. | Metalurgia | 12.345.678/0001-90 |
| Laboratório Vitallab | Farmacêutico | 23.456.789/0001-01 |
| Confecções Rio Têxtil | Têxtil | 34.567.890/0001-12 |

Cada uma com pelo menos 1 Contact (nome fictício, cargo de compras ou técnico).

**Individual Customer:**

| Nome | Documento |
| --- | --- |
| Mariana Souza | 111.111.111-11 |
| Carlos Andrade | 222.222.222-22 |
| Beatriz Lima | 333.333.333-33 |

Cada uma com o próprio Contact relacionado.

### 5. Segurança — nível mínimo para 1 dia

Não construir sharing rules complexas. Manter OWD padrão da org ou Public Read/Write nos objetos envolvidos — suficiente para a demo. Registrar essa decisão no relato final, para o tech lead saber que segurança fina de dados **não** foi tratada neste hackathon.

## Critérios de aceite

- [ ] Record Types "Business Account" e "Individual Customer" criados em Account, com layouts distintos.
- [ ] Campos customizados criados e visíveis nos layouts corretos.
- [ ] 3 contas B2B + contatos e 3 contas B2C + contatos criadas conforme a tabela acima.
- [ ] 5 produtos criados, com Price Book Entries ativas.
- [ ] Metadata alterada recuperada (retrieve) e commitada/pushada no repositório do projeto.

## Fora de escopo

- Opportunity, Case, Flow, relatório — começam nos próximos prompts.
- Person Accounts, sharing rules avançadas, integrações externas.

## Quando parar e perguntar

- Se a org já tiver Person Accounts habilitado antes deste hackathon.
- Se não existir repositório Git do projeto configurado (Prompt 00 não executado).
- Se algum nome de campo customizado sugerido já existir na org com finalidade diferente.

## Formato da entrega

- Lista de componentes criados (Record Types, campos, produtos).
- Confirmação de que os dados de exemplo foram carregados.
- Decisão de segurança registrada (OWD/Public Read-Write, sem sharing fino).
- Link do commit/push correspondente.
- Pendências ou riscos identificados.
