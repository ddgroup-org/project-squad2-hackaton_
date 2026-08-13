# Demanda atual

> Escreva aqui a descrição da tarefa a ser executada — pode ser um pedaço do backlog do Tarefai, uma pergunta nova do cliente, ou qualquer trabalho de implementação. Depois de escrever, rode `/executar-demanda NN` no Claude Code (NN = número sequencial, ex.: 01, 02...). Ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md).

## O que fazer

[Cromatta Química] - [Tarefa 10 - Service] Fila do Laboratório e Regras de Atribuição

**Contexto:** Quando uma amostra é reprovada, o Case gerado precisa ser direcionado automaticamente aos responsáveis técnicos certos (químicos Sérgio e André).

**Objetivo:** Criar a Fila do Laboratório no objeto Case e configurar a regra de atribuição automática/Flow para que Cases de amostras reprovadas caiam nessa fila.

**Descrição Detalhada:**
- Criar a Queue (Fila) "Fila do Laboratório" (`Fila_do_Laboratorio`) associada ao objeto Case.
- Adicionar os usuários químicos (Sérgio e André) como membros dessa Fila.
- Configurar Assignment Rule ou Flow para que todo Case gerado por motivo de Amostra Reprovada (ou com tipo de registro de amostra e status reprovado) seja atribuído automaticamente à Fila do Laboratório (`OwnerId` = Id da Fila).
- Garantir permissões para que os membros da fila consigam visualizar e assumir a propriedade dos Cases ("Assign to Me" / Assumir).

## Critério de aceite

- Fila do Laboratório criada com os químicos cadastrados como membros.
- Teste ponta a ponta via Apex: criar/reprovar uma amostra, verificar se o Case é gerado e se o proprietário (Owner) do Case é a Fila do Laboratório.

---

## Execução — registro (via Claude/CLI + Apex, org `hackaton2`)

**Status: concluída — sem novo metadata, por sobreposição total com demandas já executadas.**

1. **Descoberta antes de implementar:** ao investigar o estado da org antes de criar a Queue `Fila_do_Laboratorio` pedida no texto, encontrei que a Queue "Laboratório" (API name `Laboratorio`) já existe desde a demanda-02, com Sérgio e André como membros, e que o Flow `Amostra_Reprovada_Cria_Case` (demanda-09) já atribui automaticamente `Case.OwnerId` a essa fila sempre que uma Amostra é reprovada — já testado e funcionando desde então.
2. **Decisão (perguntada ao usuário, não presumida):** em vez de criar uma segunda fila com API name diferente (o que duplicaria a infraestrutura e criaria ambiguidade sobre qual fila é a "oficial"), reaproveitar a Queue `Laboratorio` já existente. Escolha confirmada explicitamente pelo usuário antes de qualquer alteração.
3. **Nenhum metadata novo foi necessário:**
   - Queue + membros: já existiam (demanda-02).
   - Atribuição automática de Case por amostra reprovada: já existia via Flow (demanda-09).
   - Permissão de "Assumir"/"Assign to Me": o Permission Set `Laboratorio` já concede `allowEdit=true` em Case desde a demanda-02 — isso já é suficiente para que um membro da fila assuma a propriedade de um Case pertencente à sua própria fila (comportamento padrão do Salesforce para registros de fila, sem exigir a permissão especial "Transfer Record"). O retrieve desta demanda também confirmou que o Case já tem a action padrão "Accept" disponível (`Case.object-meta.xml`, `actionOverrides` para `Accept`).
4. **Teste ponta a ponta via Apex (`sf apex run`, script não commitado), especificamente para esta demanda:** criada 1 Account + 1 Opportunity (Caminho B) + 1 Amostra Reprovada. Confirmado via SOQL: `Case.OwnerId` = Id da Queue Laboratório, `Owner.Type = 'Queue'`, `Owner.Name = 'Laboratório'`. Registros de teste removidos após validação.
5. **Achado crítico durante o retrieve (fora do escopo original desta demanda, mas corrigido nela):** o `sf project retrieve start` trouxe `sharingModel=Private` para Account, Opportunity e Case — divergente do `Read` (Public Read Only) configurado na demanda-02. Confirmado via Tooling API que o valor real na org também era `Private`, não um artefato do retrieve. Isso quebrava silenciosamente o requisito "vendedores veem todos os registros, mas só editam os próprios" (um Vendedor deixa de ver os registros dos colegas com OWD Private). Não foi esta sessão que alterou o OWD — origem não identificada (sem acesso a Setup Audit Trail). Perguntado ao usuário antes de agir; confirmado corrigir imediatamente. Restaurado `sharingModel=Read` via deploy de metadata nos 3 objetos (o deploy de Opportunity falhou uma vez com erro transitório de recálculo de sharing em andamento — resolvido na segunda tentativa) e confirmado novamente via Tooling API. Registrado como [ADR 0005](../../decisions/0005-owd-revertido-para-private-fora-do-fluxo.md).
6. **Retrieve final executado** conforme o fluxo (regra central 2 do `CLAUDE.md`) após a correção do OWD — refletindo o estado real corrigido da org antes do commit.
