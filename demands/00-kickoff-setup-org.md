# Prompt 00 — Kickoff e setup da org (quimicahackaton)

## Contexto do projeto (ler antes de tudo)

- **Projeto:** hackathon de **1 dia** para construir, do zero, uma solução Salesforce em **Sales Cloud** e **Service Cloud**, atendendo dois modelos de cliente: **B2B** (empresas) e **B2C** (consumidores finais), no cenário de uma distribuidora do setor químico chamada **Quimtech Distribuidora Química Ltda.** (nome fictício — se você tiver recebido um nome/cenário real diferente deste, use o real e ignore o fictício).
- **Canal B2B:** vende insumos químicos a granel (solventes, ácidos, matérias-primas) para fábricas, laboratórios e indústrias. Ciclo de venda técnico, mais longo: cotação, ficha de segurança, negociação de volume/prazo, aprovação de desconto acima de um limite.
- **Canal B2C:** vende produtos de limpeza, piscina e jardim para consumidores finais. Ciclo de venda simples, rápido.
- **Seu papel:** Salesforce solution builder sênior, atuando **sozinho, sem supervisão em tempo real**. Quem está operando esta sessão pode não ser especialista Salesforce — não espere validação técnica dele; decida você mesmo dentro do que este prompt autoriza, e registre a decisão tomada.
- **Você não tem acesso a nenhum vault, repositório de conhecimento ou conversa anterior.** Tudo que você precisa para esta etapa está neste prompt. Se faltar informação essencial para prosseguir com segurança, **pare e pergunte** — não invente licença, dado de negócio ou API Name.
- **Prazo:** 1 dia inteiro de hackathon, e este é o **primeiro** de 7 prompts que serão executados em sequência ao longo do dia. Priorize velocidade seguindo processo — não precisa entregar tudo agora, apenas o setup.

## Objetivo deste prompt

Preparar o ambiente antes de qualquer configuração de negócio. Nenhum objeto, campo ou automação de negócio é criado neste prompt — apenas infraestrutura.

## Passo a passo

1. **Confirmar/criar a org:**
   - Se já existe uma org conectada, identifique: alias, username, Organization ID, tipo (Developer Edition, Trailhead Playground, Scratch Org, Sandbox, Produção) e instance URL.
   - **Se a org parecer de Produção real, ou contiver dados que pareçam de clientes reais (nomes de empresas reais, e-mails reais, volume de dados incompatível com uma org nova) — pare imediatamente e avise.** Este hackathon nunca deve tocar uma org de produção real.
   - Se não existe org, oriente e execute a criação de uma **Developer Edition** (signup gratuito) ou, se disponível, um **Scratch Org** a partir de um Dev Hub já autenticado. Não presuma que existe um Dev Hub disponível — confirme antes de tentar Scratch Org; se não houver, Developer Edition é o caminho padrão.

2. **Confirmar licenças/recursos disponíveis** (isso muda o que os próximos prompts poderão usar):
   - Service Cloud habilitado?
   - Omni-Channel disponível?
   - Knowledge habilitado?
   - Entitlements/Milestones disponível?
   - Path habilitado (Sales Path/Service Path)?
   - Registre o resultado — os próximos prompts pedirão essa informação.

3. **Criar o repositório do projeto Salesforce** (separado deste prompt, é um repositório novo, não um vault de notas):
   - Criar uma pasta de projeto local (ex: `quimicahackaton-org/`), fora de qualquer vault de documentação.
   - Inicializar como projeto SFDX: `sf project generate --name quimicahackaton-org` (ou equivalente da versão instalada do CLI).
   - `git init`, primeiro commit vazio ou com a estrutura gerada.
   - Autenticar a org: `sf org login web --alias quimica-hackathon --set-default` (ou fluxo equivalente).
   - Criar uma branch única de trabalho para o dia (ex: `hackathon`) — não há necessidade de modelo de branches complexo para uma execução solo de 1 dia.
   - **Se houver um repositório remoto já indicado para este projeto, configurá-lo como `origin` e fazer o primeiro push.** Se não houver, criar um repositório remoto (GitHub ou equivalente) e reportar a URL ao final — o tech lead deste projeto **não tem acesso à org** e só consegue revisar o trabalho através deste repositório.

4. **Registrar o resultado deste setup** em um arquivo `docs/00-setup.md` dentro do próprio repositório do projeto Salesforce (não neste prompt, no repositório novo), contendo: tipo de org, alias, Organization ID (pode registrar, não é segredo), licenças confirmadas, URL do repositório remoto, e qualquer limitação encontrada.

## Critérios de aceite

- [ ] Org confirmada como não-produção, com tipo e alias identificados.
- [ ] Licenças/recursos relevantes (Service Cloud, Omni-Channel, Knowledge, Entitlements, Path) verificados e registrados.
- [ ] Repositório Git do projeto criado, com estrutura SFDX válida, branch de trabalho criada, org autenticada como default.
- [ ] Repositório remoto configurado e primeiro push realizado — ou, se não foi possível, motivo registrado e reportado explicitamente.
- [ ] `docs/00-setup.md` criado no repositório do projeto com o resumo desta etapa.

## Fora de escopo deste prompt

- Qualquer objeto, campo, Record Type, Flow ou dado de negócio — isso começa no Prompt 01.
- Qualquer alteração em org que não seja a própria org do hackathon.

## Quando parar e perguntar

- Indício de que a org é de Produção real ou tem dados reais de clientes.
- Ausência de Dev Hub quando Scratch Org for a única opção viável e Developer Edition não servir por algum motivo não previsto aqui.
- Impossibilidade de criar ou acessar um repositório remoto — não prosseguir silenciosamente sem repositório, porque isso deixa o tech lead sem visibilidade nas próximas etapas.

## Formato da entrega (relate isso ao final)

- Tipo e alias da org, Organization ID, licenças confirmadas.
- URL do repositório remoto (ou motivo de não existir ainda).
- Qualquer limitação de licença que deva ser considerada nos próximos prompts (ex: "Knowledge não disponível nesta org").
- Pendências ou riscos identificados.
