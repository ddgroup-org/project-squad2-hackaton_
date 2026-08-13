---
title: "Runbook — Deploy direcionado para a org DEV"
description: "Procedimento para enviar código e metadata locais à org DEV com validação, execução de testes e rollback controlado."
category: "runbook"
status: "active"
version: "1.1"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - deploy
  - cli
  - runbook
applies_to:
  - global
source_of_truth: false
source_references:
  - desenvolvimento.md
  - execucao.md
---

# Runbook — Deploy direcionado para a org DEV

## Objetivo

Enviar à org DEV apenas os componentes alterados localmente, com validação prévia, execução dos testes relevantes e possibilidade de reversão.

## Quando utilizar

Após implementar ou ajustar código e metadata no repositório local, para validar o comportamento na org de desenvolvimento.

**Este runbook não se aplica a UAT nem a Produção**, que recebem alterações exclusivamente pela pipeline.

## Pré-condições

- feature branch da demanda ativa;
- implementação local concluída ou em ponto verificável;
- org DEV confirmada;
- componentes a implantar identificados;
- autorização para deploy em DEV, quando não fizer parte explícita da tarefa.

## Entradas

```text
{DEV_ORG_ALIAS}     alias da org de desenvolvimento
{METADATA_TYPE}     tipo de metadata
{COMPONENT_NAME}    nome do componente
{MANIFEST_PATH}     manifest da demanda, quando houver
{TEST_CLASS_NAME}   classes de teste a executar
```

## Verificações iniciais

- [ ] Branch correta ativa.
- [ ] Alterações locais revisadas e limitadas ao escopo.
- [ ] Nenhum segredo no que será implantado.
- [ ] Org confirmada.
- [ ] Dependências dos componentes mapeadas.

---

## Procedimento

### 1. Revisar o que será implantado

```bash
git status
git diff
```

Confirmar que apenas arquivos da demanda serão enviados. Arquivo fora do escopo no deploy leva alteração indevida à org compartilhada.

### 2. Verificar segredos

Inspecionar o conjunto quanto a valores reais de token, senha, client secret, chave privada ou certificado.

**Encontrando segredo:** interromper, remover o valor e tratar a credencial como comprometida antes de qualquer operação.

### 3. Confirmar a org

```bash
sf org list
sf org display --target-org {DEV_ORG_ALIAS}
```

Confirmar alias, username, Organization ID, instance URL e tipo de ambiente.

**Ponto de decisão:** qualquer indício de que a org não é a DEV esperada — ou de que é Produção — **interrompe o procedimento**. Na dúvida, tratar como o ambiente de maior criticidade.

### 4. Verificar dependências e concorrência

- os componentes referenciados existem na org ou estão incluídos no deploy;
- a ordem de deploy foi considerada quando a operação for fracionada;
- nenhuma outra demanda está atuando nos mesmos componentes.

**Ponto de decisão:** em sandbox compartilhada, verificar se a versão que está na org foi alterada por outra pessoa desde o último alinhamento. Havendo divergência, **não sobrescrever**: preservar as duas versões, apresentar o conflito e coordenar.

### 5. Validar antes de aplicar

```bash
sf project deploy validate \
  --manifest {MANIFEST_PATH} \
  --target-org {DEV_ORG_ALIAS} \
  --test-level RunSpecifiedTests \
  --tests {TEST_CLASS_NAME}
```

A validação executa a verificação completa sem persistir a alteração, antecipando falhas de dependência, de teste e de metadata.

**Ponto de decisão:** falha na validação interrompe o procedimento. Corrigir a causa — não repetir o comando esperando resultado diferente.

### 6. Executar o deploy

Por componente:

```bash
sf project deploy start \
  --metadata {METADATA_TYPE}:{COMPONENT_NAME} \
  --target-org {DEV_ORG_ALIAS}
```

Por manifest, com testes:

```bash
sf project deploy start \
  --manifest {MANIFEST_PATH} \
  --target-org {DEV_ORG_ALIAS} \
  --test-level RunSpecifiedTests \
  --tests {TEST_CLASS_NAME}
```

Acompanhamento, quando a operação for assíncrona:

```bash
sf project deploy report --target-org {DEV_ORG_ALIAS}
sf project deploy resume --job-id {DEPLOY_JOB_ID}
```

### 7. Tratar falha parcial

**Ponto de decisão crítico.** Se o deploy falhar após processar parte dos componentes:

1. interromper as ações seguintes;
2. identificar o que foi aplicado e o que falhou;
3. verificar se a org ficou em estado inconsistente;
4. **não repetir o deploy automaticamente**;
5. **não aplicar correção "por cima"** sem entender o estado;
6. restaurar o estado anterior quando seguro e autorizado;
7. registrar o resultado e as pendências.

### 8. Executar e verificar os testes

```bash
sf apex run test \
  --target-org {DEV_ORG_ALIAS} \
  --class-names {TEST_CLASS_NAME} \
  --result-format human \
  --wait 10
```

Reportar o **resultado real**: métodos que passaram, métodos que falharam e cobertura obtida. Não declarar sucesso sem a saída correspondente.

### 9. Executar a análise estática

Executar a ferramenta de análise estática configurada no projeto sobre o código criado ou alterado e tratar as violações críticas e altas. Falsos positivos devem ser documentados com justificativa, nunca suprimidos silenciosamente.

**Ponto de decisão:** ferramenta indisponível no ambiente → registrar a limitação, o risco residual e como executá-la posteriormente.

### 10. Validar o comportamento na org

Executar os cenários de aceite definidos no plano da demanda e registrar as evidências.

### 11. Retrieve do que foi configurado pelo Setup

Se, durante a validação, algo tiver sido ajustado pela interface do Salesforce, recuperar essas alterações seguindo [retrieve-from-dev.md](./retrieve-from-dev.md).

### 12. Registrar as evidências

No projeto atual:

```text
Data e hora
Org: alias, username, Organization ID, tipo de ambiente
Comandos executados
Componentes implantados
Resultado da validação
Resultado do deploy e identificador do job
Testes executados e resultado real
Resultado da análise estática
Cenários validados
Falhas, limitações e pendências
```

---

## Evidências

Saída da validação e do deploy; identificador do job; resultado real dos testes com cobertura; resultado da análise estática; evidências funcionais dos cenários de aceite.

## Riscos

| Risco | Consequência | Mitigação |
| --- | --- | --- |
| Org errada | alteração em ambiente indevido | confirmação por quatro atributos |
| Arquivo fora do escopo | alteração indevida em sandbox compartilhada | revisar diff antes do deploy |
| Sobrescrita de trabalho de outra pessoa | perda de trabalho | verificar concorrência antes |
| Falha parcial | org em estado inconsistente | interromper, diagnosticar, não repetir |
| Dependência ausente | falha de deploy ou comportamento incorreto | mapear dependências e ordem |
| Teste não executado | defeito descoberto em UAT | executar e reportar resultado real |
| Segredo implantado | vazamento | verificar antes do deploy |

## Rollback

1. identificar o commit-base registrado no início da demanda;
2. restaurar localmente a versão anterior dos componentes afetados;
3. executar deploy direcionado da versão anterior para a mesma org;
4. para Flows, reativar a versão anterior registrada;
5. repetir os testes relevantes;
6. registrar o que foi revertido e por quê.

**Efeitos não revertidos por deploy:** dados alterados, registros criados, automações executadas, integrações acionadas e configurações externas. Esses casos exigem plano específico.

## Critérios de conclusão

- [ ] Org confirmada.
- [ ] Escopo limitado aos componentes da demanda.
- [ ] Nenhum segredo implantado.
- [ ] Validação executada com sucesso.
- [ ] Deploy concluído sem falha parcial pendente.
- [ ] Testes executados com resultado real reportado.
- [ ] Análise estática executada e apontamentos tratados.
- [ ] Cenários de aceite validados na org.
- [ ] Alterações de Setup recuperadas para o repositório.
- [ ] Evidências registradas no projeto.

## Ações proibidas

Deploy em UAT ou Produção; deploy do projeto inteiro como rotina; sobrescrever trabalho de outra pessoa sem coordenação; repetir automaticamente deploy após falha parcial; declarar sucesso sem resultado real de testes; executar destructive changes sem autorização; gravar artefatos na Salesforce-AI-Base.

## Referências

[retrieve-and-deploy-policy.md](../knowledge/retrieve-and-deploy-policy.md) · [environment-safety.md](../knowledge/environment-safety.md) · [operational-safety-policy.md](../knowledge/operational-safety-policy.md) · [testing-standards.md](../knowledge/testing-standards.md) · [salesforce-development-principles.md](../knowledge/salesforce-development-principles.md) · [retrieve-from-dev.md](./retrieve-from-dev.md) · [promote-to-uat.md](./promote-to-uat.md)
