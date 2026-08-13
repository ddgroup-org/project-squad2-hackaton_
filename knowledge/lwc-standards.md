---
title: "Padrões de desenvolvimento LWC"
description: "Critérios de uso, acesso a dados, estados de interface, acessibilidade, performance e testes em Lightning Web Components."
category: "knowledge"
status: "active"
version: "1.0"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - lwc
  - frontend
  - accessibility
  - slds
applies_to:
  - global
source_of_truth: true
source_references:
  - desenvolvimento.md
  - metaprompt-salesforce.md
  - arquitetura.md
---

# Padrões de desenvolvimento LWC

## Objetivo

Definir quando construir um Lightning Web Component, como acessar dados, quais estados de interface são obrigatórios e o que é avaliado em revisão.

Este documento é a **fonte da verdade** para LWC. Segurança de backend permanece em [security-standards.md](./security-standards.md); o Apex consumido segue [apex-standards.md](./apex-standards.md).

## Escopo

Componentes de interface em Lightning Experience, Experience Cloud e aplicações móveis Salesforce. Não cobre Aura, exceto quando houver interoperabilidade.

---

## 1. Antes de criar um componente

Avaliar, nesta ordem:

1. **Componente padrão da plataforma** — Related List, Path, Dynamic Forms, Lightning Record Page com componentes nativos resolvem grande parte das necessidades de tela sem código;
2. **Configuração declarativa** — Dynamic Forms e visibilidade condicional cobrem muitos casos que aparentam exigir componente customizado;
3. **Componente-base** (`lightning-*`) dentro de um LWC próprio — herda acessibilidade, responsividade e comportamento visual;
4. **Componente totalmente customizado** — apenas quando o requisito de interação, composição ou validação não for atendido pelas opções anteriores.

Componente customizado tem custo permanente: manutenção, acessibilidade, testes, compatibilidade com mudanças de release. Só vale quando entrega algo que a plataforma não entrega.

---

## 2. Acesso a dados

### 2.1 Ordem de preferência

| Mecanismo | Quando usar | Vantagem |
| --- | --- | --- |
| Lightning Data Service (`lightning-record-form`, `lightning-record-edit-form`, `lightning-record-view-form`) | CRUD de um registro | aplica FLS e sharing automaticamente, cache compartilhado, sem Apex |
| Adaptadores de UI API (`getRecord`, `getObjectInfo`, `getPicklistValues`) | leitura de registro e metadata | cache reativo, respeita permissões |
| GraphQL API via `@wire` | leitura de múltiplos registros com filtro e paginação | reduz chamadas Apex para consultas de leitura |
| Apex | regra de negócio, agregação, integração, operações complexas | controle total |

Usar Apex apenas quando os mecanismos declarativos não atenderem. Lightning Data Service aplica FLS e sharing sem código adicional; ao substituí-lo por Apex, essa responsabilidade passa a ser sua.

### 2.2 `@wire` e chamadas imperativas

**`@wire`** para dados que a interface exibe reativamente e que se beneficiam de cache:

```javascript
import { LightningElement, api, wire } from 'lwc';
import buscarResumo from '@salesforce/apex/ResumoController.buscarResumo';

export default class ResumoPainel extends LightningElement {
    @api recordId;
    dados;
    erro;
    carregando = true;

    @wire(buscarResumo, { registroId: '$recordId' })
    tratarResultado({ data, error }) {
        this.carregando = false;
        if (data) {
            this.dados = data;
            this.erro = undefined;
        } else if (error) {
            this.erro = error;
            this.dados = undefined;
        }
    }
}
```

**Chamada imperativa** para ações disparadas pelo usuário, operações com efeito colateral e casos em que é preciso controlar o momento da execução:

```javascript
async processar() {
    this.carregando = true;
    try {
        await executarAcao({ registroId: this.recordId });
        this.notificarSucesso();
    } catch (error) {
        this.erro = error;
    } finally {
        this.carregando = false;
    }
}
```

### 2.3 Cache

`@AuraEnabled(cacheable=true)` habilita cache no cliente e é requisito para uso com `@wire`. Consequências:

- o método **não pode** conter DML nem efeito colateral;
- o dado pode estar desatualizado — após uma alteração, atualizar explicitamente com o mecanismo de refresh apropriado;
- métodos que executam ações nunca devem ser marcados como `cacheable`.

---

## 3. Estados obrigatórios da interface

Todo componente que carrega ou envia dados precisa tratar quatro estados. A ausência de qualquer um deles é apontamento de revisão.

| Estado | Comportamento esperado |
| --- | --- |
| **Loading** | indicador visível enquanto a operação está em curso; sem tela travada ou vazia sem explicação |
| **Empty** | mensagem clara quando não há dados, distinta de erro; quando fizer sentido, ação sugerida |
| **Sucesso** | dado renderizado ou confirmação explícita da ação |
| **Erro** | mensagem compreensível ao usuário, sem detalhes internos, com caminho de recuperação |

```html
<template>
    <lightning-card title={titulo}>
        <template lwc:if={carregando}>
            <lightning-spinner alternative-text="Carregando" size="small"></lightning-spinner>
        </template>

        <template lwc:elseif={erro}>
            <div class="slds-p-around_medium" role="alert">
                <p class="slds-text-color_error">{mensagemErro}</p>
            </div>
        </template>

        <template lwc:elseif={semDados}>
            <p class="slds-p-around_medium slds-text-color_weak">
                Nenhum registro encontrado para os critérios atuais.
            </p>
        </template>

        <template lwc:else>
            <!-- conteúdo -->
        </template>
    </lightning-card>
</template>
```

Mensagens de erro devem vir de Custom Labels e nunca expor stack trace, nome de classe ou trecho de query.

---

## 4. Acessibilidade

Acessibilidade é requisito funcional, não refinamento posterior.

- todo controle interativo precisa de rótulo acessível;
- navegação completa por teclado, com ordem de foco previsível;
- foco gerenciado ao abrir e fechar modais, e devolvido ao elemento de origem;
- não transmitir informação apenas por cor;
- contraste adequado entre texto e fundo;
- mensagens de erro associadas ao campo correspondente;
- conteúdo dinâmico relevante anunciado por região `aria-live` ou `role="alert"`;
- imagens com texto alternativo; imagens decorativas marcadas como tal;
- elementos semânticos em vez de `div` com manipulador de clique.

Componentes-base `lightning-*` já implementam grande parte desses comportamentos — essa é uma das razões principais para preferi-los. Ao construir markup próprio, a responsabilidade passa a ser sua.

> Validar os critérios vigentes nas diretrizes oficiais de acessibilidade da Salesforce e do SLDS.

---

## 5. SLDS e apresentação

- usar classes utilitárias do SLDS em vez de CSS próprio para espaçamento, tipografia e grid;
- CSS customizado apenas para o que o SLDS não cobre, mantido no arquivo do componente;
- não sobrescrever estilos internos de componentes-base: essas estruturas mudam entre releases e a sobrescrita quebra silenciosamente;
- respeitar responsividade — o componente pode ser renderizado em coluna estreita, em app móvel e em Experience Cloud.

---

## 6. Arquitetura do componente

### 6.1 Separação entre apresentação e regra de negócio

Regra de negócio pertence ao backend. O componente cuida de interação, apresentação e orquestração de chamadas. Validação no cliente melhora a experiência; **não é controle de segurança** — a mesma validação precisa existir no servidor.

### 6.2 Imutabilidade

Objetos retornados por `@wire` são somente leitura. Modificá-los diretamente gera erro ou comportamento inconsistente. Trabalhar sobre cópias:

```javascript
const linhas = this.dados.map((item) => ({ ...item, selecionado: false }));
```

### 6.3 Comunicação entre componentes

| Situação | Mecanismo |
| --- | --- |
| Filho informa o pai | `CustomEvent` |
| Pai configura o filho | propriedade `@api` |
| Pai chama comportamento do filho | método `@api` |
| Componentes sem relação hierárquica, na mesma página | Lightning Message Service |
| Estado compartilhado entre muitos componentes | serviço dedicado ou LMS, avaliado caso a caso |

Eventos: nome em minúsculas, sem prefixo `on`, com `detail` contendo apenas dado serializável. Ver [naming-conventions.md](./naming-conventions.md#3-lightning-web-components).

Evitar acessar componentes por consulta ao DOM de outro componente — isso cria acoplamento frágil que quebra a cada mudança de estrutura interna.

### 6.4 Textos

Todo texto visível vem de Custom Label. Isso viabiliza tradução, revisão ortográfica centralizada e ajuste sem redeploy de código.

---

## 7. Performance

- **debounce** em campos de busca e filtros que disparam consulta (tipicamente 300 ms);
- **paginação** ou carregamento incremental para listas extensas — não trazer o conjunto completo para o cliente;
- **lazy loading** de conteúdo pesado e de componentes fora da área visível;
- minimizar chamadas ao servidor: agrupar dados relacionados em uma resposta em vez de várias chamadas em cascata;
- evitar processamento pesado no navegador — agregação e ordenação de grandes volumes pertencem ao servidor;
- getters usados no template são reavaliados a cada renderização: mantê-los baratos, sem laços custosos nem chamadas assíncronas;
- não criar `setInterval` sem limpeza em `disconnectedCallback`.

### 7.1 Atualização de dados

Após uma alteração, o dado em cache fica desatualizado. Atualizar explicitamente com o mecanismo adequado ao adaptador utilizado, em vez de recarregar a página ou duplicar o estado localmente.

---

## 8. Segurança

Resumo — detalhamento em [security-standards.md](./security-standards.md):

- toda autorização é validada no servidor;
- não expor dados sensíveis no cliente, nem em atributos ocultos ou no console;
- `cacheable=true` apenas em leitura;
- não renderizar HTML construído a partir de entrada de usuário;
- considerar o comportamento sob Lightning Web Security ao usar bibliotecas de terceiros;
- em Experience Cloud, revisar o que o componente expõe ao Guest User.

---

## 9. Testes Jest

Componentes com lógica em JavaScript — getters, handlers, formatação, chamadas imperativas — precisam de testes Jest.

Cobrir: renderização condicional dos quatro estados, interação do usuário, emissão de eventos, tratamento de erro e transformação de dados. Snapshot isolado não é teste: ele detecta mudança, não comprova comportamento.

Ver [testing-standards.md](./testing-standards.md).

---

## 10. Antipadrões

| Antipadrão | Problema |
| --- | --- |
| Apex onde LDS resolveria | perde FLS e cache automáticos |
| Sem estado de loading | usuário sem retorno visual |
| Erro tratado apenas no console | falha invisível ao usuário |
| Regra de negócio no JavaScript | contornável e não testável no servidor |
| Consulta ao DOM de outro componente | acoplamento frágil |
| Chamadas ao servidor em cascata | latência acumulada |
| CSS sobrescrevendo componente-base | quebra em atualização de release |
| `div` com clique em vez de `button` | inacessível por teclado |
| Texto fixo no template | impossível de traduzir e revisar |
| `cacheable=true` em método com DML | comportamento incorreto e imprevisível |
| Mutação de objeto vindo de `@wire` | erro de imutabilidade |
| Sem debounce em busca | excesso de chamadas ao servidor |

---

## 11. Checklist de revisão

**Arquitetura**
- [ ] Componente padrão avaliado antes da criação.
- [ ] LDS ou UI API avaliados antes de Apex.
- [ ] Regra de negócio no backend.
- [ ] Comunicação entre componentes por evento ou propriedade.

**Interface**
- [ ] Loading, empty, sucesso e erro implementados.
- [ ] Mensagens de erro compreensíveis, sem detalhe interno.
- [ ] Textos em Custom Labels, revisados ortograficamente.
- [ ] SLDS e componentes-base utilizados.

**Acessibilidade**
- [ ] Controles com rótulo acessível.
- [ ] Navegação por teclado funcional e foco gerenciado.
- [ ] Informação não transmitida apenas por cor.
- [ ] Conteúdo dinâmico anunciado adequadamente.

**Performance**
- [ ] Debounce em buscas.
- [ ] Paginação ou carregamento incremental em listas extensas.
- [ ] Chamadas ao servidor minimizadas.
- [ ] Getters de template baratos.

**Segurança**
- [ ] Autorização validada no servidor.
- [ ] Sem dado sensível no cliente.
- [ ] `cacheable` apenas em leitura.
- [ ] Exposição a Guest User revisada, quando aplicável.

**Testes**
- [ ] Jest cobrindo estados, interação e erro.
- [ ] Apex relacionado revisado e testado.

---

## Referências cruzadas

- [apex-standards.md](./apex-standards.md) · [security-standards.md](./security-standards.md) · [testing-standards.md](./testing-standards.md) · [naming-conventions.md](./naming-conventions.md)

## Fontes oficiais recomendadas

Lightning Web Components Developer Guide; Salesforce Lightning Design System; Component Library oficial; documentação de Lightning Data Service, UI API e GraphQL API; diretrizes de acessibilidade da Salesforce; Salesforce Well-Architected.

## Limitações

Disponibilidade de adaptadores, diretivas de template e comportamento de Lightning Web Security variam por release e por API Version. Confirmar na documentação oficial correspondente à release do projeto — inclusive a sintaxe de renderização condicional, que mudou entre versões da plataforma.

## Critérios de revisão

Revisar a cada release com mudanças em LWC, ao adotar Experience Cloud ou app móvel, e quando novos adaptadores oficiais substituírem chamadas Apex existentes.
