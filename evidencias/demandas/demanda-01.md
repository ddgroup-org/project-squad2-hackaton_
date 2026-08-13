> **Status: PENDENTE DE EXECUÇÃO.** Este texto foi commitado por Paulo Carvalho (commit `acbf03c`, "Salva demanda 01: Solution Design + Data Mapping da Cromatta Química") como conteúdo de `demanda.md`, mas a execução via `/executar-demanda 01` não aconteceu: não há entrada correspondente em `evidencias/log.md`, nem PDF `02_Solution_Design_Cromatta_Quimica_Squad02.pdf` em `entregaveis/`. Arquivado aqui (sem marcar como concluído) para não perder o texto ao sobrepor `demanda.md` com a Demanda 02, que foi solicitada para execução imediata.

---

# Demanda atual — 01

> Ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md) para o fluxo. Depois de revisar este arquivo, rodar `/executar-demanda 01`.

## Contexto

Antes de configurar via Claude, o time precisa de um desenho técnico único para não haver retrabalho.

## Objetivo

Produzir o PDF `02_Solution_Design_Cromatta_Quimica_Squad02.pdf`, incluindo o Data Mapping, para orientar todos os prompts do Claude nas tarefas seguintes.

## O que fazer

1. **Diagrama de objetos:** Lead → Account/Contact/Opportunity → Product2/PricebookEntry → objeto customizado Amostra → Case (Laboratório/Pós-venda).
2. **Data Mapping campo a campo:** de onde vem cada informação levantada na reunião (ex.: origem do lead, linha de produto, motivo de perda, causa técnica de reprovação) e em qual objeto/campo ela será armazenada.
3. **Security Model:** Organization-Wide Default, regras de compartilhamento e Permission Sets (detalhar o que foi implementado na Tarefa 02).
4. **Automações previstas:** Approval Process (aprovação de preço), Flow/Assignment Rule (fila do laboratório), regra de alerta (concentração de receita), Entitlement/SLA (prazos de resposta).
5. **Seção "Uso do Claude por etapa":** como cada parte da arquitetura será construída via prompt (referência para o documento de evidências).

## Critérios de aceite

- [ ] Diagrama de objetos e Data Mapping completos e revisados.
- [ ] Modelo de segurança documentado e compatível com o que foi implementado na Tarefa 02.

## Notas para quem for executar

- **Fontes a usar como base** (não redescobrir do zero): `architecture.md` (modelo de dados, segurança, automações — já cobre os itens 1, 3 e 4 em nível de design), `business-scenario.md` (regras de negócio/origem de cada informação, para o Data Mapping do item 2), `decisions/0001-*.md` e `decisions/0002-*.md` (justificativas de decisões que o Solution Design deve refletir).
- **Verificar "Tarefa 02" antes de documentá-la como feita.** Hoje não há nenhuma demanda registrada em `evidencias/log.md` nem metadata de PermissionSet/sharing rule commitada em `force-app/main/default/permissionsets` (pasta vazia) — ou seja, o Security Model parece ainda não ter sido implementado neste repositório. Não presumir que "Tarefa 02" já existe: checar `evidencias/log.md`, `force-app/` e, via MCP, o estado real da org antes de escrever essa seção. Se não estiver implementado, documentar o modelo **especificado** em `architecture.md` (OWD Public Read Only + Permission Sets Vendedor/Químico/Gestor) deixando explícito que é design pendente de implementação, e reportar essa lacuna ao final em vez de seguir em silêncio.
- **Formato de saída:** PDF com o nome exato `02_Solution_Design_Cromatta_Quimica_Squad02.pdf`. Sugestão de local: uma pasta `entregaveis/` na raiz (novo, ao lado de `imgs/` e `evidencias/`) — ou outro local, desde que documentado no log de evidência. Gerar PDF pode exigir ferramenta externa (ex.: pandoc, conversão de Markdown/HTML para PDF); confirmar disponibilidade antes de assumir que é possível, e se não houver caminho viável no ambiente, reportar em vez de simular/pular a etapa.
