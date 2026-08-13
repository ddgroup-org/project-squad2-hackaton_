---
title: "Como executar demandas — quimicahackaton"
category: "guide"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# Como executar demandas

Fluxo simples para trabalhar neste repositório com o Claude Code, gerando automaticamente evidência de uso do Claude (critério de 25% da nota — ver [project-context.md](project-context.md)).

## Por que isso é mais simples do que o modelo antigo

O cofre tinha originalmente um modelo de **prompts autocontidos** em `demands/`, pensado para serem copiados e colados numa sessão *separada*, sem nenhum contexto do cofre. Isso foi descontinuado: agora o planejamento (`business-scenario.md`, `architecture.md`) e a execução (`force-app/`, a org autorizada) vivem na mesma pasta e, normalmente, na mesma sessão do Claude Code — não há mais necessidade de repetir todo o contexto em cada tarefa.

## Passo a passo

1. **Escreva a tarefa em [`demanda.md`](../demanda.md)** (raiz do repositório) — sobrescreva o conteúdo anterior. Pode ser um item do backlog do Tarefai, uma dúvida respondida pelo cliente, um ajuste pedido — qualquer unidade de trabalho.
2. **No Claude Code, dentro desta pasta, rode:**
   ```
   /executar-demanda 01
   ```
   Troque `01` pelo próximo número sequencial (consulte [`evidencias/log.md`](../evidencias/log.md) para ver qual foi o último).
3. O Claude vai:
   - Ler `demanda.md` e implementar o que foi pedido, sempre via Claude/IA (regra central do projeto — configuração manual só se comprovadamente inviável, e registrada).
   - Rodar `sf project retrieve start` antes de dar qualquer push, para a metadata commitada refletir a org real.
   - Arquivar o `demanda.md` executado em `evidencias/demandas/demanda-01.md`.
   - Acrescentar uma linha em `evidencias/log.md` com o resumo do que foi pedido e do que foi feito.
   - Comitar e dar push de tudo.
4. **Opcional — evidência visual:** se quiser um print da org/execução como evidência, rode manualmente:
   ```
   scripts/capturar-print.sh nome-do-print
   ```
   Isso tira um screenshot da tela inteira e salva em `evidencias/prints/`. É manual (não roda dentro do `/executar-demanda`) porque o repositório é **público** — confira o conteúdo antes de commitar, para não expor algo fora do escopo do hackathon.

## Se a demanda não estiver clara

O Claude vai parar e perguntar em vez de assumir, se `demanda.md` estiver vago, incompleto, ou tocar em algo não coberto por `business-scenario.md`/`architecture.md`. Isso é intencional — não presumir requisito de negócio é uma das regras centrais deste projeto (ver `CLAUDE.md`).

## Onde ver o histórico

- [`evidencias/log.md`](../evidencias/log.md) — uma linha por demanda executada.
- [`evidencias/demandas/`](../evidencias/demandas/) — o texto de cada demanda, como foi escrito.
- `git log` — o histórico real de commits/pushes, correlacionado ao log de evidências pelo hash do commit.
