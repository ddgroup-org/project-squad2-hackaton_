---
title: "Runbook — Hotfix emergencial"
description: "Procedimento para correção emergencial em Produção preservando branch, revisão, testes, rastreabilidade, Pull Request, rollback e validação pós-deploy."
category: "runbook"
status: "active"
version: "1.2"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - hotfix
  - incident
  - production
  - runbook
applies_to:
  - global
source_of_truth: false
source_references:
  - execucao.md
  - arquitetura.md
---

# Runbook — Hotfix emergencial

## Objetivo

Corrigir com urgência um problema em Produção **sem abandonar** branch, revisão, testes, rastreabilidade, Pull Request, rollback e validação pós-deploy.

## Princípio

**Hotfix não significa alteração manual e não rastreada em Produção.**

Urgência reduz o *tempo* de cada etapa e o *tamanho* do escopo. Não elimina etapa nenhuma. Uma correção não rastreada em Produção cria dois problemas: o original e a divergência permanente entre a org e o repositório — que reaparece no próximo deploy, sobrescrevendo a correção.

O que a urgência autoriza: escopo mínimo, revisão simultânea em vez de assíncrona, testes focados no defeito e nos processos afetados, documentação concisa. O que ela não autoriza: pular o Git, pular a revisão, pular o teste, pular o rollback.

## Quando utilizar

Defeito em Produção com impacto relevante — erro em processo crítico, perda ou corrupção de dados, indisponibilidade funcional, exposição indevida de dados ou falha de integração — que não pode aguardar o ciclo normal.

**Quando não utilizar:** melhoria, ajuste cosmético, correção sem impacto imediato, ou qualquer demanda que suporte o ciclo regular. Hotfix usado por conveniência erode o processo.

## Pré-condições

- [ ] Problema confirmado em Produção, com evidência.
- [ ] Impacto avaliado: processo afetado, usuários afetados, dados afetados.
- [ ] Criticidade que justifica o fluxo emergencial confirmada com o responsável.
- [ ] **Autorização explícita do Tech Lead ou do responsável pelo ambiente.**
- [ ] Causa identificada ou hipótese sustentada por evidência.

## Entradas

```text
{ID_INCIDENTE}      identificador do incidente
{HOTFIX_BRANCH}     branch da correção
{PROD_ORG_ALIAS}    org de Produção
{UAT_ORG_ALIAS}     org de validação
{COMMIT_HASH}       commit da correção
```

---

## Procedimento

### 1. Registrar o incidente

Antes de qualquer alteração:

```text
Data e hora da detecção
Sintoma observado
Evidência (log, print, relato, registro afetado)
Impacto: processo, usuários e dados
Criticidade
Responsável pela decisão de acionar o hotfix
```

Registrar no projeto atual, nunca nesta base global.

### 2. Diagnosticar em modo leitura

Investigar **sem alterar Produção**: consultar registros afetados, examinar logs, verificar metadata e histórico de deploy, identificar o que mudou recentemente.

**Ponto de decisão:** Produção é somente leitura por padrão. Nenhuma alteração de dados, metadata, permissão ou configuração é feita durante o diagnóstico.

Distinguir claramente **causa raiz**, **efeito observado**, **evidência confirmada** e **hipótese**. Não apresentar hipótese como fato.

### 3. Confirmar as orgs

```bash
sf org display --target-org {PROD_ORG_ALIAS}
sf org display --target-org {UAT_ORG_ALIAS}
```

Confirmar alias, username, Organization ID e tipo de ambiente das duas.

### 4. Criar a branch de hotfix a partir da branch-base de Produção

```bash
git checkout {PRODUCTION_BASE_BRANCH}
git pull --ff-only origin {PRODUCTION_BASE_BRANCH}
git log -1 --format=%H
git checkout -b {HOTFIX_BRANCH}
```

Registrar o hash como **commit-base do rollback**.

A branch parte da branch-base de **Produção** porque a correção precisa refletir o estado atual do ambiente produtivo — não o da linha de desenvolvimento, que contém trabalho não promovido. Confirmar o nome real dessa branch no projeto.

### 5. Implementar a correção mínima

**Escopo mínimo absoluto.** Corrigir o defeito, nada mais. Melhorias, refatorações e correções adjacentes ficam para o ciclo normal, registradas como recomendação.

**Ponto de decisão:** se a correção exigir alteração ampla, o hotfix provavelmente não é o caminho. Reavaliar com o Tech Lead: mitigação temporária agora e correção completa pelo ciclo regular pode ser a decisão mais segura.

### 6. Testar

Escopo reduzido, mas real:

- teste que **reproduz o defeito** e comprova a correção;
- testes dos processos diretamente afetados;
- cenário em massa, quando o defeito envolver volume;
- verificação de que a correção não introduz regressão nos processos vizinhos.

```bash
sf apex run test \
  --target-org {UAT_ORG_ALIAS} \
  --class-names {TEST_CLASS_NAME} \
  --result-format human \
  --wait 10
```

Reportar o **resultado real**. Teste não executado é registrado como tal, com o risco assumido explicitamente e por quem.

### 7. Validar em ambiente controlado

Aplicar a correção em UAT — ou no ambiente disponível mais próximo de Produção — e confirmar que o defeito foi resolvido.

**Ponto de decisão:** quando a urgência não permitir validação prévia completa, registrar explicitamente: qual validação foi omitida, qual risco permanece, quem aceitou esse risco e como validar imediatamente após o deploy. Essa decisão é do responsável pelo ambiente, não do executor.

### 8. Revisão de código

Revisão obrigatória, ainda que simultânea e conduzida por uma única pessoa. Foco: a correção resolve a causa; não introduz efeito colateral; não reduz controle de segurança; é reversível.

### 9. Verificar segredos

Inspecionar o diff. Correções feitas sob pressão são o cenário típico de credencial esquecida no código.

### 10. Pull Request para a branch-base de Produção

```bash
git push -u origin {HOTFIX_BRANCH}
```

**Push, abertura do PR e merge exigem autorização explícita**, mesmo em emergência.

Descrição conforme o [pull-request-production-template.md](../templates/pull-request-production-template.md), acrescentando: incidente, sintoma, causa identificada, evidência, escopo da correção, validações executadas e validações omitidas com o risco assumido.

### 11. Executar a pipeline de Produção

**Execução exige autorização explícita.** Acompanhar cada etapa.

Havendo falha parcial: interromper, identificar o que foi aplicado, verificar consistência, **não repetir automaticamente** e decidir entre concluir ou reverter — com autorização.

### 12. Validar imediatamente após o deploy

- o defeito não se reproduz mais;
- o processo afetado opera normalmente;
- processos vizinhos permanecem funcionais;
- não surgiram erros novos;
- os dados afetados durante o incidente foram avaliados.

**Ponto de decisão:** dados corrompidos durante o período do defeito exigem plano próprio de correção, com autorização específica. Deploy não corrige dado.

### 13. Propagar a correção para a linha de desenvolvimento

**Etapa frequentemente esquecida — e a causa clássica de regressão.**

A correção está na linha de Produção. Se não for propagada para `{DEVELOPMENT_BASE_BRANCH}`, a próxima promoção sobrescreve a correção e o defeito retorna a Produção.

Propagar conforme a política do projeto, com autorização, e confirmar que a correção está presente em ambas as linhas.

### 14. Registrar o encerramento

```text
Incidente e linha do tempo
Causa raiz confirmada ou hipótese remanescente
Correção aplicada e commits
Validações executadas e omitidas, com risco assumido e por quem
Resultado da validação pós-deploy
Dados afetados e tratamento aplicado
Propagação para developer confirmada
Ações preventivas recomendadas
Pendências
```

### 15. Ações preventivas

Registrar o que evita a recorrência: teste ausente que teria detectado o defeito, validação faltante na pipeline, lacuna de monitoramento, débito técnico relacionado. Essas ações entram no ciclo normal — não no hotfix.

---

## Evidências

Registro do incidente com evidência do sintoma; diagnóstico com distinção entre fato e hipótese; diff da correção; resultado real dos testes; evidência da validação em ambiente controlado; resultado da pipeline; evidência da validação pós-deploy; confirmação da propagação para a linha de desenvolvimento.

## Riscos

| Risco | Consequência | Mitigação |
| --- | --- | --- |
| Correção manual em Produção | divergência permanente entre org e repositório | correção sempre via branch e pipeline |
| Escopo ampliado sob pressão | novo defeito introduzido | escopo mínimo absoluto |
| Teste omitido | correção que não corrige ou que quebra outra coisa | teste que reproduz o defeito, no mínimo |
| Correção não propagada para a linha de desenvolvimento | regressão na próxima promoção | etapa 13 obrigatória |
| Causa não identificada | correção do sintoma, defeito retorna | distinguir causa de efeito |
| Rollback não planejado | indisponibilidade prolongada | plano definido antes do deploy |
| Dados corrompidos ignorados | inconsistência permanente | avaliar e tratar com plano próprio |

## Rollback

Definido **antes** do deploy:

1. redeploy da versão anterior a partir do commit-base registrado no passo 4;
2. reativação da versão anterior de Flows, quando aplicável;
3. reversão dos passos manuais executados;
4. repetição dos testes dos processos afetados;
5. comunicação aos envolvidos.

**Atenção:** reverter o hotfix restaura o defeito original. A decisão de reverter compara o impacto do defeito com o impacto da correção — e é do responsável pelo ambiente.

Efeitos não reversíveis por deploy: dados alterados, integrações acionadas, notificações enviadas.

## Critérios de conclusão

- [ ] Incidente registrado com evidência.
- [ ] Causa identificada, ou hipótese declarada como tal.
- [ ] Correção implementada em branch a partir da branch-base de Produção, com escopo mínimo.
- [ ] Testes executados com resultado real, ou omissão registrada com risco assumido.
- [ ] Revisão de código realizada.
- [ ] Nenhum segredo no diff.
- [ ] Pull Request aberto, aprovado e mesclado com autorização.
- [ ] Pipeline concluída.
- [ ] Validação pós-deploy concluída com evidências.
- [ ] Dados afetados avaliados.
- [ ] **Correção propagada para a linha de desenvolvimento.**
- [ ] Encerramento registrado com ações preventivas.

## Ações proibidas

**Alterar metadata, código, configuração ou dados diretamente em Produção**; corrigir sem branch, sem commit e sem Pull Request; pular revisão, testes ou validação pós-deploy sem registro explícito do risco e de quem o assumiu; ampliar o escopo além do defeito; deixar de propagar a correção para a linha de desenvolvimento; declarar o incidente encerrado sem validação; gravar artefatos na Salesforce-AI-Base.

## Referências

[promote-to-production.md](./promote-to-production.md) · [environment-safety.md](../knowledge/environment-safety.md) · [operational-safety-policy.md](../knowledge/operational-safety-policy.md) · [github-development-workflow.md](../knowledge/github-development-workflow.md) · [salesforce-development-principles.md](../knowledge/salesforce-development-principles.md) · [testing-standards.md](../knowledge/testing-standards.md) · [pull-request-production-template.md](../templates/pull-request-production-template.md)
