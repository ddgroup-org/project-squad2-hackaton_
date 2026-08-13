---
title: "Convenções de nomenclatura"
description: "Padrões de nomes para branches, commits, Pull Requests, metadados Salesforce, código, manifests e documentação."
category: "knowledge"
status: "active"
version: "1.1"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - naming
  - conventions
  - clean-code
applies_to:
  - global
source_of_truth: true
source_references:
  - desenvolvimento.md
  - metaprompt-salesforce.md
---

# Convenções de nomenclatura

## Objetivo

Padronizar nomes de branches, commits, Pull Requests, metadados Salesforce, código e artefatos de apoio, para que qualquer pessoa do time entenda a função de um artefato pelo nome.

## Escopo

Aplica-se a projetos que ainda não possuem convenção própria. **Quando o projeto já tiver um padrão consistente, o padrão do projeto prevalece.** Convenções nunca devem ser trocadas no meio de um repositório apenas por preferência: inconsistência custa mais do que um padrão imperfeito.

## Princípios

- o nome descreve a intenção, não a implementação;
- sem abreviações ambíguas;
- idioma consistente dentro do repositório;
- sem prefixo de cliente, cliente-projeto ou sigla corporativa nesta base — se o projeto exigir prefixo, ele é definido no `CLAUDE.md` do repositório;
- nomes de API mantêm os sufixos oficiais da plataforma (`__c`, `__r`, `__e`, `__mdt`, `__x`).

## Estilos por tipo de artefato

```text
PascalCase        classes Apex, LWC (nome do componente em metadata), objetos e campos customizados
camelCase         métodos, variáveis, propriedades, pasta de LWC
UPPER_SNAKE_CASE  constantes
kebab-case        branches, nomes de arquivos de documentação, scripts
```

---

## 1. Git

### 1.1 Branches

**Padrão de fallback**, aplicável apenas quando o projeto não tiver convenção própria:

```text
feature/{ID-DEMANDA}-{descricao-curta}
fix/{ID-DEMANDA}-{descricao-curta}
release/{VERSAO-OU-DATA}
hotfix/{ID-INCIDENTE}-{descricao-curta}
```

Regras: minúsculas, `kebab-case` na descrição, sem acentos, sem espaços, descrição curta e específica. O identificador da demanda é o elo de rastreabilidade — ver [github-development-workflow.md](./github-development-workflow.md#1-o-fluxo-do-projeto-vem-primeiro).

> **Confirmar no projeto antes de usar:** convenção real de nomes de branch, nomes das branches-base, formato do identificador da demanda e prefixos adicionais exigidos pela pipeline.

**Nunca renomear ou recriar branches existentes para adequá-las a este padrão.** Convenção divergente e consistente é preferível a convenção "correta" e inconsistente.

### 1.2 Commits

Formato recomendado:

```text
{tipo}({escopo}): {descrição no imperativo}

{corpo opcional explicando o porquê}

Ref: {ID-DEMANDA}
```

Tipos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `revert`.

Boas práticas: descrição no imperativo ("adiciona", "corrige"), primeira linha curta e objetiva, corpo explicando o motivo quando a mudança não for autoexplicativa, um propósito por commit.

### 1.3 Pull Requests

```text
[{ID-DEMANDA}] {Título objetivo da entrega}
```

O corpo segue [pull-request-uat-template.md](../templates/pull-request-uat-template.md) ou [pull-request-production-template.md](../templates/pull-request-production-template.md).

---

## 2. Apex

### 2.1 Classes

`PascalCase`, substantivo que descreve a responsabilidade. Sufixos por papel arquitetural:

```text
{Dominio}Service        regra de negócio
{Dominio}Selector       consultas SOQL
{Dominio}Repository     acesso a dados quando o projeto usar esse padrão
{Dominio}Controller     entrada para LWC, Aura ou Visualforce
{Dominio}Handler        tratamento de trigger
{Dominio}TriggerHandler tratamento de trigger, quando o projeto usar esse sufixo
{Dominio}Batch          Batch Apex
{Dominio}Queueable      Queueable
{Dominio}Schedulable    Scheduled Apex
{Dominio}Invocable      classe invocável por Flow
{Dominio}Mock           implementação de mock para teste
{Dominio}Util           utilitário sem estado
```

> Confirmar no projeto: o conjunto de sufixos em uso. Não introduzir um novo padrão de camadas em repositório que já segue outro consistente.

### 2.2 Interfaces

`PascalCase`, descrevendo capacidade. O projeto define se usa prefixo `I` — verificar antes de criar. Sem prefixo: `PaymentGateway`. Com prefixo: `IPaymentGateway`. Consistência interna importa mais que a escolha.

### 2.3 Triggers

```text
{ObjectApiName}Trigger
```

Um trigger por objeto, com a lógica delegada ao handler. Ver [apex-standards.md](./apex-standards.md).

### 2.4 Classes de teste

```text
{ClasseTestada}Test
```

Métodos de teste descrevem o cenário e o resultado esperado:

```apex
@IsTest
static void deveRetornarErroQuandoUsuarioSemPermissao() { }

@IsTest
static void deveProcessarLoteCompletoEmOperacaoBulk() { }
```

### 2.5 Métodos, variáveis e constantes

- métodos: `camelCase`, verbo no início (`calcularTotal`, `buscarRegistrosAtivos`);
- métodos que retornam booleano: prefixo de pergunta (`isAtivo`, `hasPermissao`, `podeExecutar`) — manter um único idioma dentro do repositório;
- variáveis: `camelCase`, descritivas; coleções no plural (`contas`, `idsProcessados`); mapas indicando chave e valor (`contaPorId`, `itensPorPedidoId`);
- constantes: `UPPER_SNAKE_CASE`, declaradas `static final`;
- evitar nomes de uma letra fora de laços curtos.

---

## 3. Lightning Web Components

```text
pasta do componente     camelCase          ex.: accountSummaryPanel
nome em metadata        camelCase          igual ao da pasta
classe JavaScript       PascalCase         ex.: AccountSummaryPanel
propriedades públicas   camelCase          expostas em HTML como kebab-case
```

Eventos customizados: nome em minúsculas, sem prefixo `on`, sem camelCase — o padrão da plataforma é minúsculo, e nomes com maiúsculas não são capturados de forma consistente em templates.

```javascript
this.dispatchEvent(new CustomEvent('recordselect', { detail: { recordId } }));
```

No template: `onrecordselect={handleRecordSelect}`. Handlers seguem `handle{Evento}`.

Ver [lwc-standards.md](./lwc-standards.md).

---

## 4. Custom Labels

```text
{Contexto}_{Finalidade}
```

Exemplos genéricos: `Erro_Permissao_Negada`, `Mensagem_Registro_Salvo`, `Titulo_Painel_Resumo`.

Todo texto exibido ao usuário deve vir de Custom Label. O texto precisa estar gramaticalmente correto e no idioma definido para o projeto — erro de ortografia em texto visível é motivo de retrabalho.

---

## 5. Flows

### 5.1 Nome do Flow

```text
{Objeto}_{Evento}_{Finalidade}
```

Exemplos genéricos: `{ObjectApiName}_BeforeSave_CalculaCampos`, `{ObjectApiName}_AfterSave_CriaTarefa`, `{ObjectApiName}_Screen_CadastroGuiado`.

O nome deve permitir identificar objeto, momento de execução e propósito sem abrir o Flow.

### 5.2 Subflows

```text
Sub_{Dominio}_{Finalidade}
```

### 5.3 Elementos internos

`PascalCase` ou `Nome_Com_Underscore`, conforme o padrão do projeto, sempre descritivo:

```text
Get_{Objeto}_Por_{Criterio}
Update_{Objeto}_{Campo}
Decision_{CondicaoAvaliada}
Loop_Sobre_{Colecao}
Assignment_{Finalidade}
Fault_{Elemento}
```

Toda variável e todo elemento devem ter descrição preenchida. Ver [flow-standards.md](./flow-standards.md).

---

## 6. Permissões

```text
Permission Set          PS_{Dominio}_{Finalidade}
Permission Set Group    PSG_{Perfil_Funcional}
Custom Permission       CP_{Acao_Permitida}
```

O nome deve indicar o que é concedido, não quem recebe. Permissões nomeadas por cargo ou por pessoa envelhecem mal.

Ver [security-standards.md](./security-standards.md).

---

## 7. Configuração e integração

```text
Custom Metadata Type    {Dominio}_Config__mdt  ou  {Dominio}Setting__mdt
Registro de CMDT        {Contexto}_{Chave}
Named Credential        NC_{Sistema}_{Ambiente}
External Credential     EC_{Sistema}_{TipoAutenticacao}
Platform Event          {Dominio}_{Evento}__e
```

Named Credentials referenciam ambientes distintos por org — não versionar valores de endpoint específicos de um ambiente sem confirmar a política do projeto, e nunca versionar segredos. Ver [integration-standards.md](./integration-standards.md).

---

## 8. Objetos, campos e regras

```text
Objeto customizado      {Nome}__c            PascalCase, singular
Campo customizado       {Nome}__c            PascalCase, descritivo
Relacionamento          {Objeto}__c          nome do campo indicando o alvo
Record Type             {Contexto}_{Tipo}
Validation Rule         VR_{Objeto}_{RegraValidada}
```

Nomes de campo descrevem o dado, não a tela onde aparecem. `DataAprovacao__c` envelhece melhor que `CampoAba2__c`.

Rótulos (labels) são voltados ao usuário e seguem o idioma do projeto; API Names seguem a convenção técnica do repositório.

---

## 9. Manifests, scripts e documentação

```text
manifest/package-{id-demanda}.xml
manifest/destructiveChanges-{id-demanda}.xml
scripts/apex/{finalidade}.apex
scripts/shell/{finalidade}.sh
docs/{assunto}.md
docs/technical-analysis/{id-demanda}-{assunto}.md
docs/decisions/ADR-{NNN}-{titulo-curto}.md
```

Arquivos de documentação em `kebab-case`, sem acentos e sem espaços. ADRs numerados sequencialmente e nunca renumerados após criados.

Esses artefatos pertencem ao repositório do projeto. Nenhum deles deve ser criado nesta base global.

---

## 10. Padrões que exigem confirmação no projeto

Antes de aplicar, confirmar no `CLAUDE.md`, no `AGENTS.md` ou no código existente:

- [ ] idioma dos nomes técnicos (português ou inglês);
- [ ] formato do identificador da demanda;
- [ ] sufixos de camadas Apex em uso;
- [ ] uso de prefixo `I` em interfaces;
- [ ] prefixos obrigatórios de metadata definidos pelo projeto;
- [ ] convenção de nomes de Flow adotada;
- [ ] estrutura de pastas de documentação;
- [ ] convenção de mensagens de commit exigida pela pipeline.

Divergência entre esta base e o projeto se resolve a favor do projeto, salvo quando o padrão local violar segurança ou limites da plataforma.

---

## 11. Práticas proibidas

- nomes genéricos sem significado (`Teste`, `Novo`, `Temp`, `Aux2`, `ClasseNova`);
- abreviações não convencionadas;
- mistura de idiomas no mesmo artefato;
- nomes com data, número de chamado ou nome de pessoa embutidos em metadata permanente;
- prefixos de cliente em conteúdo global;
- renomear metadata existente sem avaliar dependências — renomear API Name é alteração de contrato, com impacto em Flows, fórmulas, relatórios, integrações e código.

---

## Referências cruzadas

- [apex-standards.md](./apex-standards.md) · [lwc-standards.md](./lwc-standards.md) · [flow-standards.md](./flow-standards.md) · [security-standards.md](./security-standards.md) · [integration-standards.md](./integration-standards.md) · [github-development-workflow.md](./github-development-workflow.md)

## Fontes oficiais recomendadas

Apex Developer Guide; Lightning Web Components Developer Guide; Salesforce Help para limites de nomenclatura de metadata (comprimento, caracteres permitidos e unicidade).

## Limitações

Limites de caracteres e regras de unicidade variam por tipo de metadata e podem mudar entre releases. Confirmar na documentação oficial antes de padronizar nomes longos.

## Critérios de revisão

Revisar quando o time adotar um novo padrão arquitetural, quando houver mudança de idioma padrão do projeto ou quando a pipeline passar a validar formato de commit.
