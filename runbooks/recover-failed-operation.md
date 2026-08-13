---
title: "Runbook — Recuperar uma operação que falhou"
description: "Procedimento para interromper, diagnosticar e recuperar uma operação que falhou parcialmente em arquivos, Git, metadata, dados ou pipeline."
category: "runbook"
status: "active"
version: "1.0"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - recovery
  - partial-failure
  - rollback
  - runbook
applies_to:
  - global
source_of_truth: false
source_references:
  - execucao.md
  - metaprompt-salesforce.md
---

# Runbook — Recuperar uma operação que falhou

## Objetivo

Recuperar o estado conhecido após uma operação que falhou — total ou parcialmente — sem agravar o problema com tentativas repetidas ou correções "por cima".

## Princípio

**Uma operação que falhou parcialmente deixou o ambiente em estado desconhecido.** A primeira ação não é corrigir: é **parar e descobrir o que aconteceu**.

O erro mais caro nesta situação é repetir o comando. A repetição de uma escrita que falhou pode duplicar efeitos, mascarar a causa e destruir a evidência que permitiria diagnosticar.

## Quando utilizar

Deploy que falhou depois de processar parte dos componentes; retrieve que alterou apenas parte dos arquivos; cherry-pick ou merge interrompido com conflitos; pipeline que parou no meio; script que processou parte dos registros; criação incompleta de metadata dependente; operação de arquivo interrompida.

## Quando não utilizar

Falha limpa, sem efeito algum — comando rejeitado na validação, autenticação recusada, erro de sintaxe antes da execução. Nesses casos não há estado parcial: corrigir a causa e reexecutar normalmente.

## Documentos aplicáveis

- [operational-safety-policy.md](../knowledge/operational-safety-policy.md#8-tratamento-de-falhas-parciais) — regra de tratamento de falha parcial.
- [environment-safety.md](../knowledge/environment-safety.md) — confirmação de ambiente antes de qualquer recuperação.
- [instruction-precedence.md](../knowledge/instruction-precedence.md) — o que prevalece quando a recuperação conflita com o pedido original.

---

## Procedimento

### 1. Interromper imediatamente

**Nenhuma ação de escrita subsequente.** Isso inclui a ação que falhou, as ações que dependiam dela e qualquer "ajuste rápido".

**Ponto de decisão:** se houver uma operação ainda em andamento (deploy assíncrono, job, pipeline), **não cancelar automaticamente** — cancelar no meio pode produzir um estado pior. Consultar o status, registrar, e decidir com autorização.

### 2. Preservar a evidência antes de qualquer coisa

A evidência desaparece rápido: sessões de terminal são fechadas, logs rotacionam, jobs saem da fila.

Capturar e salvar **no projeto** (`{PROJECT_ROOT}/docs/evidence/`), antes de qualquer tentativa de recuperação:

```text
Data e hora da falha
Comando ou operação executada, na íntegra
Saída completa, incluindo a mensagem de erro
Identificador do job, quando houver
Org: alias, username, Organization ID, tipo de ambiente
Branch e commit no momento da falha
Estado do working tree
```

**Não gravar essas evidências na Salesforce-AI-Base.**

### 3. Confirmar o ambiente

Antes de investigar, confirmar em qual org e em qual branch o problema ocorreu — a recuperação errada, no ambiente errado, transforma um problema em dois.

Confirmar alias, username, Organization ID e tipo de ambiente. Ver [environment-safety.md](../knowledge/environment-safety.md#1-identificação-da-org).

**Ponto de decisão:** falha em Produção muda o procedimento. Nenhuma recuperação em Produção é executada sem autorização explícita do responsável pelo ambiente.

### 4. Inventariar o que foi aplicado

Responder, componente a componente ou registro a registro:

| Pergunta | Como responder |
| --- | --- |
| O que foi concluído com sucesso? | relatório da operação, log do job, estado atual |
| O que falhou? | mensagem de erro, itens listados como falha |
| O que **não chegou a ser tentado**? | comparar o escopo previsto com o processado |
| Houve efeito colateral? | automações acionadas, integrações chamadas, notificações enviadas |
| O estado atual é consistente? | dependências satisfeitas, referências resolvidas |

O terceiro item é o mais esquecido e o mais importante: um componente não tentado é diferente de um componente que falhou.

### 5. Classificar a falha pelo tipo

O procedimento de recuperação depende do que foi afetado.

#### 5.1 Falha em arquivo local

Escopo limitado, reversão barata.

- identificar exatamente quais arquivos foram criados, alterados ou removidos;
- comparar com o estado registrado antes da operação;
- reverter **arquivo a arquivo**, nunca o diretório inteiro;
- preservar alterações não relacionadas presentes no mesmo working tree.

**Nunca** usar `git checkout -- .`, `git restore .`, `git clean -fd` ou `git reset --hard` para "limpar".

#### 5.2 Falha em operação Git

Merge, rebase ou cherry-pick interrompido deixa o repositório em estado especial.

- identificar o estado (`git status` informa a operação em andamento);
- **não iniciar outra operação Git** sobre um estado incompleto;
- decidir conscientemente entre concluir a resolução ou abortar a operação;
- abortar exige autorização quando houver resolução de conflito já feita — ela seria perdida;
- preservar o trabalho de terceiros envolvido no conflito.

Ver [handle-metadata-conflict.md](./handle-metadata-conflict.md) quando o conflito for de metadata.

#### 5.3 Falha em deploy de metadata

O caso mais comum e o mais enganoso: parte dos componentes pode ter sido aplicada.

- obter o relatório completo do deploy pelo identificador do job;
- listar componentes com sucesso, com falha e não processados;
- verificar se algum componente aplicado depende de outro que falhou — essa combinação é a que produz comportamento incorreto silencioso;
- verificar se automações foram ativadas ou desativadas;
- verificar a versão ativa de cada Flow implantado;
- **não reexecutar o deploy** antes de entender o estado.

**Ponto de decisão:** com dependência quebrada em ambiente compartilhado, avaliar se o correto é completar o deploy (aplicando o que falta) ou reverter o que foi aplicado. A decisão depende de quem mais usa o ambiente — coordenar antes.

#### 5.4 Falha em operação com dados

**Deploy não reverte dados.** Esta é a categoria de menor reversibilidade.

- identificar exatamente quais registros foram criados, alterados ou excluídos;
- verificar se automações dispararam em cadeia a partir dessas alterações;
- verificar se integrações foram acionadas e se notificações foram enviadas para fora;
- **não executar correção em massa** sem plano específico e autorização;
- tratar a correção de dados como uma operação nova, com seu próprio plano, backup e aprovação.

Registros excluídos podem estar recuperáveis por um período — verificar antes de concluir que a perda é definitiva, e não presumir o contrário.

#### 5.5 Falha em pipeline

- identificar em qual etapa parou;
- verificar se a etapa que falhou tinha efeito no ambiente ou era apenas validação;
- verificar se etapas posteriores foram puladas ou executadas;
- **não reexecutar a pipeline repetidamente** esperando resultado diferente;
- diagnosticar a causa real antes de qualquer nova execução.

### 6. Decidir entre completar e reverter

Duas saídas legítimas, uma decisão a tomar conscientemente:

| Saída | Quando costuma ser adequada |
| --- | --- |
| **Completar** | o que falhou é isolável, a causa é conhecida, o estado parcial é consistente e o ambiente não é crítico |
| **Reverter** | há dependência quebrada, a causa não é clara, o ambiente é compartilhado ou produtivo, ou o estado parcial é inconsistente |

**Na dúvida, reverter.** Ver [operational-safety-policy.md](../knowledge/operational-safety-policy.md#10-reversão-de-alteração-incorreta).

Em nenhum dos dois casos aplicar correção "por cima" sem entender o estado.

### 7. Executar a recuperação escolhida

Com autorização compatível com o ambiente:

1. declarar o que será feito e qual o efeito esperado;
2. executar **uma** ação por vez, verificando o resultado antes da seguinte;
3. registrar cada passo com horário e resultado real;
4. para Flows, confirmar qual versão ficou ativa ao final;
5. para permissões, confirmar quem tem acesso ao quê ao final.

### 8. Revalidar

Recuperação sem revalidação é suposição.

- repetir os testes dos processos afetados, com resultado real;
- verificar os cenários críticos do ambiente, não apenas o componente que falhou;
- verificar se automações vizinhas continuam funcionais;
- verificar se integrações estão operando;
- confirmar que o estado final é o pretendido, componente a componente.

### 9. Escalonar quando necessário

Escalonar imediatamente, sem tentar resolver sozinho, quando houver:

- efeito em Produção;
- perda ou corrupção de dados;
- exposição indevida de dados;
- integração externa acionada indevidamente;
- trabalho de outra pessoa afetado;
- estado que não foi possível determinar após a investigação;
- necessidade de decisão funcional para escolher entre completar e reverter.

Informar: o que foi detectado, qual o estado atual conhecido, o que já foi feito, qual decisão é necessária e quais alternativas existem.

### 10. Registrar o encerramento

No projeto atual:

```text
Operação que falhou e horário
Causa identificada ou hipótese remanescente
Estado parcial encontrado, item a item
Decisão tomada: completar ou reverter, e por quem
Passos de recuperação executados, com resultado real
Revalidação executada e resultado
Efeitos não revertidos e por quê
Pendências e responsáveis
Ação preventiva recomendada
```

---

## Evidências

Saída completa da operação que falhou; relatório do job quando houver; inventário do que foi aplicado, falhou e não foi tentado; identificação da org e da branch; registro de cada passo de recuperação; resultado real da revalidação.

## Riscos

| Risco | Consequência | Mitigação |
| --- | --- | --- |
| Repetir a operação automaticamente | duplicação de efeitos e perda da evidência | interromper e diagnosticar antes |
| "Corrigir por cima" | resíduo da tentativa errada permanece | reverter ao estado anterior |
| Comando destrutivo para "limpar" | perda de trabalho não relacionado | reverter artefato a artefato |
| Evidência perdida | causa nunca identificada, recorrência | capturar antes de recuperar |
| Recuperação no ambiente errado | segundo incidente | confirmar org antes de agir |
| Componente não tentado tratado como aplicado | dependência quebrada silenciosa | inventário com três categorias |
| Dados alterados tratados como reversíveis por deploy | inconsistência permanente | plano específico de dados |

## Rollback

Este runbook **é** o procedimento de recuperação. Quando a decisão for reverter:

1. usar o commit-base registrado no início da demanda;
2. reverter os artefatos afetados, individualmente;
3. reativar a versão anterior dos Flows, registrada antes da operação;
4. reverter passos manuais aplicados;
5. repetir os testes dos processos afetados;
6. registrar o que **não** foi revertido e por quê.

**Efeitos não reversíveis:** dados alterados ou criados, integrações acionadas, notificações enviadas, pacotes instalados, configurações em sistemas externos.

## Critérios de conclusão

- [ ] Operação interrompida sem repetição automática.
- [ ] Evidências capturadas e salvas no projeto.
- [ ] Org e branch confirmadas.
- [ ] Inventário completo: aplicado, falhou, não tentado.
- [ ] Tipo de falha classificado.
- [ ] Decisão entre completar e reverter tomada com autorização.
- [ ] Recuperação executada passo a passo, com resultado registrado.
- [ ] Revalidação executada com resultado real.
- [ ] Escalonamento realizado quando aplicável.
- [ ] Encerramento registrado com pendências e ação preventiva.

## Ações proibidas

Repetir automaticamente a operação que falhou; aplicar correção sem entender o estado; usar comandos destrutivos para limpar o ambiente; descartar alterações locais ou trabalho de terceiros; recuperar em Produção sem autorização explícita; executar correção em massa de dados sem plano próprio; declarar o incidente encerrado sem revalidação; gravar evidências na Salesforce-AI-Base.

## Referências

[operational-safety-policy.md](../knowledge/operational-safety-policy.md) · [environment-safety.md](../knowledge/environment-safety.md) · [instruction-precedence.md](../knowledge/instruction-precedence.md) · [salesforce-development-principles.md](../knowledge/salesforce-development-principles.md) · [retrieve-and-deploy-policy.md](../knowledge/retrieve-and-deploy-policy.md) · [resolve-org-repository-drift.md](./resolve-org-repository-drift.md) · [handle-metadata-conflict.md](./handle-metadata-conflict.md) · [emergency-hotfix.md](./emergency-hotfix.md)

## Critérios de revisão

Revisar após qualquer falha parcial cujo procedimento de recuperação tenha se mostrado insuficiente, e quando novos tipos de operação com efeito externo forem incorporados ao fluxo do time.
