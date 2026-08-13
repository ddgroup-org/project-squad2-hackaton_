---
title: "Runbook — Retrieve direcionado da org DEV"
description: "Procedimento para recuperar da org DEV as alterações feitas pelo Setup, analisar diferenças e tratar conflitos em sandbox compartilhada."
category: "runbook"
status: "active"
version: "1.1"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - retrieve
  - cli
  - runbook
applies_to:
  - global
source_of_truth: false
source_references:
  - execucao.md
  - desenvolvimento.md
---

# Runbook — Retrieve direcionado da org DEV

## Objetivo

Trazer para o repositório as alterações feitas pela interface do Salesforce (Setup) na org DEV, de forma direcionada, com revisão completa das diferenças e sem sobrescrever trabalho local.

## Quando utilizar

Após realizar configurações pelo Setup — campos, Record Types, Validation Rules, Layouts, Permission Sets, Flows, Custom Metadata — que precisam ser versionadas.

**Não utilizar** como forma de "sincronizar o projeto" ou de "resolver conflito". Retrieve não é mecanismo genérico de sincronização.

## Pré-condições

- feature branch da demanda ativa;
- org DEV confirmada;
- lista dos componentes efetivamente alterados no Setup;
- working tree conhecido, com alterações locais identificadas.

## Entradas

```text
{DEV_ORG_ALIAS}     alias da org de desenvolvimento
{METADATA_TYPE}     tipo de metadata a recuperar
{COMPONENT_NAME}    nome do componente
{MANIFEST_PATH}     manifest da demanda, quando houver
{FEATURE_BRANCH}    branch da demanda
```

## Verificações iniciais

- [ ] Branch correta ativa.
- [ ] Alterações locais preexistentes identificadas e classificadas.
- [ ] Componentes a recuperar listados explicitamente.
- [ ] Org confirmada.

---

## Procedimento

### 1. Registrar o estado antes do retrieve

```bash
git branch --show-current
git status
git stash list
```

Este é o ponto de comparação. Sem ele, não há como distinguir o que veio do retrieve do que já estava local.

**Ponto de decisão:** havendo alterações locais não commitadas nos mesmos componentes que serão recuperados, o retrieve pode sobrescrevê-las. Antes de prosseguir:

- confirmar se a versão da org ou a versão local é a correta;
- quando ambas contiverem trabalho válido, preservar a versão local em um ponto seguro antes de recuperar;
- na dúvida, **não executar o retrieve** — perguntar.

### 2. Confirmar a org

```bash
sf org list
sf org display --target-org {DEV_ORG_ALIAS}
```

Confirmar alias, username, Organization ID, instance URL e tipo de ambiente. **Interromper diante de qualquer indício de Produção.**

### 3. Pré-visualizar, quando suportado

```bash
sf project retrieve preview --target-org {DEV_ORG_ALIAS}
```

**Ponto de decisão:** o comando depende de source tracking habilitado e da versão da CLI. Não estando disponível, registrar a limitação e compensar com escopo estreito e revisão detalhada do diff.

Se a pré-visualização indicar volume muito maior do que o esperado, **não prosseguir com retrieve amplo**. Restringir por componente.

### 4. Executar o retrieve direcionado

Por componente:

```bash
sf project retrieve start \
  --metadata {METADATA_TYPE}:{COMPONENT_NAME} \
  --target-org {DEV_ORG_ALIAS}
```

Por manifest:

```bash
sf project retrieve start \
  --manifest {MANIFEST_PATH} \
  --target-org {DEV_ORG_ALIAS}
```

**Nunca executar retrieve completo da org como rotina.**

### 5. Revisar todas as diferenças

```bash
git status
git diff
```

Classificar cada arquivo:

| Classificação | Ação |
| --- | --- |
| Alteração da demanda | manter |
| Ruído de formatação ou reordenação | reverter o arquivo |
| Alteração de API Version não solicitada | reverter |
| Metadata de outra demanda | reverter e comunicar |
| Remoção inesperada de elemento local | investigar antes de qualquer ação |
| Origem desconhecida | investigar; não manter por padrão |

**Ponto de decisão:** arquivos de Profile, Permission Set e Layout costumam trazer entradas de outras demandas e de outras pessoas. Revisar linha a linha. Manter apenas o que pertence à demanda.

Para reverter um arquivo específico sem afetar o restante:

```bash
git checkout -- caminho/do/arquivo
```

Aplicar por arquivo, nunca com `.` ou de forma ampla.

### 6. Verificar segredos

Inspecionar o diff quanto a valores reais de token, senha, client secret, chave privada ou certificado. Metadata de Named Credential, Connected App e configurações de integração merecem atenção específica.

**Encontrando segredo:** interromper, remover o valor, tratar a credencial como comprometida e reportar antes de qualquer commit.

### 7. Validar a consistência do resultado

- os componentes recuperados são os esperados;
- não há remoção acidental de elemento local;
- os arquivos estão íntegros e legíveis;
- a API Version permanece compatível com o projeto;
- o conjunto continua coerente com o que está na org.

### 8. Registrar as evidências

No projeto atual:

```text
Data e hora
Org: alias, username, Organization ID, tipo de ambiente
Comando executado
Componentes recuperados
Arquivos mantidos e arquivos revertidos, com motivo
Conflitos identificados e como foram tratados
Limitações
```

---

## Evidências

Saída dos comandos; `git status` e `git diff` antes e depois; lista de arquivos mantidos e revertidos com justificativa; identificação da org.

## Riscos

| Risco | Consequência | Mitigação |
| --- | --- | --- |
| Retrieve amplo | sobrescrita de trabalho local e ruído | escopo por componente ou manifest |
| Alteração de outra pessoa na sandbox | incorporação indevida ao commit | revisar diff linha a linha e comunicar |
| Ruído de formatação | diff volumoso e revisão superficial | reverter arquivos sem alteração real |
| Segredo em metadata de integração | vazamento no repositório | verificar antes do commit |
| Remoção silenciosa de elemento local | perda funcional | comparar com o estado anterior |
| Source tracking indisponível | falsa sensação de escopo controlado | confirmar disponibilidade; não presumir |

## Rollback

Para desfazer o retrieve, reverter **apenas os arquivos afetados**:

```bash
git checkout -- caminho/do/arquivo
```

Arquivos novos trazidos pelo retrieve e não desejados podem ser removidos individualmente após confirmação. Não usar `git clean -fd`, que remove também arquivos não rastreados legítimos.

## Critérios de conclusão

- [ ] Org confirmada.
- [ ] Estado anterior registrado.
- [ ] Retrieve direcionado, sem escopo amplo.
- [ ] Todas as diferenças revisadas e classificadas.
- [ ] Arquivos fora do escopo revertidos.
- [ ] Nenhum segredo no diff.
- [ ] Alterações locais preexistentes preservadas.
- [ ] Evidências registradas no projeto.

## Ações proibidas

Retrieve completo da org como rotina; sobrescrever alterações locais sem confirmação; `git checkout -- .`, `git restore .`, `git clean -fd` ou `git reset --hard`; commit sem revisar o diff; retrieve de org de Produção sem autorização explícita; gravação de metadata recuperada na Salesforce-AI-Base.

## Referências

[retrieve-and-deploy-policy.md](../knowledge/retrieve-and-deploy-policy.md) · [environment-safety.md](../knowledge/environment-safety.md) · [operational-safety-policy.md](../knowledge/operational-safety-policy.md) · [github-development-workflow.md](../knowledge/github-development-workflow.md) · [salesforce-development-principles.md](../knowledge/salesforce-development-principles.md) · [deploy-to-dev.md](./deploy-to-dev.md)
