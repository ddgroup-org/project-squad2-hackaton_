---
description: Executa a tarefa descrita em demanda.md e registra evidência de uso do Claude
---

Você vai executar a demanda descrita no arquivo `demanda.md` (raiz deste repositório). Número/rótulo desta demanda: $ARGUMENTS — use isso para nomear a evidência; se vier vazio, olhe `evidencias/log.md` e use o próximo número da sequência.

## Antes de começar

1. Leia `demanda.md` por completo. Se estiver vazio ou não fizer sentido como tarefa, pare e peça para o usuário preencher antes de continuar — não invente a tarefa.
2. Tenha em mente as regras centrais deste projeto (`CLAUDE.md`): tudo via Claude/IA como padrão (configuração manual só se comprovadamente inviável, e registrada); sempre `sf project retrieve start` antes de qualquer `git push`; não presumir requisito de negócio não confirmado — o que estiver em `business-scenario.md`/`architecture.md` é o que já foi levantado com o cliente, o resto é pendência a confirmar; validar também via MCP (ver `docs/mcp.md`), não só pela CLI.
3. Se a tarefa tocar em algo não coberto por `business-scenario.md`/`architecture.md` e não estiver claro em `demanda.md`, pare e pergunte em vez de assumir.

## Execução

Implemente exatamente o que `demanda.md` pede, seguindo a ordem de preferência declarativa (config → Flow → Approval Process → Apex/LWC só se necessário) descrita em `architecture.md`.

## Roteamento de agentes especialistas (obrigatório)

Este repositório tem 7 agentes copiados em `.claude/agents/` (ver `CLAUDE.md`). Acionar via Agent tool o(s) agente(s) que corresponde(m) ao **tipo de conteúdo da demanda**, sempre antes do passo de validação final — não pular esta etapa só porque "parece simples":

| Conteúdo da demanda | Agente |
| --- | --- |
| Decisão arquitetural, modelo de dados, Solution Design, avaliação de alternativas | `salesforce-architect` |
| Implementação em si (analisar/projetar/codar a demanda) | `salesforce-developer` |
| Classe/trigger Apex criado ou alterado | `apex-code-reviewer` |
| Lightning Web Component criado ou alterado | `lwc-code-reviewer` |
| Flow / automação declarativa criada ou alterada | `flow-reviewer` |
| Qualquer alteração que toque CRUD/FLS/sharing/Permission Set/credenciais | `security-reviewer` |
| Empacotamento final antes de um push maior (não há UAT/Produção aqui, mas serve para revisar o conjunto de metadata antes de subir) | `deployment-reviewer` |

Uma demanda pode acionar mais de um agente (ex.: `flow-reviewer` + `security-reviewer` se o Flow tocar em dados sensíveis). Se nenhum se aplicar claramente, registrar por quê e seguir sem agente.

## Ao final

1. **Valide via MCP também**, não só pela CLI: use as ferramentas do Salesforce DX MCP Server (toolset `data` — ex. `run_soql_query` — e toolset `metadata`) para confirmar que o que foi implementado realmente está na org, condizente com o que `demanda.md` pediu. Se algo não bater, corrija antes de seguir para o commit.
2. Antes do `git push`, sempre nesta ordem: `sf project retrieve start --manifest manifest/package.xml` (ajuste/amplie o manifest primeiro se a demanda criou tipos de metadata que ele ainda não lista — ex.: CustomObject, Flow, PermissionSet), depois `git pull` — para não perder nada que outro dev já tenha enviado ao remoto.
3. Aplique o checklist de `.claude/skills/validate-change-scope/SKILL.md` (adaptado: sem branch/PR, só compare `git status`/`git diff` com o que a demanda pedia) antes de commitar — nada fora do escopo, nenhum segredo, nenhum arquivo temporário.
4. Arquive o conteúdo atual de `demanda.md` em `evidencias/demandas/demanda-$ARGUMENTS.md` (crie a pasta `evidencias/demandas/` se não existir).
5. Acrescente uma linha em `evidencias/log.md` (tabela existente) com: data, número da demanda, resumo do que foi pedido, resumo do que foi feito, e o hash do commit (preencha o hash depois de commitar).
6. Comite e dê push de tudo — metadata retrieved + evidência arquivada + log atualizado.
7. Se a demanda gerar um documento/entregável em PDF, usar o modelo em `templates/documento-corporativo-cromatta.html` (ver [docs/como-gerar-documentos.md](../../docs/como-gerar-documentos.md)) — nunca um estilo novo.
8. Avise o usuário, ao final, que ele pode rodar `scripts/capturar-print.sh <rótulo>` manualmente se quiser um screenshot da org/execução como evidência visual — isso não é feito automaticamente porque vai para um repositório público e precisa ser deliberado (ver aviso em `evidencias/README.md`).
