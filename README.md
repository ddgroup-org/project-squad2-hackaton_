---
title: "quimicahackaton — Cofre do projeto"
description: "Cofre individual de planejamento para o hackathon Salesforce Sales Cloud + Service Cloud, cliente Cromatta Química."
category: "index"
status: "active"
version: "1.2"
last_reviewed: "2026-08-13"
owner: "Tech lead"
tags:
  - salesforce
  - hackathon
  - sales-cloud
  - service-cloud
  - b2b
  - b2c
applies_to:
  - quimicahackaton
source_of_truth: true
---

# quimicahackaton

Cofre individual de planejamento para o hackathon **quimicahackaton**: uma solução Salesforce cobrindo **Sales Cloud** e **Service Cloud**, para o cliente simulado **Cromatta Química** (indústria química — clientes PJ e PF). Duração do hackathon: **1 dia**.

**Este repositório reúne duas coisas no mesmo lugar:** o planejamento (contexto, requisitos, decisões) **e** o projeto Salesforce DX em si (`sfdx-project.json`, `force-app/`, `config/`, `manifest/`), que será populado pela execução real.

Inspirado nas convenções da base global [Salesforce-AI-Base](../Salesforce-AI-Base/README.md), mas **não é um substituto dela nem uma cópia**: aqui vive apenas o que é específico deste projeto/evento.

---

## Como este projeto funciona

```text
Tech lead                                  Dev executor (outra pessoa)
─────────────────                          ───────────────────────────
Sem acesso à org                            Com acesso à org Salesforce
Usa este repositório para planejar          Roda o Claude Code neste mesmo
e manter os requisitos atualizados          repositório, populando force-app/
                                             conforme executa o trabalho

        business-scenario.md + architecture.md
        (requisitos, derivados de docs/transcricao.md)
                    │
                    ▼
        escrever a tarefa em demanda.md → rodar /executar-demanda NN
                    │
                    ▼
        dev executa — regra de ouro: tudo via Claude/IA,
        nenhuma configuração manual na UI do Salesforce
                    │
                    ▼
        sf project retrieve start (sempre antes de dar push)
                    │
                    ▼
        commit + push neste mesmo repositório (force-app/, manifest/, config/)
                    │
                    ▼
        Tech lead revisa pelo Git (não pela org)
```

Como o tech lead **não tem acesso à org**, a única forma de revisão é este mesmo repositório Git, onde o dev faz commit/push da metadata a cada etapa. **Antes de qualquer push, sempre fazer retrieve primeiro** — sem isso, o histórico commitado pode não refletir o estado real da org.

---

## Estrutura

```text
quimicahackaton/
├── README.md                              este arquivo
├── CLAUDE.md                              instruções para uma sessão de IA aberta *neste* cofre
├── demanda.md                             tarefa atual a ser executada (ver "Como executar uma demanda")
├── .claude/
│   ├── agents/                            cópia fiel dos 7 agentes da Salesforce-AI-Base — ver nota abaixo
│   └── commands/executar-demanda.md       comando `/executar-demanda`
├── evidencias/                             evidência de uso do Claude/IA (25% da nota)
│   ├── README.md
│   ├── log.md                             uma linha por demanda executada
│   ├── demandas/                           demanda.md arquivado a cada execução
│   └── prints/                             screenshots (manuais, via scripts/capturar-print.sh)
└── docs/
    ├── project-context.md                 objetivo do hackathon, papéis, critérios de avaliação, entregáveis
    ├── business-scenario.md               cenário REAL do cliente (Cromatta Química) — resumo estruturado
    ├── transcricao.md                     transcrição condensada da reunião de levantamento de requisitos
    ├── architecture.md                    clouds, modelo de dados, segurança, automações
    ├── como-executar-demandas.md          fluxo passo a passo de demanda.md → /executar-demanda
    └── decisions/
        ├── README.md
        ├── 0001-modelo-conta-b2b-b2c-sem-person-accounts.md
        └── 0002-sem-integracao-erp-precificacao-v1.md
```

Além disso, na raiz, o **projeto Salesforce DX** (mesmo repositório, gerado via `sf project generate`) e a pasta `imgs/` (assets de branding da Cromatta):

```text
quimicahackaton/
├── sfdx-project.json
├── force-app/main/default/                metadata da org — populada durante a execução
├── config/project-scratch-def.json
├── manifest/package.xml
├── scripts/
│   └── capturar-print.sh                  screenshot manual para evidencias/prints/
├── imgs/                                   logos, paleta de cores, moodboard da marca Cromatta
└── package.json, .forceignore, .gitignore, .vscode/, etc. — tooling padrão SFDX
```

---

## Agentes (.claude/agents/)

Cópia literal dos 7 agentes da [Salesforce-AI-Base](../Salesforce-AI-Base/.claude/agents/) (`salesforce-developer`, `salesforce-architect`, `apex-code-reviewer`, `lwc-code-reviewer`, `flow-reviewer`, `security-reviewer`, `deployment-reviewer`), copiados sem alteração — a base de origem não foi tocada.

**Limitação conhecida:** cada agente referencia internamente `../../knowledge/*.md` e `../../templates/*.md`, pastas que **não existem** neste cofre. Quando um agente tentar consultar esses arquivos numa sessão que rodar aqui, vai encontrar um caminho inexistente — isso não bloqueia a execução, apenas empobrece o agente em relação à versão completa da base. Se isso incomodar, a solução é trazer `knowledge/` também (deliberadamente adiado).

Por ora, **skills** (`start-salesforce-demand`, `review-apex`, etc.) não foram copiadas — só agentes, por instrução explícita. Podem ser adicionadas depois, se fizer falta.

## Publicação (GitHub)

- **Repositório:** [github.com/inaldojunior-a11y/SQUAD_02_HACKATON_DDGROUP_2026](https://github.com/inaldojunior-a11y/SQUAD_02_HACKATON_DDGROUP_2026)
- **Visibilidade:** público — o conteúdo é o levantamento de requisitos de um cliente simulado (role-play) do hackathon, não dados reais de produção.
- **Estrutura:** unificada — planejamento, requisitos, decisões e o projeto Salesforce DX (`force-app/`, `sfdx-project.json`, `manifest/`) vivem no mesmo repositório e histórico Git, para que o tech lead revise tudo em um único lugar.

---

## Requisitos do cliente — onde estão

O desafio de negócio **já é real** (não mais uma suposição fictícia): foi levantado em reunião de kickoff com o cliente simulado do hackathon.

- **Resumo estruturado, pronto para uso na implementação:** [docs/business-scenario.md](docs/business-scenario.md) e [docs/architecture.md](docs/architecture.md).
- **Fonte completa (transcrição condensada por tema):** [docs/transcricao.md](docs/transcricao.md) — usar quando o resumo estruturado parecer incompleto ou ambíguo.
- **Org:** já autorizada (alias `cromatta-hackathon`), dedicada ao hackathon.

---

## Como executar uma demanda

1. Escreva a tarefa em [`demanda.md`](demanda.md).
2. Rode `/executar-demanda NN` no Claude Code, dentro desta pasta.
3. Evidência (log + demanda arquivada) é gerada automaticamente; screenshot é manual, via `scripts/capturar-print.sh`.

Passo a passo completo: [docs/como-executar-demandas.md](docs/como-executar-demandas.md).

---

## Uso no Obsidian

Abrir esta pasta como vault (**Open folder as vault**) funciona normalmente — é Markdown com front matter, sem configuração especial. Ao contrário da Salesforce-AI-Base, este cofre **é editável**: é o espaço de trabalho ativo do hackathon, não uma base de conhecimento somente leitura.

## Manutenção

- Registrar aqui qualquer desvio relevante da execução.
- Ao final do hackathon, registrar o resultado da demo (o repositório já é este mesmo).
