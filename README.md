---
title: "quimicahackaton — Cofre do projeto"
description: "Cofre individual de planejamento para o hackathon Salesforce Sales Cloud + Service Cloud, B2B e B2C, setor químico."
category: "index"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Paulo Carvalho"
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

**Este cofre não é o projeto Salesforce em si.** Ele não contém metadata, código nem a org. Ele contém o **planejamento, as decisões e os prompts** que serão enviados para uma sessão separada do Claude Code — operada por outra pessoa, com acesso à org — que fará a execução real.

Inspirado nas convenções da base global [Salesforce-AI-Base](../Salesforce-AI-Base/README.md), mas **não é um substituto dela nem uma cópia**: aqui vive apenas o que é específico deste projeto/evento.

---

## Como este projeto funciona

```text
Paulo (tech lead)                          Dev executor (outra pessoa)
─────────────────                          ───────────────────────────
Sem acesso à org                            Com acesso à org Salesforce
Usa este cofre para planejar                Roda o Claude Code em sessão própria,
e escrever os prompts                       sem acesso a este cofre nem à
                                             Salesforce-AI-Base

        docs/demands/00 → 06 (prompts autocontidos)
                    │
                    ▼
        copiar o prompt da vez, colar na sessão do dev
                    │
                    ▼
        dev executa, valida na org, faz retrieve + commit/push
        no repositório Git do projeto Salesforce (separado deste cofre)
                    │
                    ▼
        Paulo revisa pelo Git (não pela org) e ajusta o próximo prompt
        se algo precisar mudar
```

Como Paulo **não tem acesso à org**, a única forma de revisão é o repositório Git do projeto Salesforce que o dev cria no Prompt 00. **Sem commit e push regulares, o trabalho é invisível para o tech lead** — por isso essa exigência está em todos os prompts.

Cada prompt em `docs/demands/` é **autocontido**: repete o contexto necessário, porque a sessão que o executa não tem acesso a este cofre, à Salesforce-AI-Base, nem a prompts anteriores (pode ser uma sessão nova a cada etapa).

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
    ├── decisions/
    │   ├── README.md
    │   └── 0001-modelo-conta-b2b-b2c-sem-person-accounts.md
    └── demands/
        ├── README.md                      ordem de execução e como usar os prompts
        ├── 00-kickoff-setup-org.md
        ├── 01-modelo-de-dados.md
        ├── 02-sales-cloud.md
        ├── 03-service-cloud.md
        ├── 04-automacao-cross-cloud.md
        ├── 05-relatorios-dashboards.md
        └── 06-demo-pitch.md
```

---

## Agentes (.claude/agents/)

Cópia literal dos 7 agentes da [Salesforce-AI-Base](../Salesforce-AI-Base/.claude/agents/) (`salesforce-developer`, `salesforce-architect`, `apex-code-reviewer`, `lwc-code-reviewer`, `flow-reviewer`, `security-reviewer`, `deployment-reviewer`), copiados sem alteração — a base de origem não foi tocada.

**Limitação conhecida:** cada agente referencia internamente `../../knowledge/*.md` e `../../templates/*.md`, pastas que **não existem** neste cofre (escopo atual é só prompts + agentes). Quando um agente tentar consultar esses arquivos numa sessão que rodar aqui, vai encontrar um caminho inexistente — os padrões técnicos relevantes já foram condensados diretamente em cada prompt de `docs/demands/`, então isso não bloqueia a execução, apenas empobrece o agente em relação à versão completa da base. Se isso incomodar, a solução é trazer `knowledge/` também (deliberadamente adiado).

Por ora, **skills** (`start-salesforce-demand`, `review-apex`, etc.) não foram copiadas — só agentes, por instrução explícita. Podem ser adicionadas depois, se fizer falta.

## Plano de publicação (GitHub)

Decisão registrada, ainda não executada:

- **Visibilidade:** público — o conteúdo aqui é só planejamento e um cenário fictício, sem segredo real.
- **Estrutura final:** unificar este cofre com o repositório do projeto Salesforce (prompts + agentes + metadata no mesmo histórico), para que o tech lead revise tudo em um único lugar. **Adiado por decisão explícita** — por enquanto o cofre contém só prompts e agentes; a unificação com `force-app/` (metadata SFDX) acontece depois, quando o dev iniciar a execução.
- Antes do push: mais contexto de negócio será acrescentado (o cenário atual em `business-scenario.md` é fictício e rotulado como tal).

---

## Premissa assumida — revisar antes de enviar o primeiro prompt

Como o desafio de negócio real não foi detalhado, este cofre assume um **cenário fictício rotulado como tal**: uma distribuidora química vendendo insumos a granel para empresas (B2B) e produtos de limpeza/piscina/jardim para consumidores finais (B2C). Está em [docs/business-scenario.md](docs/business-scenario.md).

**Se o hackathon já tem uma empresa/desafio real definido, ajustar `business-scenario.md` antes de enviar qualquer prompt** — os prompts referenciam esse cenário diretamente.

Da mesma forma, a org ainda não existe (será criada no Prompt 00) — nenhum dado de ambiente real foi presumido além de "Developer Edition, Trailhead Playground ou Scratch Org, nunca produção".

---

## Uso no Obsidian

Abrir esta pasta como vault (**Open folder as vault**) funciona normalmente — é Markdown com front matter, sem configuração especial. Ao contrário da Salesforce-AI-Base, este cofre **é editável**: é o espaço de trabalho ativo do hackathon, não uma base de conhecimento somente leitura.

## Manutenção

- Atualizar `docs/demands/README.md` com o status de cada prompt (enviado, em execução, concluído, bloqueado) conforme o dia avança.
- Registrar aqui qualquer desvio relevante que o dev reportar de volta, antes de escrever o próximo prompt.
- Ao final do hackathon, registrar o link do repositório Git do projeto Salesforce e o resultado da demo.
