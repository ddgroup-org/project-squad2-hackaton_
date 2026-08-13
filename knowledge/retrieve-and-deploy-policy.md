---
title: "Política de retrieve e deploy"
description: "Regras para sincronização entre repositório e org Salesforce: retrieve direcionado, deploy controlado, manifests, conflitos e rollback."
category: "knowledge"
status: "active"
version: "1.2"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - cli
  - deploy
  - retrieve
  - metadata
applies_to:
  - global
source_of_truth: true
source_references:
  - arquitetura.md
  - desenvolvimento.md
  - execucao.md
---

# Política de retrieve e deploy

## Objetivo

Definir como o repositório e as orgs Salesforce são sincronizados com segurança, preservando o Git como baseline e evitando perda de trabalho.

Este documento é a **fonte da verdade** para retrieve, deploy, manifests, `.forceignore`, ordem de deploy e rollback de metadata.

## Escopo

Aplica-se a todos os ambientes (DEV, UAT, Produção). Os comandos de exemplo utilizam a Salesforce CLI moderna (`sf`).

**O mecanismo concreto depende do modelo de desenvolvimento do projeto**, que precisa ser identificado antes de qualquer operação:

| Modelo | Como a alteração chega à org | Como a alteração volta ao repositório |
| --- | --- | --- |
| **source-driven** | deploy direcionado por metadata ou manifest | retrieve direcionado |
| **org-driven** | configuração na org; repositório registra depois | retrieve é o mecanismo principal de registro |
| **metadata-based** | deploy por manifest (`package.xml`) | retrieve por manifest |
| **package-based / unlocked** | instalação de versão do pacote | alterações vão para o código-fonte do pacote, não por retrieve avulso |
| **managed package** | instalação de versão publicada | componentes gerenciados não são recuperados como código do projeto |
| **híbrido / legado em migração** | combinação; varia por componente | varia por componente — mapear antes |

Aplicar o procedimento de um modelo em um projeto que usa outro é causa frequente de perda de trabalho. **A base não altera o modelo do projeto** — ver [salesforce-development-principles.md](./salesforce-development-principles.md#11-source-driven-development--recomendação-não-imposição).

---

## 1. Conceitos

### 1.1 Direção das operações

```text
Git / local  → org   =  deploy
org / Setup  → Git / local  =  retrieve
```

Essa distinção é a origem da maioria dos erros de sincronização. Antes de executar qualquer comando, responder: **qual lado é a fonte da verdade para este componente neste momento?**

### 1.2 Git como baseline

O repositório representa o estado esperado. Divergências em relação à org são tratadas como informação a investigar, não como algo a eliminar automaticamente com um retrieve amplo.

### 1.3 Retrieve não é mecanismo de sincronização genérico

Retrieve serve para trazer alterações específicas feitas na org de volta ao repositório. Não é ferramenta para "alinhar tudo", "resolver conflito" nem "atualizar o projeto".

---

## 2. Regras obrigatórias

1. **Retrieve completo da org não deve ser executado como rotina.** É operação ampla, com alto risco de sobrescrever trabalho local e de trazer metadata de outras demandas.
2. **Retrieve deve ser direcionado** aos componentes efetivamente envolvidos na demanda.
3. **Deploy deve ser direcionado**, limitado aos componentes alterados.
4. **A org de destino deve ser confirmada antes de qualquer retrieve ou deploy** — alias, username, Organization ID e tipo de ambiente. Alias isolado não é identificação suficiente.
5. **Toda diferença recuperada deve ser revisada** com `git status` e `git diff` antes de qualquer commit.
6. **Alterações locais preexistentes não devem ser descartadas nem sobrescritas.**
7. **Nenhum deploy direto em Produção.** Produção é promovida pela esteira autorizada.
8. **Comandos destrutivos exigem autorização explícita**, inclusive `destructiveChanges.xml` e exclusão de metadata.
9. **Não assumir que um componente não existe** apenas porque não está no repositório local.
10. **Não assumir que todos os ambientes suportam source tracking.**

---

## 3. Confirmação da org

Antes de qualquer operação:

```bash
sf org list
sf org display --target-org {DEV_ORG_ALIAS}
```

Confirmar e registrar: alias, username, Organization ID, instance URL, se é sandbox ou Produção, status da autenticação e API Version.

Se houver qualquer indicação de que a org é Produção, aplicar o bloqueio padrão descrito em [environment-safety.md](./environment-safety.md#3-bloqueio-padrão-de-produção).

---

## 4. Retrieve direcionado

### 4.1 Por componente

```bash
sf project retrieve start \
  --metadata {METADATA_TYPE}:{COMPONENT_NAME} \
  --target-org {DEV_ORG_ALIAS}
```

### 4.2 Por manifest

```bash
sf project retrieve start \
  --manifest {MANIFEST_PATH} \
  --target-org {DEV_ORG_ALIAS}
```

### 4.3 Manifests por demanda

Manter um manifest específico por demanda facilita repetir a operação, revisar o escopo e auditar o que foi movido. O manifest pertence ao **projeto**, não a esta base global — o local recomendado é `{PROJECT_ROOT}/manifest/`.

Exemplo genérico:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>{COMPONENT_NAME}</members>
        <name>{METADATA_TYPE}</name>
    </types>
    <version>{API_VERSION}</version>
</Package>
```

### 4.4 Preview quando suportado

Quando a versão da CLI oferecer pré-visualização, usá-la antes de executar o retrieve para conhecer o impacto:

```bash
sf project retrieve preview --target-org {DEV_ORG_ALIAS}
```

Se o comando não estiver disponível na versão instalada, registrar a limitação e compensar com escopo estreito e revisão cuidadosa do diff.

### 4.5 Revisão obrigatória do resultado

```bash
git status
git diff
```

Retrieve traz ruído com frequência. Verificar especificamente:

- alterações de API Version não solicitadas;
- reordenação de elementos em XML;
- entradas de Profile, Permission Set ou Layout pertencentes a outras demandas;
- campos, Record Types ou automações criados por outra pessoa na mesma sandbox;
- remoção de elementos que existiam localmente e não vieram no retrieve.

Nada que não pertença à demanda deve ser incorporado ao commit.

---

## 5. Deploy direcionado

### 5.1 Validação antes do deploy

Sempre que o ambiente permitir, validar antes de aplicar:

```bash
sf project deploy validate \
  --manifest {MANIFEST_PATH} \
  --target-org {DEV_ORG_ALIAS} \
  --test-level RunSpecifiedTests \
  --tests {TEST_CLASS_NAME}
```

### 5.2 Deploy

```bash
sf project deploy start \
  --metadata {METADATA_TYPE}:{COMPONENT_NAME} \
  --target-org {DEV_ORG_ALIAS}
```

```bash
sf project deploy start \
  --manifest {MANIFEST_PATH} \
  --target-org {DEV_ORG_ALIAS} \
  --test-level RunSpecifiedTests \
  --tests {TEST_CLASS_NAME}
```

### 5.3 Acompanhamento e histórico

```bash
sf project deploy report --target-org {DEV_ORG_ALIAS}
sf project deploy resume --job-id {DEPLOY_JOB_ID}
```

### 5.4 Níveis de teste

O nível de teste depende do ambiente e da política do projeto. Ambientes produtivos e de homologação normalmente exigem execução de testes no deploy. Validar na configuração da pipeline do projeto antes de assumir um nível.

---

## 6. Source tracking

Sandboxes com source tracking habilitado permitem identificar alterações locais e remotas:

```bash
sf project retrieve preview --target-org {DEV_ORG_ALIAS}
sf project deploy preview --target-org {DEV_ORG_ALIAS}
```

Nem todos os ambientes suportam ou têm source tracking habilitado. Quando não houver, a identificação de mudanças depende de manifests, do histórico do Git e de inspeção direcionada. Não presumir disponibilidade: verificar.

Comandos que redefinem o tracking alteram o entendimento da ferramenta sobre o estado do ambiente e podem mascarar divergências reais. Usar apenas com autorização e motivo declarado.

---

## 7. Sandbox compartilhada

Em ambientes compartilhados, o risco principal é sobrescrever o trabalho de outra pessoa.

Antes de deploy ou retrieve:

- verificar se outra demanda está atuando nos mesmos componentes;
- verificar commits recentes na branch-base e Pull Requests abertos;
- limitar o escopo ao estritamente necessário;
- evitar deploy de arquivos de Profile e Permission Set completos quando apenas um trecho mudou;
- comunicar alterações em componentes de uso comum (frameworks de trigger, classes utilitárias, layouts principais).

Detectando alteração concorrente no mesmo artefato: interromper, preservar as duas versões, apresentar o conflito e recomendar coordenação.

---

## 8. `.forceignore`

O `.forceignore` controla o que é ignorado em retrieve e deploy. Usos legítimos:

- metadata volátil que gera ruído constante no diff;
- componentes gerenciados por outro time ou por pacote;
- arquivos específicos de ambiente que não devem ser promovidos.

Cuidados:

- alterar `.forceignore` muda o comportamento de todas as pessoas do projeto — trate como decisão do projeto, não como ajuste individual;
- um componente ignorado deixa de ser rastreado: isso pode esconder divergência real entre org e repositório;
- registrar o motivo de cada entrada, preferencialmente em comentário ou na documentação do projeto.

---

## 9. Dependências e ordem de deploy

Metadata Salesforce tem dependências de criação. Deploy fora de ordem falha ou produz estado parcial.

Ordem geral, quando a operação for fracionada:

1. objetos, campos e Record Types;
2. Custom Metadata Types e seus registros;
3. Validation Rules, formulas e Layouts;
4. Flows e automações declarativas;
5. classes Apex, Triggers e classes de teste;
6. LWC, Aura e Visualforce;
7. FlexiPages e Lightning Record Pages;
8. Permission Sets, Permission Set Groups e Custom Permissions;
9. Named Credentials, External Credentials e Remote Site Settings;
10. Reports e Dashboards dependentes.

Sempre que possível, executar o deploy do conjunto completo em uma única operação, deixando a plataforma resolver a ordem interna. O fracionamento é exceção, usada quando o conjunto é grande ou quando há falha a isolar.

Antes do deploy, mapear as dependências do que será enviado: campos referenciados por Flows e fórmulas, classes chamadas por LWC, Custom Metadata consumida por Apex, permissões necessárias para o funcionamento.

---

## 10. Comportamento por ambiente

O que é permitido em cada ambiente está definido em [environment-safety.md](./environment-safety.md#4-comportamento-por-ambiente) — fonte da verdade do tema. Em resumo, aplicado a retrieve e deploy:

| Ambiente | Retrieve | Deploy |
| --- | --- | --- |
| **DEV** | direcionado, após configuração pelo Setup | direcionado, quando incluído na tarefa ou autorizado |
| **UAT** | apenas leitura para diagnóstico | exclusivamente pela pipeline; manual é exceção autorizada e justificada |
| **Produção** | apenas leitura autorizada, para diagnóstico | exclusivamente pela pipeline de Produção |

Escopo estreito e revisão do diff continuam obrigatórios em qualquer ambiente.

---

## 11. Comandos destrutivos

Exclusão de metadata e `destructiveChanges.xml` exigem autorização explícita e verificação prévia reforçada de dependências.

Antes de propor remoção:

- confirmar que não há referência em Apex, Flow, LWC, Aura, Validation Rule, Approval Process, Layout, Report, Dashboard, Permission Set ou integração;
- confirmar que não há uso em dados existentes;
- confirmar que o comportamento foi substituído, quando for o caso;
- registrar as evidências que sustentam a conclusão.

Ausência de evidência não é evidência de ausência. Sem verificação, a recomendação é **não remover**.

---

## 12. Rollback

O rollback de um deploy não é automático. Planejar antes de executar:

- **código e metadata versionados**: redeploy da versão anterior a partir do commit-base identificado;
- **Flow**: reativação da versão anterior, quando existir — registrar qual versão estava ativa antes;
- **campos e objetos criados**: a remoção é operação destrutiva e exige autorização própria;
- **dados alterados**: não são revertidos por deploy; exigem plano específico e autorização;
- **configurações externas, pacotes e integrações**: podem exigir procedimento manual documentado.

Registrar sempre: o que será revertido, como, em qual ambiente, quais dependências existem, quais testes serão repetidos e quais efeitos **não** são reversíveis automaticamente.

---

## 13. Evidências esperadas

Para cada operação de retrieve ou deploy, registrar no projeto:

- data e hora;
- org utilizada (alias, username, Organization ID, tipo de ambiente);
- comando executado;
- escopo (componentes ou manifest);
- resultado (sucesso, falha, parcial);
- identificador do job de deploy, quando aplicável;
- testes executados e resultado real;
- diferenças revisadas;
- pendências e limitações.

Esse registro pertence ao projeto — nunca a esta base global.

---

## 14. Comandos legados

A CLI antiga (`sfdx force:source:*`, `sfdx force:mdapi:*`) ainda aparece em documentação e scripts existentes. O padrão desta base é a CLI moderna (`sf`). Comandos `sfdx` só devem ser usados para interpretar scripts legados do projeto ou quando a pipeline atual depender deles — e, nesse caso, o motivo deve ser registrado.

---

## 15. Checklist

- [ ] Org de destino confirmada por alias, username, Organization ID e tipo de ambiente.
- [ ] Direção da operação (deploy ou retrieve) definida conscientemente.
- [ ] Escopo direcionado, sem retrieve ou deploy amplo.
- [ ] Alterações locais preexistentes preservadas.
- [ ] Dependências de metadata mapeadas.
- [ ] Validação executada antes do deploy, quando suportada.
- [ ] `git status` e `git diff` revisados após retrieve.
- [ ] Nenhum segredo incorporado ao repositório.
- [ ] Plano de rollback definido.
- [ ] Evidências registradas no projeto.

---

## Referências cruzadas

- [environment-safety.md](./environment-safety.md) — identificação de org, bloqueio de Produção e comportamento por ambiente.
- [operational-safety-policy.md](./operational-safety-policy.md) — matriz de aprovação, comandos condicionados e falha parcial.
- [salesforce-development-principles.md](./salesforce-development-principles.md) — pre-flight e evidências.
- [github-development-workflow.md](./github-development-workflow.md) — onde retrieve e deploy se encaixam no fluxo.
- [testing-standards.md](./testing-standards.md) — níveis de teste e validação de deploy.
- Runbooks: [retrieve-from-dev.md](../runbooks/retrieve-from-dev.md), [deploy-to-dev.md](../runbooks/deploy-to-dev.md).

## Fontes oficiais recomendadas

Salesforce CLI Reference; Salesforce DX Developer Guide; Metadata API Developer Guide; documentação oficial de Metadata Coverage para verificar suporte de cada tipo de metadata na API.

## Limitações

O suporte a cada tipo de metadata, a disponibilidade de source tracking e as opções de cada comando variam por versão da CLI e por release da plataforma. Confirmar na Salesforce CLI Reference correspondente à versão instalada antes de assumir comportamento.

## Critérios de revisão

Revisar a cada atualização relevante da Salesforce CLI, mudança na pipeline do projeto ou alteração no modelo de ambientes.
