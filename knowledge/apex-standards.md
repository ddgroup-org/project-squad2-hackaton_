---
title: "Padrões de desenvolvimento Apex"
description: "Arquitetura de classes, bulkificação, governor limits, assincronismo, tratamento de erros e antipadrões em Apex."
category: "knowledge"
status: "active"
version: "1.0"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - apex
  - clean-code
  - performance
  - governor-limits
applies_to:
  - global
source_of_truth: true
source_references:
  - arquitetura.md
  - desenvolvimento.md
  - metaprompt-salesforce.md
---

# Padrões de desenvolvimento Apex

## Objetivo

Definir os padrões de arquitetura, performance, segurança e manutenibilidade aplicáveis a código Apex.

Este documento é a **fonte da verdade** para Apex. Segurança é resumida aqui e detalhada em [security-standards.md](./security-standards.md); testes, em [testing-standards.md](./testing-standards.md).

## Escopo

Classes, triggers, processamento assíncrono, callouts e tratamento de erros. Não define framework de trigger obrigatório: **quando o projeto já usa um padrão consistente, esse padrão prevalece**.

## Quando usar Apex

Apex é justificado quando há lógica complexa, alto volume, necessidade de controle transacional, integração customizada, tratamento avançado de erro, requisitos de reutilização técnica ou quando uma solução declarativa ficaria frágil e difícil de manter.

Não usar Apex quando uma configuração ou um Flow resolve com menor risco. Também não evitar Apex quando ele for tecnicamente superior: um Flow monolítico com dezenas de elementos e lógica condicional profunda é pior que uma classe bem estruturada. Ver [salesforce-development-principles.md](./salesforce-development-principles.md#17-native-first-sem-dogma).

---

## 1. Arquitetura de classes

### 1.1 Separação de responsabilidades

| Camada | Responsabilidade | Não faz |
| --- | --- | --- |
| Trigger | delegar | conter lógica |
| Handler | orquestrar por evento de trigger | regra de negócio detalhada, SOQL direto |
| Service | regra de negócio | consulta direta, apresentação |
| Selector | consultas SOQL | regra de negócio |
| Controller | entrada de LWC, Aura ou Visualforce | regra de negócio |
| Domain | comportamento do objeto | orquestração entre objetos |
| Util | funções sem estado | acesso a dados |

Essa separação é uma referência, não um dogma. O objetivo é que a lógica seja localizável, testável isoladamente e revisável sem ler o sistema inteiro.

### 1.2 Trigger

Um trigger por objeto, sem lógica, delegando ao handler:

```apex
trigger AccountTrigger on Account (before insert, before update, after insert, after update) {
    new AccountTriggerHandler().run();
}
```

Motivos: múltiplos triggers no mesmo objeto tornam a ordem de execução indeterminada, e lógica dentro do trigger é praticamente impossível de testar isoladamente.

### 1.3 Controle de recursão

Automações que atualizam registros do próprio objeto podem reentrar. Controlar com flag estática ou com verificação do estado processado:

```apex
public class TriggerContext {
    private static Set<Id> processados = new Set<Id>();

    public static Boolean jaProcessado(Id registroId) {
        return processados.contains(registroId);
    }

    public static void marcarProcessado(Set<Id> ids) {
        processados.addAll(ids);
    }
}
```

Variáveis estáticas vivem pela duração da transação. Isso é adequado para evitar reentrância na mesma transação e insuficiente para controlar processamento entre transações distintas — nesse caso, o controle precisa estar no dado.

### 1.4 Documentação de decisões não óbvias

Comentar o **porquê**, não o **o quê**. Merecem comentário: uso de `without sharing`, decisão por processamento assíncrono, tratamento específico de limite, contorno de comportamento conhecido da plataforma e regra de negócio contraintuitiva.

---

## 2. Bulkificação

Toda lógica deve funcionar para 1, 200 e para o volume real de operações em lote, cargas de dados e integrações.

### 2.1 SOQL e DML fora de laços

```apex
// Incorreto — consulta e DML dentro do laço
for (Opportunity opp : opps) {
    Account acc = [SELECT Id, Name FROM Account WHERE Id = :opp.AccountId];
    opp.Description = acc.Name;
    update opp;
}

// Correto — consulta única, DML único
Set<Id> accountIds = new Set<Id>();
for (Opportunity opp : opps) {
    accountIds.add(opp.AccountId);
}

Map<Id, Account> contaPorId = new Map<Id, Account>(
    [SELECT Id, Name FROM Account WHERE Id IN :accountIds]
);

List<Opportunity> paraAtualizar = new List<Opportunity>();
for (Opportunity opp : opps) {
    Account acc = contaPorId.get(opp.AccountId);
    if (acc != null) {
        opp.Description = acc.Name;
        paraAtualizar.add(opp);
    }
}

if (!paraAtualizar.isEmpty()) {
    update paraAtualizar;
}
```

### 2.2 Coleções

- `Map` para busca por chave em vez de laço aninhado;
- `Set` para deduplicar e testar pertinência;
- verificar se a coleção está vazia antes do DML;
- não acumular volume desnecessário em memória.

### 2.3 Consultas seletivas

- selecionar apenas os campos usados;
- filtrar por campos indexados quando possível;
- evitar consultas sem filtro em objetos grandes;
- tratar retorno vazio explicitamente;
- limitar profundidade de relacionamentos em subqueries.

---

## 3. Governor limits

| Limite | Sintoma | Mitigação |
| --- | --- | --- |
| Consultas SOQL por transação | falha em operação em lote | consulta única com `IN`, uso de mapas |
| Linhas retornadas | falha em objetos grandes | filtros seletivos, `LIMIT`, Batch Apex |
| Instruções DML | falha em processamento em massa | agrupar DML por coleção |
| Linhas de DML | falha em cargas | Batch Apex |
| Tempo de CPU | erro intermitente sob volume | reduzir laços aninhados, simplificar processamento, mover para assíncrono |
| Heap | falha em processamento de coleções grandes | processar em blocos, evitar acumular listas |
| Callouts por transação | falha em integração | agrupar chamadas, processar de forma assíncrona |

Os valores numéricos variam por tipo de transação e por release.

> Consultar os limites vigentes no Apex Developer Guide correspondente à API Version do projeto.

Tempo de CPU é o limite mais frequentemente atingido em orgs maduras, porque é consumido pelo conjunto de automações da transação — inclusive Flows e triggers de outras demandas. Avaliar o custo agregado, não apenas o do componente que está sendo desenvolvido.

---

## 4. Segurança

Resumo — detalhamento em [security-standards.md](./security-standards.md):

- declarar `with sharing`, `inherited sharing` ou `without sharing` explicitamente em toda classe;
- `without sharing` exige justificativa registrada;
- avaliar CRUD e FLS quando houver exposição de dados a usuários;
- escolher conscientemente entre execução em modo usuário e modo sistema;
- não concatenar entrada não confiável em SOQL dinâmica;
- validar entradas no servidor;
- não expor detalhes internos em mensagens de erro;
- nenhuma credencial ou Id fixo no código.

---

## 5. Tratamento de exceções

### 5.1 Diretrizes

- capturar exceções específicas antes de genéricas;
- nunca engolir exceção silenciosamente;
- não usar exceção como fluxo de controle;
- distinguir erro funcional (regra de negócio) de erro técnico (falha de infraestrutura);
- usar exceções customizadas para erros de domínio;
- registrar contexto suficiente para investigar.

```apex
public class RegraNegocioException extends Exception {}

try {
    processar(registros);
} catch (DmlException e) {
    Logger.registrar('Falha ao processar registros', e, registros);
    throw new RegraNegocioException(Label.Erro_Processamento_Indisponivel);
}
```

### 5.2 Transações e operações parciais

Uma exceção não capturada desfaz a transação inteira. Quando o negócio exigir processamento parcial — gravar o que é válido e reportar o que falhou — usar operações com `allOrNone = false` e tratar o resultado registro a registro. Essa decisão pertence ao negócio, não ao código: processar parcialmente sem alinhamento gera inconsistência silenciosa.

`Database.Savepoint` permite reverter parte da transação, mas consome limite e adiciona complexidade. Usar apenas quando a reversão parcial for realmente necessária.

### 5.3 Idempotência

Processos que podem ser reexecutados — integrações, jobs, eventos, retries — precisam produzir o mesmo resultado quando repetidos. Estratégias: chave externa única, verificação de estado antes da ação, registro de processamento já realizado.

---

## 6. Processamento assíncrono

Assincronismo resolve limites e desacopla processos. Também adiciona complexidade de rastreabilidade e de teste. Usar quando necessário, não por precaução.

| Mecanismo | Adequado para | Cuidados |
| --- | --- | --- |
| `@future` | operação simples fora da transação | sem encadeamento, parâmetros primitivos, difícil de rastrear; preferir Queueable |
| Queueable | trabalho assíncrono com estado, encadeável | limite de profundidade de encadeamento |
| Batch Apex | grandes volumes em blocos | escopo por execução, estado entre blocos exige `Database.Stateful` |
| Scheduled Apex | execução periódica | agendamento é metadata; alterações exigem cuidado no deploy |
| Platform Events | desacoplamento e integração orientada a evento | entrega e reprocessamento têm semântica própria |

Diretrizes:

- callouts a partir de trigger exigem contexto assíncrono;
- Queueable é preferível a `@future` na maioria dos casos por permitir estado e encadeamento;
- Batch Apex exige tratamento de falha por bloco: um bloco com erro não interrompe os demais;
- todo processo assíncrono precisa de estratégia de observabilidade — sem log, uma falha assíncrona passa despercebida.

> Confirmar limites de jobs assíncronos, profundidade de encadeamento e comportamento de retry na documentação oficial da release do projeto.

---

## 7. Callouts

- endpoint por Named Credential, nunca fixo no código;
- timeout explícito;
- tratamento de status HTTP, não apenas de exceção;
- correlation ID para rastreabilidade;
- mock obrigatório em testes;
- avaliar impacto no limite de callouts da transação.

Detalhamento em [integration-standards.md](./integration-standards.md).

---

## 8. Configuração e textos

- **Custom Metadata Type** para regras que mudam sem deploy e precisam ser versionáveis e implantáveis;
- **Custom Settings** para configuração hierárquica por perfil ou usuário, quando o projeto já usar esse mecanismo;
- **Custom Labels** para todo texto exibido ao usuário;
- **constantes** para valores reutilizados internamente;
- **nunca** Ids fixos: eles mudam entre orgs e quebram na promoção. Resolver por Developer Name, Record Type Developer Name ou consulta.

---

## 9. Logs

Registrar em processos com efeito externo, processamento assíncrono e integrações: identificador do registro, usuário, operação, momento, status, mensagem técnica e correlation ID quando houver.

Não registrar dados sensíveis. Log é evidência de investigação, não cópia do payload.

O mecanismo de log varia por projeto — plataforma própria, objeto customizado, Platform Event ou ferramenta de mercado. Confirmar o padrão no projeto antes de criar um novo.

---

## 10. Classes de teste

Toda classe Apex precisa de teste que comprove comportamento. O padrão completo está em [testing-standards.md](./testing-standards.md). Requisitos mínimos: massa própria, cenário positivo, cenário negativo, cenário em massa, verificação de permissões quando aplicável, asserts comportamentais e mocks para callouts.

---

## 11. Antipadrões

| Antipadrão | Problema |
| --- | --- |
| SOQL ou DML dentro de laço | falha sob volume |
| Trigger com lógica embutida | não testável isoladamente |
| Múltiplos triggers no mesmo objeto | ordem de execução indeterminada |
| `catch (Exception e) {}` vazio | falha silenciosa |
| Id fixo no código | quebra entre ambientes |
| `SeeAllData=true` para simplificar | teste dependente de dado da org |
| Classe monolítica | impossível de revisar e reutilizar |
| `without sharing` sem justificativa | exposição de dados |
| Consulta sem filtro em objeto grande | estouro de linhas |
| Lógica duplicada entre Flow e Apex | comportamento divergente e difícil de diagnosticar |
| Assincronismo desnecessário | complexidade e perda de rastreabilidade |
| Texto fixo no código | impossível de traduzir e revisar |

---

## 12. Checklist de revisão

**Arquitetura**
- [ ] Responsabilidades separadas e classe com propósito único.
- [ ] Trigger sem lógica, delegando ao handler.
- [ ] Padrão do projeto respeitado.
- [ ] Sem duplicação de lógica existente.

**Performance**
- [ ] Sem SOQL ou DML em laço.
- [ ] Coleções usadas adequadamente.
- [ ] Consultas seletivas e com campos necessários.
- [ ] Comportamento validado em cenário de 200 registros.
- [ ] Risco de CPU e heap avaliado.

**Segurança**
- [ ] Sharing declarado explicitamente.
- [ ] CRUD e FLS avaliados.
- [ ] Modo de execução escolhido conscientemente.
- [ ] Sem SOQL dinâmica insegura.
- [ ] Sem credenciais ou Ids fixos.

**Confiabilidade**
- [ ] Exceções tratadas com contexto.
- [ ] Recursão controlada.
- [ ] Idempotência avaliada em processos reexecutáveis.
- [ ] Logs suficientes e sanitizados.

**Testes**
- [ ] Cenários positivo, negativo e em massa cobertos.
- [ ] Asserts comportamentais.
- [ ] Mocks para callouts.
- [ ] Testes executados e resultado real reportado.
- [ ] Code Analyzer executado e apontamentos tratados.

---

## Referências cruzadas

- [salesforce-development-principles.md](./salesforce-development-principles.md) · [security-standards.md](./security-standards.md) · [testing-standards.md](./testing-standards.md) · [flow-standards.md](./flow-standards.md) · [integration-standards.md](./integration-standards.md) · [naming-conventions.md](./naming-conventions.md)

## Fontes oficiais recomendadas

Apex Developer Guide; Salesforce Well-Architected; Salesforce Platform Decision Guides (automação); Salesforce Code Analyzer Documentation; Salesforce Help para Order of Execution.

## Limitações

Valores de governor limits, sintaxe de modos de execução e comportamento de mecanismos assíncronos variam por release e por API Version. Confirmar na documentação oficial correspondente antes de tratar qualquer número desta página como definitivo.

## Critérios de revisão

Revisar a cada release relevante da Salesforce, ao adotar novo padrão arquitetural no projeto ou quando o Code Analyzer passar a sinalizar novas regras.
