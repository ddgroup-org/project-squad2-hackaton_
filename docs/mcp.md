---
title: "MCP (Salesforce DX MCP Server) — quimicahackaton"
category: "guide"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# MCP neste repositório

Este repositório tem o **Salesforce DX MCP Server** oficial (`@salesforce/mcp`) configurado em [`.mcp.json`](../.mcp.json), na raiz. Ele dá ao Claude ferramentas para consultar e validar a org diretamente (SOQL, metadata, testes), além do que já é feito via `sf` CLI.

## O que está habilitado

- **Toolsets:** `orgs`, `metadata`, `data`, `users`, `testing`, `code-analysis`.
- **Org:** `DEFAULT_TARGET_ORG` — resolve dinamicamente para o org default configurado **localmente**, na máquina de cada dev, não um alias fixo. Cada pessoa que clonar este repositório precisa ter seu próprio org autorizado e marcado como default (ver abaixo).
- **`--allow-non-ga-tools`:** algumas ferramentas úteis dos toolsets acima ainda não são GA — habilitado deliberadamente para o hackathon.

## Setup necessário para cada dev (isso NÃO fica salvo no repositório)

1. Ter o Salesforce CLI instalado (`sf`).
2. Autorizar a org do hackathon localmente e marcar como default (alias em uso: `hackaton2`):
   ```
   sf org login web --alias hackaton2 --set-default
   ```
3. Abrir este repositório no Claude Code. Na primeira vez, o Claude Code vai pedir aprovação para rodar o servidor MCP declarado em `.mcp.json` — isso é uma proteção de segurança do próprio Claude Code (roda `npx @salesforce/mcp`, então precisa de confirmação explícita), aprovar uma vez é suficiente.
4. Node.js precisa estar disponível no PATH (o `.mcp.json` usa `npx -y @salesforce/mcp`, que baixa/executa o pacote automaticamente — não precisa instalar nada manualmente).

## Regra de uso — validar também via MCP

Além de tudo via Claude/IA (regra central do projeto, ver [`CLAUDE.md`](../CLAUDE.md)), **decisões e implementações devem ser validadas também pelas ferramentas de MCP**, não só pela CLI:

- `run_soql_query` (toolset `data`) — para confirmar que os dados/registros realmente existem como esperado na org.
- Ferramentas do toolset `metadata` — para confirmar o que foi de fato deployado, comparando com o que `demanda.md`/`architecture.md` pediram.
- Ferramentas do toolset `testing` — para rodar testes Apex/LWC quando existirem.

Isso evita declarar uma demanda como concluída só porque um comando `sf` não retornou erro — o MCP permite checar o estado real da org de outro ângulo antes de arquivar a evidência em `evidencias/`.
