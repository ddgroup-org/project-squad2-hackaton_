---
title: "quimicahackaton — Cofre do projeto"
description: "Cofre individual de planejamento para o hackathon Salesforce Sales Cloud + Service Cloud, B2B e B2C, setor químico."
category: "index"
status: "active"
version: "1.1"
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

Cofre individual de planejamento para o hackathon **quimicahackaton**: uma solução Salesforce cobrindo **Sales Cloud** e **Service Cloud**, para clientes **B2B** e **B2C**, no cenário de uma empresa do setor químico. Duração do hackathon: **1 dia**.

**Este repositório reúne duas coisas no mesmo lugar:** o planejamento (contexto, decisões) **e** o projeto Salesforce DX em si (`sfdx-project.json`, `force-app/`, `config/`, `manifest/`), que será populado pela execução real.

Inspirado nas convenções da base global [Salesforce-AI-Base](../Salesforce-AI-Base/README.md), mas **não é um substituto dela nem uma cópia**: aqui vive apenas o que é específico deste projeto/evento.

---

## Como este projeto funciona

```text
Tech lead                                  Dev executor (outra pessoa)
─────────────────                          ───────────────────────────
Sem acesso à org                            Com acesso à org Salesforce
Usa este repositório para planejar          Roda o Claude Code neste mesmo
e manter o documento de requisitos          repositório, populando force-app/
                                             conforme executa o trabalho

        documento de requisitos (a ser adicionado)
                    │
                    ▼
        dev executa, valida na org
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
├── .claude/
│   └── agents/                            cópia fiel dos 7 agentes da Salesforce-AI-Base — ver nota abaixo
└── docs/
    ├── project-context.md                 objetivo do hackathon, papéis, restrições, critérios de sucesso
    ├── business-scenario.md               cenário fictício da empresa química, B2B e B2C — AJUSTÁVEL
    ├── architecture.md                    clouds, modelo de dados, decisões técnicas de alto nível
    └── decisions/
        ├── README.md
        └── 0001-modelo-conta-b2b-b2c-sem-person-accounts.md
```

Além disso, na raiz, o **projeto Salesforce DX** (mesmo repositório, gerado via `sf project generate`):

```text
quimicahackaton/
├── sfdx-project.json
├── force-app/main/default/                metadata da org — populada durante a execução
├── config/project-scratch-def.json
├── manifest/package.xml
├── scripts/                                apex/soql de apoio
└── package.json, .forceignore, .gitignore, .vscode/, etc. — tooling padrão SFDX
```

---

## Agentes (.claude/agents/)

Cópia literal dos 7 agentes da [Salesforce-AI-Base](../Salesforce-AI-Base/.claude/agents/) (`salesforce-developer`, `salesforce-architect`, `apex-code-reviewer`, `lwc-code-reviewer`, `flow-reviewer`, `security-reviewer`, `deployment-reviewer`), copiados sem alteração — a base de origem não foi tocada.

**Limitação conhecida:** cada agente referencia internamente `../../knowledge/*.md` e `../../templates/*.md`, pastas que **não existem** neste cofre. Quando um agente tentar consultar esses arquivos numa sessão que rodar aqui, vai encontrar um caminho inexistente — isso não bloqueia a execução, apenas empobrece o agente em relação à versão completa da base. Se isso incomodar, a solução é trazer `knowledge/` também (deliberadamente adiado).

Por ora, **skills** (`start-salesforce-demand`, `review-apex`, etc.) não foram copiadas — só agentes, por instrução explícita. Podem ser adicionadas depois, se fizer falta.

## Publicação (GitHub)

- **Repositório:** [github.com/inaldojunior-a11y/Squad2-Cromatta-quimica](https://github.com/inaldojunior-a11y/Squad2-Cromatta-quimica)
- **Visibilidade:** público — o conteúdo aqui é só planejamento e um cenário fictício, sem segredo real.
- **Estrutura:** unificada — planejamento, decisões e o projeto Salesforce DX (`force-app/`, `sfdx-project.json`, `manifest/`) vivem no mesmo repositório e histórico Git, para que o tech lead revise tudo em um único lugar.
- Contexto de negócio ainda fictício e rotulado como tal em `business-scenario.md` — ajustar se o desafio real for definido.

---

## Premissa assumida — revisar antes de começar a execução

Como o desafio de negócio real não foi detalhado, este cofre assume um **cenário fictício rotulado como tal**: uma distribuidora química vendendo insumos a granel para empresas (B2B) e produtos de limpeza/piscina/jardim para consumidores finais (B2C). Está em [docs/business-scenario.md](docs/business-scenario.md).

**Se o hackathon já tem uma empresa/desafio real definido, ajustar `business-scenario.md` antes de começar.**

Da mesma forma, a org ainda não existe — nenhum dado de ambiente real foi presumido além de "Developer Edition, Trailhead Playground ou Scratch Org, nunca produção".

---

## Uso no Obsidian

Abrir esta pasta como vault (**Open folder as vault**) funciona normalmente — é Markdown com front matter, sem configuração especial. Ao contrário da Salesforce-AI-Base, este cofre **é editável**: é o espaço de trabalho ativo do hackathon, não uma base de conhecimento somente leitura.

## Manutenção

- Registrar aqui qualquer desvio relevante da execução.
- Ao final do hackathon, registrar o resultado da demo (o repositório já é este mesmo).
