---
title: "quimicahackaton — Instruções para sessão de IA neste cofre"
category: "instructions"
status: "active"
version: "1.3"
last_reviewed: "2026-08-27"
owner: "Tech lead"
applies_to:
  - quimicahackaton
source_of_truth: true
---

# quimicahackaton — instruções para quem trabalhar neste cofre

Este arquivo vale para uma sessão de IA aberta **dentro desta pasta** (`~/Desktop/cromatta`), ajudando o tech lead a planejar e executar.

## O que esta pasta é

Planejamento e execução de um hackathon Salesforce de 1 dia (Sales Cloud + Service Cloud) para o cliente simulado **Cromatta Química** (cenário REAL, não fictício). Ver [docs/project-context.md](docs/project-context.md), [docs/business-scenario.md](docs/business-scenario.md) e a transcrição completa da reunião de requisitos em [docs/transcricao.md](docs/transcricao.md).

Nesta mesma pasta/repositório (`SQUAD_02_HACKATON_DDGROUP_2026`) convivem:

- **Planejamento:** este arquivo, `project-context.md`, `business-scenario.md`, `architecture.md`, `decisions/` (e as cópias em `docs/`).
- **Projeto Salesforce DX:** `sfdx-project.json`, `force-app/`, `config/`, `manifest/`, `scripts/` — estrutura gerada via `sf project generate`, pronta para receber a metadata da execução.
- **Execução de demandas + evidência:** `demanda.md` (tarefa atual), `.claude/commands/executar-demanda.md` (comando `/executar-demanda`), `evidencias/` (log + demandas arquivadas + prints).
- **MCP:** `.mcp.json` (Salesforce DX MCP Server) — ver [docs/mcp.md](docs/mcp.md).
- **Agentes, skills, conhecimento técnico e templates** copiados da Salesforce-AI-Base: `.claude/agents/`, `.claude/skills/`, `knowledge/`, `runbooks/`, `templates/` — ver seção "Recursos copiados da Salesforce-AI-Base" abaixo.
- **Documentos corporativos (PDF):** `templates/documento-corporativo-cromatta.html` — ver [docs/como-gerar-documentos.md](docs/como-gerar-documentos.md).

O trabalho é guiado pelos documentos de requisitos deste repositório: o **BRD oficial** (`entregaveis/01_BRD_Cromatta_Quimica_Squad02.pdf`, aprovado pelo cliente e pelo tech lead) é a fonte de verdade mais recente; `business-scenario.md` + `architecture.md` (derivados de `docs/transcricao.md`) são o resumo estruturado de apoio, atualizados para acompanhar o BRD onde há divergência. Não há mais prompts autocontidos separados em `demands/` (descontinuado). No lugar disso, cada unidade de trabalho é uma "demanda" local (ver seção "Fluxo de trabalho" abaixo).

## O que esta pasta não é

- Não é a Salesforce-AI-Base — não duplicar conteúdo de lá; referenciar por caminho relativo quando fizer sentido (`../Salesforce-AI-Base/...`).
- Não substitui a leitura da Salesforce-AI-Base para padrões técnicos gerais; este repositório guarda apenas o que é específico deste evento.

## Regras centrais deste projeto

1. **Tudo via Claude/IA — nunca configuração manual na UI do Salesforce, como padrão.** Essa é a regra de maior peso na avaliação do hackathon (25% da nota, ver `project-context.md`).
   - **Exceção explícita:** o que não for possível fazer via Claude, pode ser feito direto na org. A exceção é sobre viabilidade técnica (ex.: algo que a ferramenta não suporta), não sobre preferência ou economia de tempo — antes de ir para a UI, tentar de fato via Claude primeiro.
   - Quando usar a exceção, registrar o que foi feito manualmente e por quê (uma nota ou ADR) — nunca fazer silenciosamente, senão o tech lead (sem acesso à org) não tem como saber que aquilo não veio do fluxo padrão.
2. **Antes de qualquer `git push`: retrieve da org + pull do GitHub, sempre nessa ordem, para não perder nada.** `sf project retrieve start` (ou equivalente) primeiro, para a metadata commitada refletir o estado real da org; depois `git pull` (ou `git pull --rebase`) para trazer o que outros devs já enviaram ao remoto, antes de commitar e só então dar push. Nunca commitar/dar push às cegas sem os dois passos. Sem isso, o tech lead (sem acesso à org) acaba revisando um histórico que pode não corresponder à realidade, ou o push de alguém sobrescreve o trabalho de outra pessoa.
3. **Não presumir requisito de negócio não confirmado.** Os documentos de requisitos (`business-scenario.md`, `architecture.md`) já cobrem o que foi levantado com o cliente; qualquer requisito ambíguo ou não coberto ali é uma pendência a confirmar (ver seção "Pendências abertas" em `project-context.md`), não uma suposição a preencher silenciosamente.
4. **Validar decisões e implementações também via MCP.** Este repositório tem o Salesforce DX MCP Server configurado em `.mcp.json` (ver [docs/mcp.md](docs/mcp.md)). Antes de considerar uma demanda concluída, usar as ferramentas de MCP para confirmar o estado real da org — `run_soql_query` para checar dados, o toolset `metadata` para confirmar o que foi de fato deployado, `testing` para rodar testes — não validar só porque um comando `sf` não retornou erro.

## Fluxo de trabalho neste cofre

1. Se surgir informação nova do cliente, atualizar `docs/business-scenario.md` (e a cópia na raiz) e, se for uma decisão estrutural relevante, registrar como ADR em `decisions/`.
2. Unidade de trabalho = **demanda**: escrever a tarefa em `demanda.md` e rodar `/executar-demanda NN` — ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md). Isso já cobre os passos 3–4 abaixo automaticamente (retrieve antes do push, arquivamento da demanda, log de evidência).
3. Implementar com base em `business-scenario.md` + `architecture.md` — toda automação/config via Claude (regra central 1).
4. Antes de cada `git push`: `sf project retrieve start`, depois `git pull`, revisar o diff, comitar, só então dar push (regra central 2).
5. Registrar decisões arquiteturais relevantes em `decisions/` (ADR) e desvios de execução onde fizer sentido.

## Evidência de uso do Claude/IA

Critério de 25% da nota (ver `project-context.md`). O fluxo `/executar-demanda` (item 2 acima) já gera evidência automaticamente em `evidencias/log.md` e `evidencias/demandas/`. Para uma captura de tela deliberada da org/execução, usar `scripts/capturar-print.sh <rótulo>` — nunca automático, porque o repositório é público (ver `evidencias/README.md`).

## Recursos copiados da Salesforce-AI-Base

Para não recriar do zero o que a base global já resolve bem, foram copiados (não referenciados por caminho relativo, para funcionar mesmo fora da máquina de quem tem a Salesforce-AI-Base clonada):

- `.claude/agents/` — os 7 agentes de revisão (salesforce-developer, salesforce-architect, apex-code-reviewer, lwc-code-reviewer, flow-reviewer, security-reviewer, deployment-reviewer). **Uso obrigatório por demanda:** `/executar-demanda` roteia para o agente certo por tipo de conteúdo — ver tabela em `.claude/commands/executar-demanda.md`.
- `.claude/skills/` — `review-apex`, `review-lwc`, `start-salesforce-demand`, `salesforce-preflight-check`, `validate-change-scope`.
- `knowledge/` — padrões técnicos (Apex, Flow, LWC, testes, nomenclatura, segurança) que os agentes/skills acima referenciam internamente.
- `runbooks/` — recuperação de operações Git/metadata que deram errado.
- `templates/` — modelo genérico de análise técnica e templates de Pull Request da base (referência; o modelo de documento deste projeto é `documento-corporativo-cromatta.html`, não estes).

**Precedência — importante:** o projeto adotou o modelo multiambiente da [ADR 0007](decisions/0007-cicd-multiambiente-com-fila-segura.md): `feature/*` e `hotfix/*` promovem exclusivamente para `developer`/HML; Produção recebe exclusivamente PR `developer` → `main`. Gates de deploy, destructive changes e merge são humanos e separados, conforme [docs/ci-cd.md](docs/ci-cd.md) e as políticas em `knowledge/`. O fluxo `demanda.md` → `/executar-demanda` continua sendo a regra local de execução e evidência; para entrega remota, ele é seguido pelo fluxo de Pull Request e promoção da ADR. Onde um padrão global divergir desses nomes ou deste desenho, prevalece a decisão específica do projeto, sem reduzir as regras globais de segurança (mesmo princípio de `knowledge/instruction-precedence.md`: regra do projeto pode adaptar processo, nunca remover controles inegociáveis).

## Onde salvar o que for produzido durante o hackathon

Documentação técnica real do projeto Salesforce (metadata, manifests, evidências, package.xml) vive **neste mesmo repositório**, dentro de `force-app/`, `manifest/` e `config/` — não em um repositório separado.
