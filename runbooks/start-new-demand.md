---
title: "Runbook — Iniciar uma nova demanda"
description: "Procedimento operacional para iniciar uma demanda Salesforce com ambiente confirmado, estado inicial registrado e plano aprovado."
category: "runbook"
status: "active"
version: "1.2"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - git
  - runbook
  - onboarding-demanda
applies_to:
  - global
source_of_truth: false
source_references:
  - execucao.md
  - metaprompt-salesforce.md
---

# Runbook — Iniciar uma nova demanda

## Objetivo

Preparar o início de uma demanda Salesforce com branch correta, org confirmada, estado inicial registrado e plano de implementação aprovado.

## Quando utilizar

Sempre que uma nova demanda for iniciada, antes de qualquer alteração de código ou metadata.

## Pré-condições

- demanda descrita, com critérios de aceite ou expectativa clara;
- projeto identificado e acessível;
- acesso de leitura ao repositório e, quando aplicável, à org DEV.

## Entradas

```text
{DEMANDA}          identificador e descrição
{PROJECT_ROOT}     caminho absoluto do projeto
{DEVELOPMENT_BASE_BRANCH}  branch-base do projeto (fallback: developer)
{FEATURE_BRANCH}   branch da demanda
{DEV_ORG_ALIAS}    alias da org de desenvolvimento
```

## Verificações iniciais

- [ ] `CLAUDE.md`, `AGENTS.md` e `README.md` do projeto lidos.
- [ ] Diretório de trabalho é o esperado.
- [ ] Repositório Git válido, sem operação incompleta.
- [ ] Existência de alterações locais preexistentes verificada.

---

## Procedimento

### 1. Confirmar o projeto

```bash
pwd
ls -la
cat sfdx-project.json
```

Registrar: caminho absoluto, package directories, API Version e modelo de desenvolvimento.

**Ponto de decisão:** se não houver `sfdx-project.json`, confirmar se o diretório é realmente a raiz do projeto Salesforce antes de prosseguir.

### 2. Verificar o estado do Git

```bash
git status
git branch --show-current
git log --oneline -10
git remote -v
```

**Ponto de decisão:** havendo arquivos modificados ou não rastreados, identificar a origem antes de continuar.

- pertencem a esta demanda → prosseguir;
- pertencem a outra demanda ou a outra pessoa → **preservar** e solicitar orientação;
- origem desconhecida → não descartar; registrar e perguntar.

Nunca executar `git reset --hard`, `git checkout -- .`, `git restore .` ou `git clean -fd` para "limpar" o ambiente.

### 3. Atualizar a branch-base

```bash
git checkout {DEVELOPMENT_BASE_BRANCH}
git pull --ff-only origin {DEVELOPMENT_BASE_BRANCH}
```

**Ponto de decisão:** se `--ff-only` falhar, existe divergência entre a base local e o remoto. Investigar a origem — não resolver com reset nem com merge automático.

### 4. Criar a branch da demanda

```bash
git checkout -b {FEATURE_BRANCH}
git log -1 --format=%H
```

Registrar o hash como **commit-base** do rollback. Nome da branch conforme [naming-conventions.md](../knowledge/naming-conventions.md#11-branches).

### 5. Confirmar a org DEV

```bash
sf org list
sf org display --target-org {DEV_ORG_ALIAS}
```

Registrar: alias, username, Organization ID, instance URL, tipo de ambiente, status de autenticação e API Version.

**Ponto de decisão:** alias isolado não confirma a org. Havendo qualquer indicação de Produção — `IsSandbox = false`, alias com `prod`, domínio produtivo, documentação divergente — **interromper**. Na dúvida, tratar como Produção.

### 6. Investigar a demanda

Sem alterar nada:

- localizar no repositório os componentes possivelmente envolvidos;
- confirmar API Names reais por metadata, consulta ou ferramenta;
- verificar se já existe solução total ou parcial;
- mapear dependências: objetos, campos, automações, classes, componentes, permissões e integrações;
- levantar as automações do objeto afetado e o momento em que executam;
- identificar testes existentes;
- verificar licenciamento quando a solução puder depender de feature licenciada.

**Ponto de decisão:** a ausência de um componente no repositório local **não** prova que ele não existe. Confirmar na org antes de concluir.

### 7. Retrieve direcionado, quando necessário

```bash
sf project retrieve start \
  --metadata {METADATA_TYPE}:{COMPONENT_NAME} \
  --target-org {DEV_ORG_ALIAS}
```

```bash
git status
git diff
```

Revisar cada diferença. Descartar do escopo o que não pertence à demanda. Detalhes em [retrieve-and-deploy-policy.md](../knowledge/retrieve-and-deploy-policy.md).

### 8. Registrar o estado inicial

Salvar no **projeto atual** (por exemplo, em `{PROJECT_ROOT}/docs/demands/`):

```text
Data e hora
Projeto e caminho absoluto
Branch-base e commit-base (hash)
Feature branch criada
Org: alias, username, Organization ID, tipo de ambiente
Arquivos modificados preexistentes
Componentes relacionados identificados
Automações existentes no objeto afetado
Testes existentes relacionados
Limitações da investigação
```

### 9. Produzir e apresentar o plano

- objetivo e critérios de aceite como condições verificáveis;
- alternativas avaliadas e a escolhida, com justificativa;
- componentes e arquivos previstos;
- componentes que **não** devem ser modificados;
- estratégia de testes;
- riscos;
- plano de rollback;
- dúvidas classificadas como bloqueantes ou não bloqueantes;
- premissas adotadas.

**Ponto de decisão:** havendo dúvida bloqueante, parar aqui e perguntar. Dúvida não bloqueante segue com a premissa mais conservadora, registrada explicitamente.

---

## Evidências

Saída dos comandos executados; identificação completa da org; lista dos componentes investigados e o que foi confirmado em cada um; diff revisado quando houver retrieve; registro do estado inicial; plano apresentado.

## Riscos

| Risco | Consequência | Mitigação |
| --- | --- | --- |
| Branch criada a partir de base desatualizada | conflitos e arrasto de trabalho de terceiros | `pull --ff-only` antes de criar |
| Org errada | alteração em ambiente indevido | confirmação por quatro atributos |
| Alterações locais descartadas | perda de trabalho | preservar e perguntar |
| Componente presumido inexistente | duplicidade | confirmar na org |
| Investigação superficial | retrabalho e regressão | mapear dependências e automações |

## Rollback

Nenhuma alteração é feita neste runbook além da criação da branch. Para desfazer:

```bash
git checkout {DEVELOPMENT_BASE_BRANCH}
git branch -d {FEATURE_BRANCH}
```

Se houver retrieve com alterações indesejadas, reverter **apenas os arquivos afetados**, preservando o restante do working tree.

## Critérios de conclusão

- [ ] Projeto, Git e org confirmados e registrados.
- [ ] Alterações locais preexistentes preservadas.
- [ ] Feature branch criada a partir da base atualizada.
- [ ] Commit-base registrado.
- [ ] Investigação concluída com evidências e API Names confirmados.
- [ ] Estado inicial registrado no projeto.
- [ ] Plano apresentado com riscos e rollback.
- [ ] Nenhuma implementação iniciada antes da aprovação do plano.

## Ações proibidas

Implementar antes da aprovação do plano; commit; push; abertura de Pull Request; deploy em UAT ou Produção; retrieve completo da org; descarte de alterações locais; comandos destrutivos; gravação de qualquer artefato na Salesforce-AI-Base.

## Referências

[instruction-precedence.md](../knowledge/instruction-precedence.md) · [operational-safety-policy.md](../knowledge/operational-safety-policy.md) · [environment-safety.md](../knowledge/environment-safety.md) · [salesforce-development-principles.md](../knowledge/salesforce-development-principles.md) · [github-development-workflow.md](../knowledge/github-development-workflow.md) · [retrieve-and-deploy-policy.md](../knowledge/retrieve-and-deploy-policy.md) · Skill: [start-salesforce-demand](../.claude/skills/start-salesforce-demand/SKILL.md)
