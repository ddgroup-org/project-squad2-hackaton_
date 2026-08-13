---
title: "Runbook — Tratar conflito de metadata"
description: "Procedimento para identificar, preservar, comparar semanticamente e resolver conflitos de metadata sem decidir regra de negócio automaticamente."
category: "runbook"
status: "active"
version: "1.0"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - conflict
  - metadata
  - collaboration
  - runbook
applies_to:
  - global
source_of_truth: false
source_references:
  - execucao.md
  - desenvolvimento.md
---

# Runbook — Tratar conflito de metadata

## Objetivo

Resolver conflitos em metadata Salesforce preservando todas as versões envolvidas, comparando o que de fato mudou e devolvendo a decisão funcional a quem responde por ela.

## Princípio

**Um conflito de metadata é, quase sempre, duas pessoas resolvendo problemas diferentes no mesmo arquivo.**

O formato dos arquivos de metadata agrava isso: ferramentas reordenam elementos, o XML é verboso, e um conflito volumoso pode conter uma única alteração significativa — ou o contrário, um conflito pequeno pode esconder a inversão de uma regra de negócio.

**Conflito de regra de negócio não é resolvido automaticamente.** Escolher um lado é uma decisão funcional, não técnica.

## Quando utilizar

Conflito ao mesclar branches; conflito durante cherry-pick ou rebase; duas versões válidas do mesmo componente entre org e repositório; alteração concorrente detectada em sandbox compartilhada; divergência em que ambos os lados contêm trabalho legítimo.

## Documentos aplicáveis

- [operational-safety-policy.md](../knowledge/operational-safety-policy.md#9-concorrência-e-trabalho-de-outras-pessoas) — regra de concorrência.
- [github-development-workflow.md](../knowledge/github-development-workflow.md#6-conflitos) — conflitos no fluxo Git.
- [instruction-precedence.md](../knowledge/instruction-precedence.md) — o que prevalece; conflito funcional é bloqueante.
- [environment-safety.md](../knowledge/environment-safety.md) — confirmação do ambiente envolvido.

---

## Procedimento

### 1. Interromper a sobrescrita

Nenhum lado é descartado antes do diagnóstico. Não concluir merge, não resolver "aceitando o meu", não reexecutar a operação.

**Ponto de decisão:** se a ferramenta já resolveu automaticamente (auto-merge), revisar o resultado como se fosse um conflito — resolução automática em metadata Salesforce é frequentemente incorreta e silenciosa.

### 2. Preservar todas as versões

Antes de qualquer edição, guardar cópia íntegra de **cada** versão envolvida, em local do projeto:

```text
Versão local (working tree)
Versão da branch-base
Versão do ancestral comum, quando existir
Versão presente na org
Versão de outra branch, quando envolvida
```

Essa preservação é o que torna a resolução reversível. Sem ela, um erro de resolução é irrecuperável.

Salvar em `{PROJECT_ROOT}/docs/evidence/` ou equivalente — **nunca na Salesforce-AI-Base**.

### 3. Identificar a origem de cada lado

| Pergunta | Por que importa |
| --- | --- |
| Quem produziu cada versão? | define quem decide |
| A qual demanda cada versão pertence? | define a prioridade e o prazo |
| Alguma já foi homologada? | conteúdo homologado tem precedência de fato |
| Alguma já está em Produção? | reverter Produção é decisão de outro nível |
| Alguma foi feita pelo Setup, sem passar pelo repositório? | pode ser configuração legítima não versionada |

Sem responder a essas perguntas, qualquer resolução é chute.

### 4. Comparar semanticamente, não textualmente

O diff textual de metadata engana. Comparar **o que o componente faz**, não como o arquivo está escrito.

Separar as diferenças em duas categorias:

**Ruído — pode ser normalizado sem decisão funcional**
- reordenação de elementos por ferramenta;
- diferença de API Version não solicitada;
- espaçamento, indentação e quebras de linha;
- entradas de Profile ou Permission Set reordenadas.

**Substância — exige decisão**
- lógica de automação alterada;
- condição de entrada ou critério de decisão modificado;
- campo, objeto ou relacionamento adicionado ou removido;
- permissão concedida ou revogada;
- valor de configuração alterado;
- texto exibido ao usuário alterado.

Por tipo de componente, o que costuma exigir atenção:

| Componente | Conflito típico | Atenção |
| --- | --- | --- |
| Flow | dois fluxos de lógica distintos no mesmo arquivo | versões; não mesclar manualmente XML de Flow sem validar no Builder |
| Profile / Permission Set | entradas de várias demandas | granular; mesclar por entrada, não por arquivo |
| Layout | ordem e presença de campos | comparar a experiência resultante, não o XML |
| Objeto / Campo | atributos divergentes | mudança de tipo ou de picklist tem efeito em dados |
| Apex | lógica concorrente | testes de ambos os lados precisam continuar passando |
| `package.xml` | conjuntos diferentes | união costuma ser correta; verificar dependências |
| LWC | markup e JS concorrentes | estados de interface e testes Jest de ambos |

### 5. Mapear dependências

Antes de decidir, verificar o que depende de cada versão:

- campos referenciados por Flows, fórmulas, Validation Rules e relatórios;
- classes chamadas por LWC, Aura, Flow ou integrações;
- permissões necessárias para o funcionamento de cada lado;
- Custom Metadata consumida;
- testes que cobrem cada comportamento.

**Uma resolução que satisfaz o arquivo em conflito e quebra um dependente não é resolução.**

### 6. Identificar o responsável pela decisão

| Natureza do conflito | Quem decide |
| --- | --- |
| Apenas ruído de ferramenta | quem executa a resolução |
| Técnico, sem mudança de comportamento | responsável técnico |
| Duas regras funcionais incompatíveis | **responsável funcional pela regra** |
| Permissões e acesso a dados | responsável pela segurança do projeto |
| Efeito em Produção | responsável pelo ambiente |

**Ponto de decisão — proibição:** conflito de regra de negócio **não é resolvido pelo agente nem por quem está executando a mesclagem**. Apresentar as duas versões, o efeito de cada uma e as dependências; aguardar a decisão.

### 7. Resolver

Com a decisão tomada:

1. normalizar primeiro todo o ruído — isso reduz o conflito ao que importa;
2. aplicar a decisão funcional sobre as diferenças de substância;
3. resolver **apenas o que pertence ao escopo da demanda**; o restante é preservado como está;
4. para Flow, preferir resolver pela versão íntegra escolhida e reaplicar a alteração no Builder, em vez de mesclar XML manualmente;
5. para Profile e Permission Set, mesclar entrada a entrada, mantendo o que pertence a cada demanda;
6. registrar cada decisão de resolução, com justificativa.

### 8. Testar o resultado

O resultado de uma resolução é código novo — nunca foi executado antes.

- executar os testes que cobrem **os dois** comportamentos originais;
- executar os testes dos dependentes mapeados no passo 5;
- validar o cenário funcional de cada lado do conflito;
- executar a análise estática sobre o resultado;
- para Flow, confirmar que a versão resultante ativa é a correta.

**Ponto de decisão:** teste de apenas um dos lados não comprova a resolução. Se um dos comportamentos não puder ser testado, registrar como pendência com responsável.

### 9. Comunicar

Informar as pessoas envolvidas: qual conflito ocorreu, qual decisão foi tomada, por quem, e o que cada lado precisa verificar. Conflito resolvido em silêncio reaparece na próxima promoção.

### 10. Registrar

No projeto atual:

```text
Data e hora
Componentes em conflito
Origem de cada versão e demanda correspondente
Diferenças classificadas: ruído × substância
Dependências mapeadas
Decisão tomada e responsável
Justificativa
Testes executados e resultado real
Pendências e riscos residuais
Comunicação realizada
```

---

## Evidências

Cópia preservada de cada versão; diff semântico com ruído e substância separados; mapa de dependências; registro da decisão com responsável; resultado real dos testes de ambos os comportamentos.

## Riscos

| Risco | Consequência | Mitigação |
| --- | --- | --- |
| Descartar um lado sem diagnóstico | perda de trabalho e regressão | preservar todas as versões primeiro |
| Aceitar auto-merge sem revisão | comportamento incorreto silencioso | revisar auto-merge como conflito |
| Resolver regra de negócio automaticamente | decisão funcional errada, sem dono | escalonar para o responsável funcional |
| Confundir ruído com substância | conflito grande revisado superficialmente | separar as duas categorias antes |
| Ignorar dependentes | quebra fora do arquivo resolvido | mapear dependências antes de decidir |
| Testar apenas um lado | metade da resolução não comprovada | testar os dois comportamentos |
| Mesclar XML de Flow manualmente | Flow inválido ou com lógica corrompida | resolver por versão íntegra e reaplicar no Builder |
| Resolver em silêncio | conflito reaparece na promoção | comunicar os envolvidos |

## Rollback

1. restaurar a versão preservada no passo 2 do lado que se deseja recuperar;
2. quando a resolução já tiver sido implantada, redeploy da versão anterior a partir do commit-base;
3. para Flow, reativar a versão anterior registrada;
4. repetir os testes dos processos afetados;
5. registrar o que foi revertido e por quê.

A preservação do passo 2 é o que torna este rollback possível — **sem ela, não há rollback**.

## Critérios de conclusão

- [ ] Sobrescrita interrompida antes de qualquer edição.
- [ ] Todas as versões preservadas no projeto.
- [ ] Origem e demanda de cada versão identificadas.
- [ ] Diferenças separadas entre ruído e substância.
- [ ] Dependências mapeadas.
- [ ] Responsável pela decisão identificado; conflito funcional escalonado.
- [ ] Resolução limitada ao escopo da demanda.
- [ ] Testes de **ambos** os comportamentos executados com resultado real.
- [ ] Envolvidos comunicados.
- [ ] Registro salvo no projeto, com decisão e justificativa.

## Ações proibidas

Descartar uma das versões sem diagnóstico; resolver conflito de regra de negócio automaticamente ou por conta própria; aceitar auto-merge sem revisão; usar comandos destrutivos para "limpar" o conflito; resolver alterações que não pertencem à demanda; declarar a resolução concluída sem testar os dois comportamentos; mesclar XML de Flow manualmente sem validação; gravar as versões preservadas ou o registro na Salesforce-AI-Base.

## Referências

[operational-safety-policy.md](../knowledge/operational-safety-policy.md) · [github-development-workflow.md](../knowledge/github-development-workflow.md) · [instruction-precedence.md](../knowledge/instruction-precedence.md) · [environment-safety.md](../knowledge/environment-safety.md) · [retrieve-and-deploy-policy.md](../knowledge/retrieve-and-deploy-policy.md) · [flow-standards.md](../knowledge/flow-standards.md) · [resolve-org-repository-drift.md](./resolve-org-repository-drift.md) · [recover-failed-operation.md](./recover-failed-operation.md)

## Critérios de revisão

Revisar quando o time adotar nova estratégia de merge, quando um tipo de metadata passar a gerar conflitos recorrentes e após qualquer resolução que tenha causado regressão.
