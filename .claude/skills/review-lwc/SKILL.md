---
name: review-lwc
description: Use para revisar um Lightning Web Component completo — HTML, JavaScript, XML, CSS, Apex relacionado e testes Jest — avaliando acessibilidade, performance, segurança e experiência do usuário. Revisa sem alterar arquivos.
---

# Objetivo

Produzir uma revisão completa de LWC, cobrindo todos os arquivos do componente, o Apex consumido e os testes, com apontamentos classificados por severidade.

# Pré-condições

- arquivos do componente disponíveis para leitura;
- contexto de renderização conhecido: Lightning Experience, Experience Cloud, app móvel ou acesso público;
- classes Apex consumidas acessíveis.

# Entradas

```text
{COMPONENTE}         caminho do componente
{CONTEXTO_USO}       onde o componente é renderizado e por quais perfis
{APEX_RELACIONADO}   classes consumidas
{TESTES_JEST}        testes existentes
{REFERENCIA_VISUAL}  layout esperado, quando houver
```

# Procedimento

## 1. Estabelecer o padrão de referência

Ler [lwc-standards.md](../../../knowledge/lwc-standards.md), [security-standards.md](../../../knowledge/security-standards.md), [apex-standards.md](../../../knowledge/apex-standards.md) e [testing-standards.md](../../../knowledge/testing-standards.md).

Ler `CLAUDE.md`, `AGENTS.md` e os padrões de design do projeto. **Quando o projeto seguir um padrão consistente diferente do global, o padrão do projeto é a referência** — os limites dessa adaptação estão em [instruction-precedence.md](../../../knowledge/instruction-precedence.md#3-o-que-o-projeto-pode-e-não-pode-adaptar): convenção e arquitetura são adaptáveis; acessibilidade e controles de segurança, não.

## 2. Revisar o HTML

- estados de loading, empty, sucesso e erro presentes e distinguíveis;
- uso de componentes-base `lightning-*` e classes utilitárias do SLDS;
- elementos semânticos em vez de `div` com manipulador de clique;
- rótulo acessível em todo controle interativo;
- erros associados ao campo correspondente;
- conteúdo dinâmico relevante anunciado por região apropriada;
- imagens com texto alternativo adequado;
- ausência de texto fixo — todo texto vindo de Custom Label;
- renderização condicional coerente e sem estados sobrepostos.

## 3. Revisar o JavaScript

- `@wire` para leitura reativa; chamada imperativa para ação do usuário;
- tratamento de erro em toda chamada ao servidor;
- imutabilidade de dados vindos de `@wire`;
- regra de negócio ausente do cliente;
- eventos nomeados corretamente, com `detail` serializável;
- ausência de acesso ao DOM de outro componente;
- limpeza de temporizadores e listeners em `disconnectedCallback`;
- getters de template baratos, sem laços custosos nem operação assíncrona;
- debounce em campos de busca;
- atualização explícita do cache após alteração de dados.

## 4. Revisar o XML de metadata

- targets coerentes com o uso real;
- propriedades expostas necessárias e bem descritas;
- API Version compatível com o projeto;
- exposição pública declarada apenas quando intencional.

## 5. Revisar o CSS

- SLDS antes de estilo próprio;
- ausência de sobrescrita de estilos internos de componentes-base;
- responsividade para coluna estreita e app móvel;
- contraste adequado entre texto e fundo.

Havendo biblioteca de terceiro carregada como recurso estático, avaliar origem, versão fixada, licença, requisições externas e comportamento sob Lightning Web Security — ver [supply-chain-security.md](../../../knowledge/supply-chain-security.md#34-bibliotecas-no-cliente-lwc).

## 6. Revisar o Apex relacionado

- `cacheable=true` apenas em métodos de leitura, sem efeito colateral;
- segurança: sharing, CRUD, FLS e validação de entrada no servidor;
- volume retornado compatível com a interface, com paginação quando necessário;
- ausência de SOQL ou DML em laço;
- mensagens de erro sem detalhe interno.

## 7. Revisar os testes Jest

- estados de loading, empty, sucesso e erro cobertos;
- interação do usuário e emissão de eventos verificadas;
- mocks de Apex e de adaptadores `@wire`;
- asserções de comportamento observável;
- snapshot isolado apontado como insuficiente.

## 8. Avaliar acessibilidade explicitamente

Navegação completa por teclado; ordem de foco previsível; foco gerenciado em modais e devolvido à origem; informação não transmitida apenas por cor; mensagens de erro perceptíveis por leitor de tela.

Declarar o que **não** foi possível verificar — validação com leitor de tela e medição real de contraste normalmente exigem execução no ambiente.

## 9. Avaliar a experiência do usuário

Clareza das mensagens; caminho de recuperação após erro; retorno visual durante operações; aderência à referência visual, com cada divergência registrada individualmente quando houver.

## 10. Classificar e consolidar

```text
Crítico    exposição de dados, falha de segurança, componente inutilizável, barreira total de acessibilidade
Alto       estado não tratado, erro invisível, falha sob volume, regra de negócio no cliente
Médio      performance, acessibilidade parcial, manutenção, aderência ao SLDS
Baixo      clareza ou consistência visual
Sugestão   preferência técnica, sem risco associado
```

Formato de cada apontamento:

```text
[SEVERIDADE] Título objetivo do problema

Arquivo:      caminho/do/componente/arquivo.js, linha N
Problema:     o que está incorreto
Impacto:      efeito para o usuário ou para o sistema
Evidência:    trecho do código que comprova
Recomendação: o que fazer, de forma acionável
Referência:   documento e seção do padrão aplicável
```

# Validações

- [ ] HTML, JavaScript, XML e CSS revisados.
- [ ] Apex relacionado revisado.
- [ ] Testes Jest revisados.
- [ ] Quatro estados de interface verificados.
- [ ] Acessibilidade avaliada explicitamente.
- [ ] Performance avaliada.
- [ ] Segurança validada no backend.
- [ ] Cada apontamento com arquivo, evidência e recomendação.
- [ ] Nenhum arquivo alterado.
- [ ] Relatório salvo no projeto atual, nunca na Salesforce-AI-Base.

# Evidências

Trechos citados em cada apontamento; resultado de lint e de testes Jest, quando executados; lista completa dos arquivos revisados; comparação com a referência visual, quando houver.

# Situações de interrupção

- componente incompleto, sem template ou sem metadata;
- Apex consumido indisponível, com impacto direto na avaliação de segurança;
- contexto de renderização indefinido quando houver possibilidade de exposição pública;
- dado sensível ou segredo detectado no cliente — interromper e reportar imediatamente.

# Saída esperada

1. **Resumo** — componente, contexto de uso e conclusão geral.
2. **Apontamentos por severidade**.
3. **Avaliação de acessibilidade** — verificado e não verificado.
4. **Avaliação dos testes Jest**.
5. **Avaliação do Apex consumido**.
6. **Avaliação de experiência do usuário**, com divergências visuais quando houver.
7. **Pontos positivos**.
8. **Bloqueios**.
9. **Decisão** — aprovado, aprovado com ressalvas ou não aprovado.
10. **Limitações da revisão** e quem deve validar o que ficou pendente.

Agente correspondente: [lwc-code-reviewer](../../agents/lwc-code-reviewer.md).
