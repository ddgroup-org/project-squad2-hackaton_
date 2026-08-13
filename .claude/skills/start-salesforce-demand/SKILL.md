---
name: start-salesforce-demand
description: Use ao iniciar uma nova demanda Salesforce, antes de escrever qualquer código. Prepara branch, confirma org, investiga o estado atual, registra o ponto de partida e produz o plano de implementação.
---

# Objetivo

Iniciar uma demanda Salesforce com o ambiente confirmado, o estado inicial registrado e um plano de implementação aprovado — evitando desenvolvimento sobre premissa incorreta, branch errada ou org errada.

# Pré-condições

- projeto Salesforce identificado, com caminho absoluto conhecido;
- demanda descrita, com critérios de aceite ou expectativa clara;
- acesso de leitura ao repositório;
- quando houver operação em org: acesso autorizado à org DEV.

# Entradas

```text
{DEMANDA}            descrição e critérios de aceite
{PROJECT_ROOT}       caminho absoluto do projeto
{FEATURE_BRANCH}     nome da branch da demanda
{DEVELOPMENT_BASE_BRANCH}        branch-base (padrão: developer)
{DEV_ORG_ALIAS}      alias da org de desenvolvimento
```

Informação ausente não deve ser inventada. Registrar como pendência ou premissa segura.

# Procedimento

## 1. Ler as instruções aplicáveis

Global — governança: [instruction-precedence.md](../../../knowledge/instruction-precedence.md), [operational-safety-policy.md](../../../knowledge/operational-safety-policy.md) e [environment-safety.md](../../../knowledge/environment-safety.md).

Global — técnicos: [salesforce-development-principles.md](../../../knowledge/salesforce-development-principles.md) e [github-development-workflow.md](../../../knowledge/github-development-workflow.md).

Do projeto: `CLAUDE.md`, `AGENTS.md`, `README.md`, documentação de arquitetura, de ambientes e ADRs. **As regras do projeto prevalecem** nos limites de [instruction-precedence.md](../../../knowledge/instruction-precedence.md#3-o-que-o-projeto-pode-e-não-pode-adaptar).

## 2. Pre-flight de projeto

Confirmar caminho absoluto, existência de `sfdx-project.json`, package directories, API Version e estrutura do repositório.

## 3. Pre-flight de Git

```bash
git status
git branch --show-current
git log --oneline -10
git remote -v
```

Verificar: branch atual, working tree, arquivos modificados e não rastreados, commits locais não enviados, divergência com o remoto e operações incompletas (merge, rebase, cherry-pick).

**Havendo alterações locais preexistentes, preservá-las.** Não descartar, não incorporar automaticamente, não executar comando que possa sobrescrevê-las. Se pertencerem a outra demanda, registrar e solicitar orientação antes de prosseguir.

## 4. Atualizar a branch-base

```bash
git checkout {DEVELOPMENT_BASE_BRANCH}
git pull --ff-only origin {DEVELOPMENT_BASE_BRANCH}
```

Falha de `--ff-only` indica divergência local: investigar, não resolver com reset.

## 5. Criar a feature branch

```bash
git checkout -b {FEATURE_BRANCH}
```

Nome conforme [naming-conventions.md](../../../knowledge/naming-conventions.md#11-branches). Criação de branch exige autorização quando não fizer parte explícita da tarefa.

## 6. Confirmar a org DEV

```bash
sf org list
sf org display --target-org {DEV_ORG_ALIAS}
```

Confirmar e registrar alias, username, Organization ID, instance URL, tipo de ambiente e API Version. **Alias isolado não é identificação suficiente.**

Havendo qualquer indício de Produção, interromper. Indicadores e procedimento completo em [environment-safety.md](../../../knowledge/environment-safety.md#31-indicadores-de-possível-produção).

## 7. Investigar a demanda

- localizar os componentes possivelmente envolvidos no repositório;
- confirmar API Names reais por metadata, consulta ou ferramenta — não por memória;
- verificar se já existe solução total ou parcial;
- mapear dependências: objetos, campos, automações, classes, componentes, permissões e integrações;
- levantar as automações existentes no objeto afetado e o momento em que executam;
- identificar testes existentes;
- verificar licenciamento quando a solução puder depender de feature licenciada.

**Não concluir que um componente não existe apenas porque não está no repositório local.** A ausência precisa ser confirmada na org ou na documentação do projeto.

## 8. Retrieve direcionado, quando necessário

Somente dos componentes efetivamente envolvidos, seguindo [retrieve-and-deploy-policy.md](../../../knowledge/retrieve-and-deploy-policy.md). Nunca retrieve completo como rotina. Revisar o diff antes de manter qualquer alteração.

## 9. Registrar o estado inicial

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
```

Este registro é a referência do rollback. Salvar no **projeto atual**, nunca na Salesforce-AI-Base.

## 10. Produzir o plano de implementação

- objetivo e critérios de aceite traduzidos em condições verificáveis;
- alternativas avaliadas (reutilização, configuração, automação declarativa, híbrida, programática) e a escolhida, com justificativa;
- componentes e arquivos previstos;
- **componentes que não devem ser modificados**;
- estratégia de testes;
- riscos identificados;
- plano de rollback;
- dúvidas classificadas como bloqueantes ou não bloqueantes.

## 11. Apresentar antes de implementar

Apresentar o plano e as premissas adotadas. Havendo dúvida bloqueante, interromper aqui.

# Validações

- [ ] Instruções globais e do projeto lidas.
- [ ] Pre-flight de projeto, Git e org concluído.
- [ ] Alterações locais preexistentes preservadas.
- [ ] Branch-base atualizada e feature branch criada a partir dela.
- [ ] Org confirmada por alias, username, Organization ID e tipo de ambiente.
- [ ] API Names confirmados, não presumidos.
- [ ] Dependências e automações existentes mapeadas.
- [ ] Estado inicial registrado no projeto.
- [ ] Plano de implementação produzido, com riscos e rollback.
- [ ] Premissas declaradas explicitamente.

# Evidências

Saída dos comandos de Git e de identificação da org; lista de componentes investigados e o que foi confirmado em cada um; diff revisado, quando houver retrieve; registro do estado inicial; plano de implementação.

# Situações de interrupção

- org não confirmada ou com indício de Produção;
- Git em estado inconsistente ou com operação incompleta;
- alterações locais fora do escopo em risco;
- branch-base divergente sem resolução segura;
- demanda dependente de outra ainda não concluída;
- dúvida bloqueante de regra de negócio;
- licença ou dependência não confirmada, sem alternativa nativa viável;
- componente compartilhado com alteração concorrente de outra pessoa.

Informar: o que foi detectado, qual risco existe, quais ações já ocorreram, qual decisão é necessária e qual alternativa segura existe.

# Saída esperada

1. Confirmação do ambiente: projeto, branch, commit-base e org.
2. Estado inicial registrado.
3. Resultado da investigação, com evidências e API Names confirmados.
4. Plano de implementação com alternativas, decisão, escopo, testes, riscos e rollback.
5. Premissas adotadas e pendências.
6. Confirmação explícita de que nenhuma alteração foi realizada até aqui.

# Ações proibidas nesta skill

Implementar antes da aprovação do plano; commit; push; abertura de Pull Request; deploy em UAT ou Produção; retrieve amplo; descarte de alterações locais; gravação de qualquer artefato na Salesforce-AI-Base.

Runbook correspondente: [start-new-demand.md](../../../runbooks/start-new-demand.md).
