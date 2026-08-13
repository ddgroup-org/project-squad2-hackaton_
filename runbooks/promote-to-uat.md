---
title: "Runbook — Promover para UAT"
description: "Procedimento para abrir o Pull Request da feature branch para developer, acompanhar a pipeline e validar a homologação em UAT."
category: "runbook"
status: "active"
version: "1.2"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - pull-request
  - uat
  - runbook
applies_to:
  - global
source_of_truth: false
source_references:
  - execucao.md
  - metaprompt-salesforce.md
---

# Runbook — Promover para UAT

## Objetivo

Levar a demanda concluída da branch de trabalho para a branch que alimenta o ambiente de homologação, com Pull Request completo, pipeline executada e homologação validada.

```text
{FEATURE_BRANCH} → {UAT_TARGET_BRANCH} → pipeline → homologação
```

> **Branches são placeholders.** Resolver `{DEVELOPMENT_BASE_BRANCH}`, `{UAT_TARGET_BRANCH}`, `{PRODUCTION_BASE_BRANCH}`, `{FEATURE_BRANCH}`, `{RELEASE_BRANCH}` e `{HOTFIX_BRANCH}` com os nomes reais do projeto antes de executar qualquer comando. O padrão `developer`/`main` é apenas fallback — ver [github-development-workflow.md](../knowledge/github-development-workflow.md#1-o-fluxo-do-projeto-vem-primeiro).


## Quando utilizar

Após a implementação estar concluída, testada e validada em DEV.

## Pré-condições

- [ ] Implementação concluída e validada em DEV.
- [ ] Testes executados com resultado real.
- [ ] Análise estática executada e apontamentos tratados.
- [ ] Diff revisado, limitado ao escopo da demanda.
- [ ] Nenhum segredo no diff.
- [ ] Plano de rollback definido.
- [ ] Autorização explícita para commit, push e abertura do Pull Request.

## Entradas

```text
{DEMANDA}           identificador e descrição
{FEATURE_BRANCH}    branch de origem
{UAT_TARGET_BRANCH}  branch de destino (fallback: developer)
{UAT_ORG_ALIAS}     org de homologação
{DEV_ORG_ALIAS}     org onde a implementação foi validada
```

---

## Procedimento

### 1. Revisar o conjunto a promover

```bash
git status
git branch --show-current
git log {UAT_TARGET_BRANCH}..{FEATURE_BRANCH} --oneline
git diff {UAT_TARGET_BRANCH}...{FEATURE_BRANCH} --stat
git diff {UAT_TARGET_BRANCH}...{FEATURE_BRANCH}
```

Verificar: todos os arquivos da demanda presentes; nenhum arquivo fora do escopo; ausência de arquivos temporários, de log ou de evidência; API Version inalterada, salvo quando for parte da demanda.

**Ponto de decisão:** arquivo fora do escopo interrompe o procedimento até ser removido ou justificado.

### 2. Verificar segredos

Inspecionar o diff completo. **Encontrando segredo, interromper antes de qualquer push**, remover o valor e tratar a credencial como comprometida.

### 3. Atualizar a base e avaliar conflitos

```bash
git fetch origin
git log {FEATURE_BRANCH}..origin/{UAT_TARGET_BRANCH} --oneline
```

**Ponto de decisão:** havendo commits novos na base, avaliar conflito potencial. A estratégia de atualização — merge ou rebase — segue a política do projeto. **Rebase exige autorização explícita.** Conflitos que envolvam trabalho de outra pessoa não devem ser resolvidos unilateralmente.

### 4. Commit

```bash
git add caminho/do/arquivo
git commit
```

Adicionar arquivos explicitamente, nunca com `.`. Mensagem conforme [naming-conventions.md](../knowledge/naming-conventions.md#12-commits), referenciando a demanda.

**Commit exige autorização explícita.**

### 5. Push

```bash
git push -u origin {FEATURE_BRANCH}
```

**Push exige autorização explícita e separada.** Nunca usar `--force` em branch compartilhada.

### 6. Preparar a descrição do Pull Request

Usar o [pull-request-uat-template.md](../templates/pull-request-uat-template.md), com: demanda, objetivo, resumo, componentes criados e alterados, decisão técnica, segurança, testes com resultado real, análise estática, evidências, dependências, riscos, instruções de UAT, rollback e checklist.

A skill [prepare-uat-pr](../.claude/skills/prepare-uat-pr/SKILL.md) produz esse conteúdo.

### 7. Abrir o Pull Request

**Abertura exige autorização explícita e separada.** Autorização para commit e push não autoriza abrir o PR.

Destino: `{UAT_TARGET_BRANCH}`. Origem: `{FEATURE_BRANCH}`.

### 8. Acompanhar a revisão de código

Responder aos apontamentos com alteração ou justificativa técnica. Ajustes solicitados na revisão seguem o mesmo ciclo: alterar, testar, revisar diff, commitar com autorização.

**Ponto de decisão:** apontamento de severidade crítica ou alta bloqueia o merge até ser tratado.

### 9. Acompanhar a pipeline

Verificar o resultado de cada etapa: validação, testes e deploy em UAT.

**Ponto de decisão:** falha de pipeline é bloqueio. Diagnosticar a causa real antes de qualquer nova tentativa. Não reexecutar repetidamente esperando resultado diferente.

Falha parcial de deploy exige o tratamento descrito em [operational-safety-policy.md](../knowledge/operational-safety-policy.md#8-tratamento-de-falhas-parciais).

### 10. Executar os passos manuais em UAT

Aplicar o que não é coberto por deploy: atribuição de Permission Set, registros de Custom Metadata, ativação de Flow na versão correta, Remote Site Settings, Named Credentials, agendamentos e ajustes de dados.

Registrar cada passo executado, com responsável e momento.

### 11. Confirmar o ambiente de homologação

```bash
sf org display --target-org {UAT_ORG_ALIAS}
```

Confirmar que a validação está sendo feita na org correta.

### 12. Homologar

Executar os cenários do plano de teste com os perfis previstos, coletando evidências: cenários positivos, negativos, de regressão e de segurança, conforme o plano.

Registrar, por cenário: resultado obtido, aderência ao esperado e evidência.

**Ponto de decisão:** divergência em relação aos critérios de aceite retorna a demanda ao ciclo de correção. Não ajustar diretamente em UAT — a correção segue o fluxo completo a partir da feature branch.

### 13. Obter a aprovação

Registrar a aprovação do Tech Lead e do responsável funcional, quando aplicável. Essa aprovação é pré-requisito da promoção a Produção.

### 14. Registrar as evidências

No projeto atual:

```text
Demanda, branch e commits
Pull Request e revisores
Resultado da pipeline
Componentes implantados em UAT
Passos manuais executados, com responsável
Cenários homologados e resultados
Evidências coletadas
Aprovação registrada
Pendências e riscos residuais
```

---

## Evidências

Diff consolidado; resultado real dos testes e da análise estática; resultado da pipeline; registro dos passos manuais; evidências de cada cenário homologado; registro da aprovação.

## Riscos

| Risco | Consequência | Mitigação |
| --- | --- | --- |
| Arquivo fora do escopo no PR | alteração indevida promovida | revisar diff integralmente |
| Segredo no diff | vazamento no repositório remoto | verificar antes do push |
| Passo manual esquecido | funcionalidade incompleta em UAT | mapear e registrar com responsável |
| Correção aplicada diretamente em UAT | divergência entre org e repositório | corrigir sempre a partir da branch |
| Falha de pipeline reexecutada sem diagnóstico | estado inconsistente | investigar a causa antes de repetir |
| Homologação sem evidência | promoção sem base para decisão | registrar cada cenário |

## Rollback

**Antes do merge:** fechar o Pull Request e manter a branch para retomada.

**Após o merge na branch de homologação:** avaliar com o Tech Lead entre reverter o merge e corrigir com nova entrega. Reversão de merge em branch compartilhada exige autorização explícita e comunicação ao time.

**No ambiente UAT:** redeploy da versão anterior a partir do commit-base; reativação da versão anterior de Flows; reversão dos passos manuais executados. Dados alterados durante a homologação não são revertidos por deploy.

## Critérios de conclusão

- [ ] Diff revisado e limitado ao escopo.
- [ ] Nenhum segredo promovido.
- [ ] Commit, push e abertura do PR com autorização explícita.
- [ ] Descrição do PR completa.
- [ ] Revisão de código concluída, com apontamentos tratados.
- [ ] Pipeline concluída com sucesso.
- [ ] Passos manuais executados e registrados.
- [ ] Cenários homologados com evidências.
- [ ] Aprovação do Tech Lead registrada.
- [ ] Evidências salvas no projeto.

## Ações proibidas

Executar commit, push, abertura de PR ou merge sem autorização explícita; `git push --force` em branch compartilhada; corrigir defeito diretamente na org de UAT; promover para Produção conteúdo não homologado; declarar homologação concluída sem evidências; gravar artefatos na Salesforce-AI-Base.

## Referências

[github-development-workflow.md](../knowledge/github-development-workflow.md) · [operational-safety-policy.md](../knowledge/operational-safety-policy.md) · [environment-safety.md](../knowledge/environment-safety.md) · [testing-standards.md](../knowledge/testing-standards.md) · [retrieve-and-deploy-policy.md](../knowledge/retrieve-and-deploy-policy.md) · [pull-request-uat-template.md](../templates/pull-request-uat-template.md) · Skill: [prepare-uat-pr](../.claude/skills/prepare-uat-pr/SKILL.md) · [promote-to-production.md](./promote-to-production.md)
