---
title: "Runbook — Promover para Produção"
description: "Procedimento para criar a branch de release a partir da main, aplicar apenas os commits homologados, abrir o Pull Request de Produção e validar após o deploy."
category: "runbook"
status: "active"
version: "1.2"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - release
  - production
  - runbook
applies_to:
  - global
source_of_truth: false
source_references:
  - execucao.md
  - metaprompt-salesforce.md
---

# Runbook — Promover para Produção

## Objetivo

Promover para Produção exatamente o conteúdo homologado, pela estratégia de promoção definida pelo projeto, com Pull Request próprio, pipeline de Produção e validação pós-deploy.

```text
{PRODUCTION_BASE_BRANCH} atualizada → {RELEASE_BRANCH} → conteúdo homologado → PR para {PRODUCTION_BASE_BRANCH} → pipeline → Produção → validação
```

> **Branches são placeholders.** Resolver `{DEVELOPMENT_BASE_BRANCH}`, `{UAT_TARGET_BRANCH}`, `{PRODUCTION_BASE_BRANCH}`, `{FEATURE_BRANCH}`, `{RELEASE_BRANCH}` e `{HOTFIX_BRANCH}` com os nomes reais do projeto antes de executar qualquer comando. O padrão `developer`/`main` é apenas fallback — ver [github-development-workflow.md](../knowledge/github-development-workflow.md#1-o-fluxo-do-projeto-vem-primeiro).

**Este runbook descreve a estratégia de fallback (release branch + cherry-pick).** Se o projeto usar merge controlado, promotion branches ou promoção por versão de pacote, seguir a estratégia do projeto: os passos 2 e 3 mudam, os controles das seções 4 a 7 permanecem.

## Quando utilizar

Após a homologação em UAT concluída e aprovada pelo Tech Lead.

## Pré-condições — nenhuma etapa prossegue sem confirmar

- [ ] **Homologação em UAT concluída**, com evidências disponíveis.
- [ ] **Aprovação do Tech Lead** registrada.
- [ ] **Commits homologados identificados**, com hashes.
- [ ] **Dependências entre commits mapeadas.**
- [ ] **Nenhuma alteração não aprovada** no conjunto a promover.
- [ ] **Plano de rollback definido e executável.**
- [ ] **Plano de validação pós-deploy definido.**
- [ ] **Janela de implantação acordada**, quando o projeto exigir.
- [ ] **Autorização explícita e separada** para push, abertura do PR e execução da pipeline.

Qualquer item não confirmado **interrompe o procedimento**.

## Entradas

```text
{DEMANDA}           identificador e descrição
{PR_UAT}            Pull Request de UAT correspondente
{RELEASE_BRANCH}    branch de release
{COMMIT_HASH}       commits homologados
{PROD_ORG_ALIAS}    org de Produção
{MANIFEST_PATH}     manifest da promoção, quando houver
```

---

## Procedimento

### 1. Atualizar a branch-base de Produção

```bash
git checkout {PRODUCTION_BASE_BRANCH}
git pull --ff-only origin {PRODUCTION_BASE_BRANCH}
git log -1 --format=%H
```

Registrar o hash como **commit-base do rollback**.

**Ponto de decisão:** falha de `--ff-only` indica divergência local na branch-base. Investigar antes de prosseguir — nunca resolver com reset.

### 2. Criar a branch de release a partir dela

```bash
git checkout -b {RELEASE_BRANCH}
```

**Uma branch de desenvolvimento não deve ser promovida diretamente para Produção** quando contiver trabalho de outras demandas ainda não homologado. Esse é o risco que a branch de release isola.

### 3. Aplicar apenas o conteúdo homologado

```bash
git cherry-pick {COMMIT_HASH}
```

**Cherry-pick exige autorização explícita e é uma estratégia possível, não obrigatória.** Se o projeto adotar outra, aplicá-la e pular para o passo 4 — a verificação de equivalência é que não é opcional.

**Ponto de decisão — quando NÃO usar cherry-pick:**

- os commits homologados dependem de commits não homologados;
- há muitos commits entrelaçados na mesma área de código;
- a metadata foi alterada por várias demandas em paralelo;
- a resolução manual de conflitos é extensa a ponto de comprometer a equivalência com o homologado.

Em qualquer desses casos, **interromper** e alinhar a estratégia com o responsável técnico: promover o conjunto completo, adotar merge controlado, reorganizar os commits na origem, promover por versão de pacote ou reimplementar de forma isolada.

Conflito durante o cherry-pick: resolver apenas o que pertence ao escopo, sem descartar trabalho de terceiros, e registrar cada resolução. Cherry-pick interrompido é falha parcial — diagnosticar antes de continuar.

### 4. Verificar a equivalência com o homologado

**Este é o passo central do runbook.**

```bash
git diff {PRODUCTION_BASE_BRANCH}...{RELEASE_BRANCH} --stat
git diff {PRODUCTION_BASE_BRANCH}...{RELEASE_BRANCH}
git log {PRODUCTION_BASE_BRANCH}..{RELEASE_BRANCH} --oneline
```

Confirmar, componente a componente:

- todos os componentes homologados estão presentes;
- nenhum componente adicional foi incluído;
- as diferenças resultantes de resolução de conflito estão identificadas e justificadas;
- nenhuma alteração de comportamento foi introduzida durante a preparação.

**Ponto de decisão:** diferença não justificada entre o homologado e o promovido é **bloqueio absoluto**. O que vai para Produção precisa ser o que foi testado.

### 5. Validar dependências em Produção

Para cada componente promovido, confirmar que suas dependências existem em Produção ou estão incluídas na promoção: campos referenciados, classes chamadas, Custom Metadata consumida, Record Types, permissões, Named Credentials e configurações de integração.

**Ponto de decisão:** dependência ausente causa falha de deploy ou comportamento incorreto. Não prosseguir sem resolver.

### 6. Verificar segredos

Inspecionar o diff completo quanto a valores reais de token, senha, client secret, chave privada ou certificado.

**Encontrando segredo:** interromper antes de qualquer push, remover o valor e tratar a credencial como comprometida.

### 7. Confirmar a org de Produção

```bash
sf org list
sf org display --target-org {PROD_ORG_ALIAS}
```

Confirmar alias, username, Organization ID, instance URL e tipo de ambiente. Alias isolado não é identificação suficiente.

**Produção é somente leitura por padrão.** Nenhuma escrita manual, em nenhuma circunstância, fora da pipeline autorizada.

### 8. Executar a validação sem deploy, quando autorizada

```bash
sf project deploy validate \
  --manifest {MANIFEST_PATH} \
  --target-org {PROD_ORG_ALIAS} \
  --test-level {TEST_LEVEL}
```

A validação **não** aplica alterações. Ainda assim exige autorização e confirmação prévia da org.

**Ponto de decisão:** falha na validação interrompe a promoção. Corrigir a causa e reiniciar o ciclo — a correção passa novamente por homologação.

### 9. Definir a ordem de deploy e os passos manuais

- **pré-deploy** — configurações que precisam existir antes;
- **deploy** — componentes e ordem, quando fracionado;
- **pós-deploy** — atribuição de Permission Set, registros de Custom Metadata, ativação de Flow na versão correta, Remote Site Settings, Named Credentials, agendamentos e ajustes de dados.

Cada passo com responsável e momento definidos.

### 10. Push e abertura do Pull Request

```bash
git push -u origin {RELEASE_BRANCH}
```

**Push e abertura do Pull Request exigem autorizações explícitas e separadas.**

Destino: `{PRODUCTION_BASE_BRANCH}`. Origem: `{RELEASE_BRANCH}`. Descrição conforme o [pull-request-production-template.md](../templates/pull-request-production-template.md), referenciando o Pull Request de UAT.

A skill [prepare-production-pr](../.claude/skills/prepare-production-pr/SKILL.md) produz esse conteúdo.

### 11. Revisão e aprovação do Pull Request

Aguardar revisão e aprovação formal. Merge exige autorização explícita.

### 12. Executar a pipeline de Produção

**Execução da pipeline exige autorização explícita e separada.**

Acompanhar cada etapa. **Ponto de decisão:** falha na pipeline interrompe a promoção. Havendo falha parcial de deploy, aplicar o tratamento de falha parcial: identificar o que foi aplicado, verificar consistência, **não repetir automaticamente**, e decidir entre concluir ou reverter com autorização.

### 13. Executar os passos manuais pós-deploy

Aplicar na ordem definida, registrando cada passo com responsável e momento.

Confirmar especificamente: versão ativa de cada Flow implantado; Permission Sets atribuídos; registros de Custom Metadata presentes; configurações de integração operantes.

### 14. Validar após o deploy

Executar os cenários críticos definidos no plano de validação pós-deploy e registrar as evidências.

Verificar: funcionalidades entregues operando conforme os critérios de aceite; processos existentes preservados; integrações funcionando; ausência de erros novos no período de monitoramento definido.

**Ponto de decisão:** comportamento divergente do esperado aciona a avaliação de rollback. A decisão de reverter é do responsável definido, não automática.

### 15. Registrar as evidências

No projeto atual:

```text
Data, hora e janela de implantação
Demanda, PR de UAT e PR de Produção
Commits promovidos
Commit-base do rollback
Org: alias, username, Organization ID
Resultado da validação
Resultado da pipeline
Componentes implantados
Passos manuais executados, com responsável
Cenários validados após o deploy e resultados
Erros observados no monitoramento
Pendências e riscos residuais
```

---

## Evidências

Comparação entre o conteúdo homologado e o promovido; referência ao PR de UAT e às evidências de homologação; registro da aprovação do Tech Lead; resultado da validação e da pipeline; registro dos passos manuais; evidências da validação pós-deploy.

## Riscos

| Risco | Consequência | Mitigação |
| --- | --- | --- |
| Conteúdo divergente do homologado | comportamento não testado em Produção | verificação de equivalência obrigatória |
| Commit dependente promovido sem sua base | falha de deploy ou comportamento incorreto | mapear dependências antes do cherry-pick |
| Dependência ausente em Produção | falha de deploy | validar dependências previamente |
| Passo manual esquecido | funcionalidade incompleta | mapear com responsável e conferir após o deploy |
| Falha parcial de deploy | org em estado inconsistente | interromper, diagnosticar, decidir com autorização |
| Rollback não planejado | indisponibilidade prolongada | plano definido antes da promoção |
| Promoção a partir de branch de desenvolvimento | trabalho não homologado em Produção | isolar o conteúdo homologado pela estratégia do projeto |
| Segredo promovido | vazamento em repositório e ambiente produtivo | verificar antes do push |

## Rollback

Planejado **antes** da promoção:

1. **Código e metadata versionados** — redeploy da versão anterior a partir do commit-base registrado no passo 1.
2. **Flows** — reativar a versão anterior, registrada antes da promoção.
3. **Permissões** — reverter atribuições realizadas no pós-deploy.
4. **Custom Metadata** — reverter ou remover registros criados, conforme o impacto.
5. **Repetir os testes** dos processos afetados.
6. **Comunicar** o rollback aos envolvidos e registrar a decisão.

**Efeitos não reversíveis automaticamente:** dados alterados ou criados, integrações acionadas, notificações enviadas, pacotes instalados e configurações em sistemas externos. Cada um exige plano específico, definido antes da promoção.

Reversão em Produção exige autorização explícita, da mesma forma que a promoção.

## Critérios de conclusão

- [ ] Todas as pré-condições confirmadas.
- [ ] Estratégia de promoção do projeto confirmada e aplicada.
- [ ] Branch de release criada a partir da branch-base de Produção atualizada, quando essa for a estratégia.
- [ ] Somente commits homologados aplicados.
- [ ] Equivalência com o homologado confirmada.
- [ ] Dependências satisfeitas em Produção.
- [ ] Nenhum segredo promovido.
- [ ] Validação executada, quando autorizada.
- [ ] Pull Request aprovado.
- [ ] Pipeline concluída sem falha pendente.
- [ ] Passos manuais executados e conferidos.
- [ ] Validação pós-deploy concluída com evidências.
- [ ] Evidências registradas no projeto.

## Ações proibidas

**Deploy direto em Produção fora da pipeline autorizada**; qualquer alteração manual de metadata, dados ou configuração em Produção; push, abertura de PR, merge, cherry-pick ou execução de pipeline sem autorização explícita; promover conteúdo não homologado; promover conteúdo que não passou pela homologação; declarar sucesso sem validação pós-deploy; gravar artefatos na Salesforce-AI-Base.

## Referências

[github-development-workflow.md](../knowledge/github-development-workflow.md) · [environment-safety.md](../knowledge/environment-safety.md) · [operational-safety-policy.md](../knowledge/operational-safety-policy.md) · [retrieve-and-deploy-policy.md](../knowledge/retrieve-and-deploy-policy.md) · [testing-standards.md](../knowledge/testing-standards.md) · [salesforce-development-principles.md](../knowledge/salesforce-development-principles.md) · [pull-request-production-template.md](../templates/pull-request-production-template.md) · Skill: [prepare-production-pr](../.claude/skills/prepare-production-pr/SKILL.md) · [emergency-hotfix.md](./emergency-hotfix.md)
