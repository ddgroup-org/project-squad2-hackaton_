---
title: "Fluxo de desenvolvimento com GitHub"
description: "Fluxo condicional de branches, commits, Pull Requests e promoção: o modelo do projeto prevalece; o padrão desta base é fallback."
category: "knowledge"
status: "active"
version: "2.0"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - git
  - github
  - branching
  - release
applies_to:
  - global
source_of_truth: true
source_references:
  - execucao.md
  - metaprompt-salesforce.md
---

# Fluxo de desenvolvimento com GitHub

## Objetivo

Definir o fluxo padrão de trabalho com Git e GitHub em projetos Salesforce, do início da demanda até a validação pós-deploy em Produção.

Este documento é a **fonte da verdade** para os **princípios** de branches, commits, Pull Requests, promoção e rastreabilidade — não para os nomes de branch de nenhum projeto. Os runbooks executam este fluxo; não o reexplicam.

## Escopo

Aplica-se a qualquer repositório Salesforce, em qualquer modelo de desenvolvimento: source-driven, org-driven, metadata-based, package-based, unlocked package, managed package, híbrido ou legado em migração.

**O modelo de branches concreto pertence ao projeto.** Este documento fornece o fluxo lógico, os controles inegociáveis e um padrão de fallback para quando o projeto não definir o seu.

---

## 1. O fluxo do projeto vem primeiro

**Este documento descreve um padrão de referência, não um padrão universal.** Antes de aplicar qualquer coisa daqui, levantar o fluxo real do repositório atual.

### 1.1 Investigação obrigatória antes de aplicar

Consultar, nesta ordem:

1. `CLAUDE.md` e `AGENTS.md` do repositório;
2. documentação da pipeline e arquivos de CI;
3. branches remotas existentes e suas proteções;
4. histórico recente de merges e Pull Requests;
5. templates de Pull Request do repositório;
6. `docs/environments.md` e demais documentos de processo do projeto.

**O fluxo do projeto prevalece.** Ver [instruction-precedence.md](./instruction-precedence.md#3-o-que-o-projeto-pode-e-não-pode-adaptar): modelo de branches, estratégia de merge, uso de cherry-pick e modelo de packages são explicitamente adaptáveis pelo projeto.

### 1.2 Proibições

- **Não criar, renomear, substituir ou excluir branches para adequar um projeto ao padrão desta base.**
- Não presumir a existência de uma branch pelo nome usual — verificar no remoto.
- Não tratar a ausência de uma etapa deste documento como defeito do projeto: pode ser decisão arquitetural registrada.
- Não alterar o modelo de desenvolvimento do projeto sem decisão arquitetural (ADR) e autorização.

### 1.3 Placeholders

Nos documentos desta base, as branches aparecem como placeholders. Resolver cada um com o valor real do projeto antes de executar qualquer comando:

```text
{DEVELOPMENT_BASE_BRANCH}   branch-base do desenvolvimento
{UAT_TARGET_BRANCH}         branch cuja promoção alimenta o ambiente de homologação
{PRODUCTION_BASE_BRANCH}    branch-base de Produção
{FEATURE_BRANCH}            branch da demanda
{RELEASE_BRANCH}            branch de preparação da promoção a Produção
{HOTFIX_BRANCH}             branch de correção emergencial
```

Em muitos projetos `{DEVELOPMENT_BASE_BRANCH}` e `{UAT_TARGET_BRANCH}` são a mesma branch; em outros, não. Confirmar em vez de presumir.

### 1.4 Padrão de fallback

Quando — e **somente quando** — o projeto não definir seu próprio fluxo, aplicar este padrão de referência e registrar que ele foi adotado por ausência de definição local:

```text
{DEVELOPMENT_BASE_BRANCH}  = developer     exemplo de fallback
{UAT_TARGET_BRANCH}        = developer     exemplo de fallback
{PRODUCTION_BASE_BRANCH}   = main          exemplo de fallback
{FEATURE_BRANCH}           = feature/*     exemplo de fallback
{RELEASE_BRANCH}           = release/*     exemplo de fallback
{HOTFIX_BRANCH}            = hotfix/*      exemplo de fallback
```

Os nomes `developer` e `main` aparecem neste documento apenas como **exemplo do fallback**. Encontrá-los em um comando não significa que sejam os nomes corretos no projeto atual.

### 1.5 O que não é negociável

Independentemente do modelo adotado, permanecem obrigatórios:

- separação entre a linha que alimenta homologação e a linha que alimenta Produção;
- nenhum desenvolvimento diretamente sobre uma branch-base protegida;
- Pull Request e revisão para alteração de branch protegida;
- Produção promovida apenas por esteira autorizada;
- equivalência entre o que foi homologado e o que é promovido;
- rastreabilidade da demanda até o deploy.

Estes são controles de segurança, não convenções — ver [operational-safety-policy.md](./operational-safety-policy.md).

---

## 1.6 Estratégias de promoção aceitáveis

Nenhuma das estratégias abaixo é obrigatória; nenhuma é proibida. A escolha pertence ao projeto:

| Estratégia | Quando costuma ser adequada | Observação |
| --- | --- | --- |
| **Cherry-pick de commits homologados** | poucos commits, bem isolados, entrelaçamento baixo | é o padrão de fallback desta base, não uma exigência |
| **Merge controlado da linha completa** | tudo em `{UAT_TARGET_BRANCH}` é promovido junto | exige que nada não homologado esteja na linha |
| **Release branch com merge seletivo** | ciclos com escopo fechado por release | mais previsível que cherry-pick em volume alto |
| **Promotion branches encadeadas** | ambientes múltiplos, promoção linear | cada ambiente tem sua branch |
| **Trunk-based com feature flags** | entregas contínuas | exige disciplina de flag e de teste |
| **Package-based (unlocked ou managed)** | modularização por pacote, versionamento próprio | a unidade promovida é o pacote, não o commit |

O que a base exige é que a estratégia seja **declarada, rastreável e reversível** — não que seja uma específica.

---

## 2. Fluxo lógico

O fluxo abaixo descreve **etapas lógicas**, não nomes de branch. Um projeto pode implementá-lo com qualquer estratégia da seção 1.6.

```text
Confirmar o fluxo real do projeto
↓
Atualizar {DEVELOPMENT_BASE_BRANCH}
↓
Criar {FEATURE_BRANCH} a partir dela
↓
Confirmar a org de destino e o estado de sincronização
↓
Investigar os componentes envolvidos
↓
Desenvolver
↓
Levar as alterações locais para a org de desenvolvimento
↓
Trazer para o repositório o que foi configurado pelo Setup
↓
Revisar as diferenças integralmente
↓
Executar testes e validações
↓
Commit e push autorizados
↓
Pull Request para {UAT_TARGET_BRANCH}
↓
Pipeline
↓
Homologação no ambiente de aceite
↓
Aprovação do responsável técnico
↓
Preparar a promoção a Produção pela estratégia do projeto
↓
Pull Request para {PRODUCTION_BASE_BRANCH}
↓
Pipeline de Produção
↓
Deploy em Produção
↓
Validação pós-deploy
```

A etapa "levar as alterações para a org" varia com o modelo de desenvolvimento: deploy direcionado por metadata, deploy por manifest, instalação de versão de pacote ou sincronização por source tracking. Ver [retrieve-and-deploy-policy.md](./retrieve-and-deploy-policy.md).

---

## 3. Etapas detalhadas

### 3.1 Atualizar a branch-base

Antes de criar qualquer branch, sincronizar a base com o remoto. Trabalhar a partir de uma base desatualizada gera conflitos evitáveis e Pull Requests que carregam alterações de terceiros.

```bash
git checkout {DEVELOPMENT_BASE_BRANCH}
git pull --ff-only origin {DEVELOPMENT_BASE_BRANCH}
```

Se `--ff-only` falhar, existe divergência local. Investigar antes de prosseguir — não resolver com reset.

### 3.2 Criar a branch da demanda

```bash
git checkout -b {FEATURE_BRANCH}
```

Criação e troca de branch exigem autorização quando não fizerem parte explícita da tarefa (ver matriz em [operational-safety-policy.md](./operational-safety-policy.md#3-matriz-de-aprovação-humana)).

### 3.3 Sincronização com a org DEV

Confirmar a org de destino antes de qualquer operação e verificar se o que está na org corresponde ao que está no repositório para os componentes da demanda. Detalhes em [retrieve-and-deploy-policy.md](./retrieve-and-deploy-policy.md).

### 3.4 Investigação e desenvolvimento

Investigar antes de implementar; implementar a alteração mínima necessária. Ver [salesforce-development-principles.md](./salesforce-development-principles.md).

### 3.5 Deploy direcionado para DEV

Código e metadata alterados localmente vão para a org DEV por deploy **direcionado**, nunca por deploy do projeto inteiro como rotina.

### 3.6 Retrieve do que foi alterado pelo Setup

Configuração feita pela interface do Salesforce só existe na org até ser recuperada. Retrieve direcionado dos componentes tocados, seguido de revisão das diferenças.

### 3.7 Revisar diferenças

```bash
git status
git diff
```

Toda diferença recuperada da org precisa ser revisada antes do commit. Retrieve costuma trazer ruído: reordenação de elementos, alterações de API Version, campos de outras demandas, metadata de perfis. O que não pertence à demanda não entra no commit.

### 3.8 Testes e validações

Executar os testes e a análise estática antes do commit. Ver [testing-standards.md](./testing-standards.md).

### 3.9 Commit e push

Commit e push exigem autorização explícita. Ver seção 4.

### 3.10 Pull Request para a branch de homologação

Destino: `{UAT_TARGET_BRANCH}`. Abrir PR usando o template [pull-request-uat-template.md](../templates/pull-request-uat-template.md). Abertura de PR exige autorização explícita.

### 3.11 Pipeline e UAT

A pipeline valida e promove para UAT conforme configuração do projeto. Falha de pipeline é bloqueio, não sugestão.

### 3.12 Homologação e aprovação

A demanda é testada em UAT pelos critérios de aceite definidos. A aprovação do Tech Lead é pré-requisito para a promoção a Produção.

### 3.13 Preparação da promoção a Produção

**Princípio inegociável:** o que chega a Produção é exatamente o que foi homologado. Uma branch de desenvolvimento contém trabalho de outras demandas, possivelmente não homologado — promovê-la inteira arrasta esse trabalho junto.

**Como isso é garantido depende da estratégia do projeto** (seção 1.6). No padrão de fallback:

1. atualizar `{PRODUCTION_BASE_BRANCH}` a partir do remoto;
2. criar `{RELEASE_BRANCH}` a partir dela;
3. aplicar somente os commits homologados;
4. validar dependências entre os commits aplicados e o que já existe em `{PRODUCTION_BASE_BRANCH}`;
5. abrir Pull Request de `{RELEASE_BRANCH}` para `{PRODUCTION_BASE_BRANCH}`;
6. executar a pipeline de Produção;
7. validar após o deploy.

Em projetos que promovem a linha completa, que usam promotion branches ou que promovem versões de pacote, os passos 2 e 3 mudam — o princípio da equivalência, não.

O Pull Request de homologação e o Pull Request de Produção são **independentes** sempre que a estratégia do projeto permitir separá-los.

### 3.14 Validação pós-deploy

Após o deploy em Produção, confirmar o comportamento com evidências: execução dos cenários críticos, verificação de configurações manuais previstas, checagem de automações ativadas e monitoramento de erros. Registrar o resultado no projeto.

---

## 4. Commits

### 4.1 Autorização

Commit, push, merge, abertura de Pull Request, cherry-pick e rebase **sempre** exigem autorização explícita. Uma autorização para implementar não é autorização para versionar.

### 4.2 Qualidade dos commits

- commits pequenos e coerentes, com uma intenção clara por commit;
- não misturar refatoração ampla, correção e nova funcionalidade no mesmo commit;
- não incluir arquivos fora do escopo da demanda;
- não commitar credenciais, tokens, certificados, arquivos de log, dados de teste com informação sensível ou artefatos gerados;
- mensagem no padrão definido em [naming-conventions.md](./naming-conventions.md), referenciando a demanda.

### 4.3 Dependências entre commits

Um commit que depende de outro precisa ser identificado como tal. Isso é decisivo na promoção a Produção: aplicar um commit dependente sem o commit-base gera falha de deploy ou comportamento inconsistente.

Registrar, quando houver:

- commits que dependem de metadata criada em commit anterior;
- commits que dependem de configuração manual já aplicada na org;
- commits que dependem de outra demanda ainda não homologada.

---

## 5. Cherry-pick

**Cherry-pick é uma estratégia possível, não obrigatória.** É o padrão de fallback desta base porque preserva a equivalência com o homologado em cenários de escopo pequeno. Projetos que promovem a linha completa, usam promotion branches ou versionam pacotes não precisam usá-lo — e não devem ser adequados a ele.

### 5.1 Quando utilizar

Apenas quando o projeto adotar essa estratégia **e** os commits estiverem devidamente isolados, sem depender de mudanças não aprovadas.

```bash
git checkout {PRODUCTION_BASE_BRANCH}
git pull --ff-only origin {PRODUCTION_BASE_BRANCH}
git checkout -b {RELEASE_BRANCH}
git cherry-pick {COMMIT_HASH}
```

### 5.2 Quando **não** utilizar

- quando os commits homologados dependerem de commits não homologados;
- quando houver muitos commits entrelaçados na mesma área de código;
- quando a demanda envolver metadata que foi alterada por várias demandas em paralelo;
- quando o resultado do cherry-pick exigir resolução manual extensa de conflitos — nesse caso, o risco de divergência entre o que foi homologado e o que será promovido é alto.

Nessas situações, avaliar alternativas com o responsável técnico: promover o conjunto completo, adotar merge controlado, reorganizar os commits na origem, promover por versão de pacote ou reimplementar a alteração de forma isolada. A escolha é do projeto — ver seção 1.6.

O cherry-pick exige autorização explícita e verificação posterior de equivalência entre o conteúdo homologado e o conteúdo promovido.

---

## 6. Conflitos

Ao encontrar conflito:

1. não resolver com comandos destrutivos (`reset --hard`, `checkout -- .`, `clean -fd`);
2. identificar a origem de cada lado do conflito;
3. verificar se o conflito envolve trabalho de outra pessoa ou de outra demanda;
4. preservar as duas versões até entender a intenção de cada uma;
5. resolver apenas o que pertence ao escopo da demanda;
6. quando o conflito for de regra funcional, não decidir automaticamente — envolver a pessoa responsável;
7. após resolver, revisar o resultado completo com `git diff` antes de concluir.

Conflitos em metadata Salesforce merecem atenção redobrada: arquivos de Profile, Permission Set, Layout e `package.xml` costumam ser reordenados por ferramentas, o que produz conflitos volumosos e pouco significativos misturados a alterações reais.

---

## 7. Branches protegidas

As branches-base do projeto — `{DEVELOPMENT_BASE_BRANCH}`, `{UAT_TARGET_BRANCH}` e `{PRODUCTION_BASE_BRANCH}`, quaisquer que sejam seus nomes reais — devem exigir, no mínimo:

- Pull Request para qualquer alteração;
- revisão aprovada antes do merge;
- checks de pipeline concluídos com sucesso;
- bloqueio de push forçado;
- bloqueio de exclusão da branch.

Se o repositório não tiver essas proteções configuradas, registrar como recomendação ao responsável técnico. **A ausência de proteção técnica não autoriza push direto** — e não autoriza criar ou reconfigurar branches para "corrigir" o repositório.

---

## 8. Rastreabilidade

Cada demanda deve ser rastreável de ponta a ponta:

```text
Demanda → branch → commits → Pull Request de UAT → homologação → branch de release → Pull Request de Produção → deploy → validação
```

Elementos mínimos de rastreabilidade:

- identificador da demanda no nome da branch e nas mensagens de commit;
- descrição do Pull Request referenciando a demanda e as evidências;
- Pull Request de Produção referenciando o Pull Request de UAT correspondente;
- registro do resultado da validação pós-deploy no projeto.

---

## 9. Práticas proibidas

- desenvolver diretamente sobre uma branch-base protegida;
- promover para Produção uma branch que contenha trabalho não homologado;
- criar, renomear ou substituir branches para adequar o projeto ao padrão desta base;
- executar commit, push, merge, PR, cherry-pick ou rebase sem autorização explícita;
- usar `git push --force` em branch compartilhada;
- resolver conflito descartando o trabalho de outra pessoa;
- incluir no commit arquivos que não pertencem à demanda;
- versionar credenciais, segredos ou dados sensíveis;
- promover para Produção conteúdo diferente do que foi homologado;
- alterar o modelo de branches ou de desenvolvimento do projeto sem decisão arquitetural registrada e autorização.

---

## 10. Checklist antes do Pull Request

- [ ] Fluxo real do projeto confirmado antes de aplicar qualquer padrão desta base.
- [ ] Branch criada a partir da base correta e atualizada, com o nome real do projeto.
- [ ] Apenas arquivos da demanda modificados.
- [ ] `git status` e `git diff` revisados integralmente.
- [ ] Nenhum segredo, token ou dado sensível no diff.
- [ ] Testes executados e resultado real registrado.
- [ ] Análise estática executada e apontamentos relevantes tratados.
- [ ] Dependências entre commits identificadas.
- [ ] Descrição do PR preenchida a partir do template correspondente.
- [ ] Plano de rollback declarado.
- [ ] Autorização explícita obtida para commit, push e abertura do PR.

---

## Referências cruzadas

- [salesforce-development-principles.md](./salesforce-development-principles.md) — modos operacionais e matriz de aprovação.
- [retrieve-and-deploy-policy.md](./retrieve-and-deploy-policy.md) — retrieve e deploy direcionados.
- [naming-conventions.md](./naming-conventions.md) — nomes de branch, commit e Pull Request.
- Runbooks: [start-new-demand.md](../runbooks/start-new-demand.md), [promote-to-uat.md](../runbooks/promote-to-uat.md), [promote-to-production.md](../runbooks/promote-to-production.md), [emergency-hotfix.md](../runbooks/emergency-hotfix.md).
- Templates: [pull-request-uat-template.md](../templates/pull-request-uat-template.md), [pull-request-production-template.md](../templates/pull-request-production-template.md).

## Fontes oficiais recomendadas

Documentação oficial do GitHub para proteção de branches e Pull Requests; Salesforce CLI Reference e Salesforce DX Developer Guide para o modelo source-driven.

## Limitações

O modelo de branches, o modelo de pipeline, as ferramentas de CI, a estratégia de promoção e as regras de aprovação variam por projeto. Este documento descreve o fluxo lógico e os controles inegociáveis; **a implementação concreta pertence ao repositório atual** e deve ser confirmada nele antes de qualquer aplicação.

Os nomes `developer`, `main`, `feature/*`, `release/*` e `hotfix/*` aparecem aqui exclusivamente como exemplo do padrão de fallback da seção 1.4.

## Critérios de revisão

Revisar quando o time alterar o modelo de branches, quando a esteira de CI/CD mudar ou quando o processo de homologação for redefinido.
