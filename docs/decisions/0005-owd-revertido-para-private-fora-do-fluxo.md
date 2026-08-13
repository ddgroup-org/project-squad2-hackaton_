---
title: "ADR 0005 — OWD de Account/Opportunity/Case revertido para Private fora do fluxo Claude"
category: "decision"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# ADR 0005 — OWD de Account/Opportunity/Case revertido para Private fora do fluxo Claude

## Contexto

Durante a execução da demanda-10 (Fila do Laboratório), o `sf project retrieve start --manifest manifest/package.xml` trouxe `sharingModel=Private` para Account, Opportunity e Case — divergente do `sharingModel=Read` (Public Read Only) configurado na demanda-02 e confirmado repetidamente em demandas posteriores (05, 08, 09) via `EntityDefinition.InternalSharingModel`.

Confirmado via Tooling API (`SELECT QualifiedApiName, InternalSharingModel FROM EntityDefinition`) que o valor real na org também era `Private` — não foi um artefato do retrieve, o OWD tinha sido de fato alterado na org.

Esta sessão (Claude) não fez essa alteração. Não foi identificada a origem exata (candidatos: ação manual na UI do Setup, alteração por outra sessão/pessoa, ou efeito colateral de alguma operação na org) — sem acesso a Setup Audit Trail neste momento para confirmar autoria.

## Problema

`architecture.md`/`business-scenario.md` exigem, como requisito de negócio confirmado com o cliente: "vendedores veem todos os registros, mas só editam os próprios". Esse comportamento depende diretamente do OWD Public Read Only nesses 3 objetos (ver seção "Segurança e acessos" de `architecture.md`) — com `Private`, um Vendedor deixa de ver os registros dos colegas, quebrando um critério de aceite já validado (demanda-02) silenciosamente.

## Decisão

**Restaurar `sharingModel=Read` (Public Read Only) em Account, Opportunity e Case**, via deploy de metadata (não manual na UI), replicando exatamente a configuração já decidida e validada nas demandas anteriores. Feito durante a execução da demanda-10, com confirmação explícita do usuário antes de agir (ver `evidencias/demandas/demanda-10.md`).

- O deploy de Opportunity falhou na primeira tentativa com o erro transitório "The sharing calculation you requested can't be processed right now" (recalculo de sharing anterior ainda em andamento) — resolvido com uma segunda tentativa após breve espera, sem intervenção manual.
- Nenhum dado de Account/Opportunity/Case foi perdido; a correção é apenas de configuração de compartilhamento.

## Consequências

- Reforça a regra central 4 do `CLAUDE.md` ("validar também via MCP/Tooling API, não só pela CLI") — esta divergência só foi percebida porque o diff pós-retrieve foi revisado antes do commit, e não aceito às cegas.
- Fica registrado que o OWD desses 3 objetos é uma configuração sensível e já foi alterada fora do fluxo Claude uma vez (após a demanda-09, antes da demanda-10) — recomenda-se que qualquer sessão futura confirme o OWD real via Tooling API antes de assumir que o estado do repositório reflete o estado da org, especialmente após um intervalo sem execução de demandas.
- Se uma alteração de OWD for intencional no futuro (ex.: mudança de requisito de negócio), deve vir acompanhada de uma nova demanda/ADR explícita — não deve ser feita silenciosamente na UI.

## Alternativas descartadas

| Alternativa | Por que foi descartada |
| --- | --- |
| Não corrigir agora, só documentar como pendência | O usuário confirmou explicitamente que a correção deveria ser feita imediatamente, já que a divergência quebra um requisito de negócio já validado — deixar a org inconsistente com o design documentado por mais tempo não trazia benefício. |
| Investigar a causa raiz antes de corrigir | Sem acesso a Setup Audit Trail nesta sessão; a correção declarativa é idempotente e de baixo risco, então não há necessidade de bloquear a correção à espera de uma investigação que pode não ser conclusiva. |
