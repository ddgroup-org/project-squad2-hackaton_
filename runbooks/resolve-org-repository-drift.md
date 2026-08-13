---
title: "Runbook — Resolver divergência entre org e repositório"
description: "Procedimento para diagnosticar e resolver drift entre branch-base, working tree, remoto, org e metadata recuperada, sem retrieve amplo."
category: "runbook"
status: "active"
version: "1.0"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - drift
  - synchronization
  - metadata
  - runbook
applies_to:
  - global
source_of_truth: false
source_references:
  - execucao.md
  - desenvolvimento.md
  - arquitetura.md
---

# Runbook — Resolver divergência entre org e repositório

## Objetivo

Diagnosticar e resolver divergências (*drift*) entre o que está no repositório e o que está na org, preservando trabalho de todas as origens envolvidas.

## Princípio

**Divergência é informação, não sujeira.** Cada diferença tem uma origem — alguém configurou algo pelo Setup, alguém promoveu um commit, uma pipeline aplicou uma alteração, um refresh substituiu o ambiente. Apagar a divergência sem entendê-la destrói a informação e, com frequência, o trabalho de alguém.

**Retrieve completo não é mecanismo de sincronização.** É a forma mais rápida de transformar um drift diagnosticável em perda de trabalho.

## Quando utilizar

O repositório e a org divergem e não se sabe por quê: componente presente na org e ausente no repositório; comportamento na org diferente do código versionado; diff volumoso e inesperado após retrieve; dúvida sobre qual lado é a fonte da verdade.

## Documentos aplicáveis

- [retrieve-and-deploy-policy.md](../knowledge/retrieve-and-deploy-policy.md) — retrieve direcionado e modelos de desenvolvimento.
- [environment-safety.md](../knowledge/environment-safety.md) — identificação de org e comportamento por ambiente.
- [operational-safety-policy.md](../knowledge/operational-safety-policy.md) — concorrência e preservação de trabalho de terceiros.
- [instruction-precedence.md](../knowledge/instruction-precedence.md) — estado real da org como nível de evidência.

---

## 0. Antes de tudo: qual é o modelo do projeto?

A pergunta "qual lado é a fonte da verdade?" **não tem resposta universal** — depende do modelo de desenvolvimento:

| Modelo | Fonte da verdade esperada | Drift significa |
| --- | --- | --- |
| source-driven | repositório | algo foi feito na org sem retornar ao repositório |
| org-driven | org | o repositório está desatualizado por design |
| metadata-based | manifest versionado | componente fora do manifest não é rastreado |
| package-based / unlocked | código-fonte do pacote | alteração direta na org é fora do processo |
| managed package | o pacote publicado | componentes gerenciados não são versionados localmente |
| híbrido / legado em migração | **varia por componente** | mapear componente a componente |

Confirmar o modelo em `CLAUDE.md`, `docs/architecture.md` ou com o responsável técnico **antes** de decidir o que fazer com a divergência. Ver [salesforce-development-principles.md](../knowledge/salesforce-development-principles.md#11-source-driven-development--recomendação-não-imposição).

---

## Procedimento

### 1. Confirmar a org e a branch

```bash
sf org list
sf org display --target-org {ORG_OU_AMBIENTE}
git branch --show-current
git status
```

Confirmar alias, username, Organization ID e tipo de ambiente. **Muitos "drifts" são apenas comparação com a org errada.**

**Ponto de decisão:** qualquer indício de Produção interrompe a investigação ativa — a comparação com Produção é feita apenas em leitura.

### 2. Levantar as origens possíveis, em ordem

Comparar cada uma antes de concluir. A ordem importa: as primeiras são baratas e explicam a maioria dos casos.

#### 2.1 Working tree local

```bash
git status
git diff
git stash list
```

Alterações locais não commitadas são a explicação mais frequente e a mais fácil de destruir por engano. **Identificar a quem pertencem** antes de qualquer coisa.

#### 2.2 Branch-base local × remoto

```bash
git fetch origin
git log {DEVELOPMENT_BASE_BRANCH}..origin/{DEVELOPMENT_BASE_BRANCH} --oneline
git log origin/{DEVELOPMENT_BASE_BRANCH}..{DEVELOPMENT_BASE_BRANCH} --oneline
```

Base local desatualizada explica divergência aparente sem que exista drift real.

#### 2.3 Outras branches

Um componente "ausente" pode estar em outra branch ainda não promovida — feature branch de outra pessoa, release em preparação, hotfix não propagado.

```bash
git branch -a
git log --all --oneline -- caminho/do/componente
```

#### 2.4 Pull Requests abertos

Alteração aprovada e ainda não mesclada, ou mesclada e ainda não promovida ao ambiente, produz divergência legítima e temporária.

#### 2.5 Alterações concorrentes na sandbox

Em ambiente compartilhado, outra pessoa pode ter alterado o mesmo componente pelo Setup. Verificar histórico de modificação do componente na org e alinhar antes de tocar nele.

#### 2.6 Metadata recuperada × repositório

Somente depois de esgotar as origens acima, comparar a metadata da org com a versão versionada — **e de forma direcionada**, componente a componente.

### 3. Recuperar de forma direcionada, nunca ampla

```bash
sf project retrieve start \
  --metadata {METADATA_TYPE}:{COMPONENT_NAME} \
  --target-org {ORG_OU_AMBIENTE}
```

**Ponto de decisão — proibição:** não executar retrieve completo da org como forma de "sincronizar", "alinhar" ou "resolver o conflito". Retrieve amplo sobrescreve trabalho local, traz metadata de outras demandas e substitui um problema diagnosticável por um diff impossível de revisar.

Quando o volume da divergência for grande, a resposta é **fatiar a investigação**, não ampliar o retrieve.

Se houver alterações locais não commitadas nos mesmos componentes, preservá-las em ponto seguro antes de recuperar. Na dúvida, **não recuperar** — perguntar.

### 4. Classificar cada diferença

| Classificação | Origem provável | Ação |
| --- | --- | --- |
| Alteração da demanda atual | trabalho em curso | manter |
| Configuração feita pelo Setup ainda não versionada | trabalho legítimo | versionar, com revisão |
| Alteração de outra demanda | trabalho de terceiro | **não incorporar**; comunicar |
| Ruído de formatação ou reordenação | ferramenta | reverter o arquivo |
| Alteração de API Version não solicitada | ferramenta | reverter |
| Componente gerenciado por pacote | pacote instalado | não versionar como código do projeto |
| Remoção inesperada de elemento local | possível perda | **investigar antes de qualquer ação** |
| Origem desconhecida | indeterminada | investigar; não manter por padrão |

Arquivos de Profile, Permission Set, Layout e `package.xml` merecem revisão linha a linha — são os que mais acumulam entradas de terceiros.

### 5. Determinar a fonte da verdade por componente

Não existe resposta única para todo o drift. Para **cada** componente divergente, responder:

```text
1. Qual versão é a correta funcionalmente?
2. Quem produziu cada versão?
3. Alguma das versões já foi homologada?
4. Alguma das versões já está em Produção?
5. Existe dependência entre este componente e outro divergente?
```

**Ponto de decisão:** quando as duas versões contiverem trabalho válido, isso não é drift — é **conflito**. Seguir [handle-metadata-conflict.md](./handle-metadata-conflict.md).

### 6. Resolver

Com a classificação feita e a fonte da verdade definida por componente:

- **repositório correto** → deploy direcionado para a org, com autorização compatível com o ambiente;
- **org correta** → retrieve direcionado, revisão do diff e commit com autorização;
- **ambos parcialmente corretos** → conflito: não resolver automaticamente;
- **nenhum correto** → a correção é uma demanda, não uma sincronização.

Reverter arquivo a arquivo o que não pertence ao escopo:

```bash
git checkout -- caminho/do/arquivo
```

Nunca com `.` nem de forma ampla.

### 7. Prevenir a recorrência

Drift recorrente é sintoma de processo, não de descuido. Registrar a causa e a recomendação:

| Causa frequente | Recomendação |
| --- | --- |
| Configuração pelo Setup sem retrieve | incluir o retrieve no fluxo da demanda |
| Deploy manual em ambiente que deveria receber só pela pipeline | reforçar o gate |
| Refresh de sandbox sem reconfiguração | checklist pós-refresh documentado |
| Ambiente compartilhado sem coordenação | acordo de ownership por componente |
| Componentes voláteis gerando ruído constante | avaliar `.forceignore`, com decisão do projeto |
| Modelo de desenvolvimento indefinido | registrar como ADR |

### 8. Registrar

No projeto atual:

```text
Data e hora
Org e branch comparadas
Modelo de desenvolvimento confirmado
Componentes divergentes, um a um
Origem identificada de cada divergência
Fonte da verdade adotada e justificativa
Ações executadas
Conflitos identificados e encaminhamento
Causa raiz e recomendação preventiva
Pendências
```

---

## Evidências

Identificação da org; `git status` e `git diff` antes e depois; lista de componentes divergentes com origem identificada; decisão de fonte da verdade por componente; registro do que foi mantido, revertido e comunicado.

## Riscos

| Risco | Consequência | Mitigação |
| --- | --- | --- |
| Retrieve completo como sincronização | perda de trabalho local e ruído massivo | retrieve direcionado, componente a componente |
| Sobrescrever trabalho de outra pessoa | perda e retrabalho | identificar origem antes de agir |
| Presumir a fonte da verdade | promoção de comportamento errado | decidir componente a componente |
| Comparar com a org errada | diagnóstico inteiro inválido | confirmar org por quatro atributos |
| Tratar conflito como drift | decisão funcional tomada por engano | conflito segue runbook próprio |
| Ignorar o modelo do projeto | procedimento inadequado ao modelo | confirmar o modelo antes |
| Resolver o sintoma | drift recorrente | registrar causa e recomendação |

## Rollback

Nenhuma alteração deste runbook é irreversível se executada arquivo a arquivo. Para desfazer:

1. reverter os arquivos afetados individualmente;
2. quando houver deploy executado, redeploy da versão anterior a partir do commit-base;
3. reativar a versão anterior dos Flows, quando aplicável;
4. registrar o que foi desfeito.

Alterações aplicadas na org por deploy durante a resolução seguem [recover-failed-operation.md](./recover-failed-operation.md) se falharem.

## Critérios de conclusão

- [ ] Org e branch confirmadas.
- [ ] Modelo de desenvolvimento do projeto confirmado.
- [ ] Todas as origens possíveis verificadas antes de recuperar metadata.
- [ ] Nenhum retrieve amplo executado.
- [ ] Cada diferença classificada com origem identificada.
- [ ] Fonte da verdade definida por componente, com justificativa.
- [ ] Alterações locais e trabalho de terceiros preservados.
- [ ] Conflitos encaminhados ao runbook próprio.
- [ ] Causa raiz registrada com recomendação preventiva.
- [ ] Registro salvo no projeto.

## Ações proibidas

Retrieve completo da org como mecanismo de sincronização; sobrescrever alterações locais sem confirmação; incorporar ao commit metadata de outra demanda; `git checkout -- .`, `git restore .`, `git clean -fd` ou `git reset --hard`; resolver conflito de regra funcional automaticamente; alterar o modelo de desenvolvimento do projeto para "resolver" o drift; gravar a análise na Salesforce-AI-Base.

## Referências

[retrieve-and-deploy-policy.md](../knowledge/retrieve-and-deploy-policy.md) · [environment-safety.md](../knowledge/environment-safety.md) · [operational-safety-policy.md](../knowledge/operational-safety-policy.md) · [instruction-precedence.md](../knowledge/instruction-precedence.md) · [salesforce-development-principles.md](../knowledge/salesforce-development-principles.md) · [handle-metadata-conflict.md](./handle-metadata-conflict.md) · [recover-failed-operation.md](./recover-failed-operation.md) · [retrieve-from-dev.md](./retrieve-from-dev.md)

## Critérios de revisão

Revisar quando o modelo de desenvolvimento do time mudar, quando um novo ambiente for adicionado ao fluxo e sempre que um drift recorrente indicar lacuna de processo.
