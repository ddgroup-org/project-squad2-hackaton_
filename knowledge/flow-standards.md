---
title: "Padrões de Flow"
description: "Critérios de uso, tipos de Flow, ordem de execução, bulkificação, fault paths, versionamento e testes de automação declarativa."
category: "knowledge"
status: "active"
version: "1.0"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - flow
  - automation
  - declarative
applies_to:
  - global
source_of_truth: true
source_references:
  - desenvolvimento.md
  - arquitetura.md
  - metaprompt-salesforce.md
---

# Padrões de Flow

## Objetivo

Definir quando usar Flow, como estruturá-lo com segurança e desempenho, e o que é avaliado em revisão de automação declarativa.

Este documento é a **fonte da verdade** para Flow. Segurança em [security-standards.md](./security-standards.md); alternativa programática em [apex-standards.md](./apex-standards.md).

## Escopo

Todos os tipos de Flow e a interação deles com o restante das automações do objeto.

---

## 1. Quando usar Flow

**Adequado quando:** a regra é declarativa; o processo tem complexidade baixa ou média; a manutenção por pessoas de administração é desejável; não há necessidade forte de lógica customizada; o volume é controlado; a automação pode ser documentada e testada.

**Não adequado quando:** a lógica exige estruturas de controle complexas; o volume é alto e o processamento pesado; há necessidade de controle transacional fino; há integração customizada com tratamento avançado de erro; o Flow resultante ficaria monolítico, frágil ou difícil de manter.

Um Flow com dezenas de elementos, decisões aninhadas e laços é sinal de que a regra ultrapassou o que o Flow sustenta bem. Nesse ponto, Apex ou uma solução híbrida com Apex Invocable é a escolha tecnicamente correta — **não forçar Flow por preferência declarativa**.

O inverso também vale: não escrever Apex para o que uma Validation Rule, um campo fórmula ou um Flow simples resolvem com menor risco.

---

## 2. Tipos de Flow

| Tipo | Uso principal | Observações |
| --- | --- | --- |
| **Record-Triggered — before save** | atualizar campos do próprio registro que disparou | mais eficiente; não executa DML adicional; não acessa registros relacionados para atualização |
| **Record-Triggered — after save** | atualizar registros relacionados, criar registros, chamar ações | executa após a gravação; pode disparar novas automações |
| **Screen Flow** | interação guiada com usuário | exige tratamento de estados e mensagens claras |
| **Autolaunched** | lógica reutilizável chamada por outros processos | bom candidato a subflow |
| **Scheduled** | processamento periódico | avaliar volume e limites do lote |
| **Platform Event-Triggered** | reação a evento | considerar reprocessamento e idempotência |
| **Orchestration** | processos de várias etapas com participantes distintos | avaliar necessidade real antes de adotar |

**Regra prática:** atualização de campo no próprio registro pertence a before save. Usar after save para isso gera DML desnecessário e aumenta o risco de recursão.

---

## 3. Critérios de entrada

Todo Flow acionado por registro deve ter critérios de entrada tão restritivos quanto possível.

- filtrar por condição de entrada em vez de decidir dentro do Flow;
- usar a opção de execução condicionada a mudança de campo quando a automação só faz sentido em alteração específica;
- evitar que o Flow seja avaliado em toda gravação do objeto quando ele só se aplica a um subconjunto de registros.

Critérios de entrada permissivos são a causa mais comum de consumo desnecessário de CPU em orgs com muitas automações.

---

## 4. Ordem de execução e densidade de automações

### 4.1 Order of Execution

A ordem em que Validation Rules, triggers, Flows, Workflow Rules legadas, Approval Processes e regras de atribuição são executados é definida pela plataforma. Alterar uma automação sem entender essa ordem produz efeitos difíceis de diagnosticar.

> Consultar o Order of Execution na documentação oficial correspondente à release do projeto antes de introduzir automação em objeto que já possui várias.

### 4.2 Trigger Order

Quando houver múltiplos Record-Triggered Flows no mesmo objeto e no mesmo momento, a ordem entre eles pode ser controlada. Sem definição explícita, a ordem não é garantida — e depender de ordem não garantida é defeito latente.

### 4.3 Densidade

Dois extremos são igualmente problemáticos:

- **Flow monolítico**: uma automação enorme que concentra todas as regras do objeto. Difícil de revisar, testar, versionar e reverter. Qualquer alteração tem risco alto.
- **Um Flow por regra pequena**: dezenas de automações no mesmo objeto e no mesmo momento. Ordem imprevisível, custo de CPU somado, diagnóstico caro e alto risco de duplicidade.

O equilíbrio: agrupar por **momento de execução e propósito coeso** (por exemplo, um before save e um after save por objeto, com subflows para blocos reutilizáveis), e documentar a intenção de cada um.

Antes de criar um Flow novo, verificar se já existe um que cubra o mesmo momento no mesmo objeto.

---

## 5. Bulkificação

Flows são executados em lote. A estrutura interna determina se isso funciona ou falha.

**Regra central: nenhum elemento de dados dentro de laço.**

```text
Incorreto:
  Loop sobre coleção
    └── Get Records          ← consulta por iteração
    └── Update Records       ← DML por iteração

Correto:
  Get Records (uma vez, com filtro por coleção)
  Loop sobre coleção
    └── Assignment (monta a coleção de saída)
  Update Records (uma vez, com a coleção)
```

- consultas fora do laço, filtrando por coleção de identificadores;
- Assignment dentro do laço apenas para montar coleções;
- operações de criação, atualização e exclusão fora do laço, com a coleção completa;
- limitar consultas ao que é necessário: selecionar apenas os campos usados e aplicar filtro adequado;
- validar o comportamento com volume real, não apenas com um registro.

---

## 6. Recursão

Um Flow after save que atualiza o registro que o disparou reinicia o ciclo de automações. Sintomas: limites atingidos sob volume, atualizações duplicadas, comportamento intermitente.

Prevenção:

- atualizar o próprio registro em before save, não em after save;
- restringir critérios de entrada por mudança de campo específica;
- evitar cadeias em que o Flow A atualiza um registro que dispara o Flow B que atualiza o registro original;
- mapear o caminho completo antes de adicionar automação em objeto com muitas existentes.

---

## 7. Fault paths

Todo elemento que acessa dados ou chama ação externa precisa de fault path. Sem ele, a falha aparece como erro genérico e sem contexto para o usuário, e o diagnóstico depende de log de sistema.

O fault path deve, no mínimo: registrar o erro de forma recuperável, apresentar mensagem compreensível ao usuário (em Screen Flow) e evitar que o processo termine em estado inconsistente.

Elementos que exigem fault path: Get Records, Create Records, Update Records, Delete Records, Apex Action, chamadas externas e subflows que executam operações de dados.

---

## 8. Contexto de execução e segurança

- Flows acionados por registro executam, por padrão, em contexto de sistema — o que significa que podem acessar e alterar dados além do alcance do usuário;
- Screen Flows executam com as permissões do usuário que os inicia, salvo configuração em contrário;
- a configuração de contexto do Flow deve ser uma escolha consciente, não o padrão aceito por omissão;
- Flows acionados por usuário exigem acesso concedido por Permission Set;
- Flow que expõe ou altera dado sensível merece a mesma revisão de segurança que código.

Ver [security-standards.md](./security-standards.md).

---

## 9. Versionamento e ativação

- toda alteração gera nova versão; a versão anterior permanece disponível;
- **registrar qual versão estava ativa antes da alteração** — esse é o mecanismo prático de rollback do Flow;
- ativação e desativação de Flow fora de DEV exigem autorização explícita;
- desativar um Flow em uso muda comportamento imediatamente: exigir evidência de que não há uso atual ou de que o comportamento foi substituído;
- a versão ativa é parte do metadata implantado — confirmar, após o deploy, qual versão ficou ativa no ambiente de destino.

---

## 10. Documentação dos elementos

- descrição preenchida no Flow, explicando propósito e critério de disparo;
- descrição em cada elemento não trivial;
- nomes de elementos e variáveis descritivos, seguindo [naming-conventions.md](./naming-conventions.md#5-flows);
- registro das dependências: objetos, campos, subflows, classes invocáveis e permissões.

Flow sem documentação interna transfere para quem for mantê-lo o custo de reconstituir a intenção original a partir do diagrama.

---

## 11. Testes

Flow precisa ser testado como qualquer automação. Ver [testing-standards.md](./testing-standards.md).

Cenários mínimos:

- caminho positivo com os critérios de entrada satisfeitos;
- caminho negativo, em que o Flow **não** deve executar;
- execução em massa;
- fault path acionado;
- usuário com permissões diferentes, quando o contexto for relevante;
- regressão nos processos relacionados ao objeto.

Flow Test permite automatizar cenários de Flows acionados por registro. A disponibilidade e os tipos suportados variam por release.

> Confirmar os tipos de Flow suportados por Flow Test na documentação oficial da release do projeto. Quando não houver suporte, registrar o plano de teste manual com evidências.

---

## 12. Antipadrões

| Antipadrão | Problema |
| --- | --- |
| Get, Update, Create ou Delete dentro de laço | falha sob volume |
| Atualização do próprio registro em after save | DML desnecessário e risco de recursão |
| Ausência de fault path | falha silenciosa ou erro incompreensível |
| Critérios de entrada permissivos | execução desnecessária e consumo de CPU |
| Flow monolítico | risco alto em qualquer alteração |
| Um Flow por regra mínima | ordem imprevisível e custo somado |
| Duplicidade entre Flow e Apex | comportamento divergente |
| Elementos sem descrição | manutenção cara |
| Dependência de ordem não configurada | defeito latente |
| Desativar Flow sem verificar uso | quebra funcional imediata |
| Texto fixo em mensagens | impossível de traduzir e revisar |

---

## 13. Checklist de revisão

**Decisão**
- [ ] Flow é a ferramenta adequada; alternativas avaliadas.
- [ ] Tipo de Flow correto para o momento de execução.
- [ ] Não há automação existente cobrindo o mesmo propósito.

**Estrutura**
- [ ] Critérios de entrada restritivos.
- [ ] Nenhum elemento de dados dentro de laço.
- [ ] Coleções usadas para operações em massa.
- [ ] Fault paths em todos os elementos de dados e ações.
- [ ] Elementos e variáveis nomeados e descritos.

**Execução**
- [ ] Order of Execution considerada.
- [ ] Trigger Order definida quando houver múltiplos Flows.
- [ ] Risco de recursão avaliado.
- [ ] Densidade de automações do objeto avaliada.

**Segurança**
- [ ] Contexto de execução escolhido conscientemente.
- [ ] Acesso ao Flow definido por Permission Set, quando aplicável.
- [ ] Dados sensíveis tratados adequadamente.

**Entrega**
- [ ] Testes positivo, negativo, em massa e de fault path executados.
- [ ] Versão anterior registrada para rollback.
- [ ] Plano de ativação definido.
- [ ] Impacto em integrações e cargas avaliado.

---

## Referências cruzadas

- [apex-standards.md](./apex-standards.md) · [security-standards.md](./security-standards.md) · [testing-standards.md](./testing-standards.md) · [naming-conventions.md](./naming-conventions.md) · [salesforce-development-principles.md](./salesforce-development-principles.md)

## Fontes oficiais recomendadas

Documentação oficial de Flow (Flow Builder); Salesforce Help para Order of Execution e Trigger Order; Salesforce Platform Decision Guides para escolha entre automações; Salesforce Well-Architected.

## Limitações

Tipos de Flow disponíveis, recursos do Flow Builder, suporte do Flow Test e limites de execução variam por release. Confirmar na documentação oficial correspondente à release do projeto.

## Critérios de revisão

Revisar a cada release com mudanças relevantes em Flow, quando o projeto adotar novo padrão de automação ou quando a densidade de automações de um objeto crítico aumentar.
