---
name: review-apex
description: Use para revisar código Apex criado ou alterado, produzindo apontamentos estruturados por severidade com arquivo, problema, impacto, evidência e recomendação. Revisa sem alterar arquivos.
---

# Objetivo

Produzir uma revisão Apex estruturada e acionável, classificada por severidade, com cada apontamento sustentado por evidência no código.

# Pré-condições

- código Apex disponível para leitura;
- escopo da revisão definido (arquivos, diff ou classes);
- contexto da demanda conhecido;
- padrão arquitetural do projeto identificado.

# Entradas

```text
{ARQUIVOS_OU_DIFF}   escopo da revisão
{DEMANDA}            contexto e critérios de aceite
{TEST_CLASSES}       classes de teste relacionadas
{RESULTADO_TESTES}   saída real da execução, quando existir
{RESULTADO_ANALISE}  saída da análise estática, quando existir
```

# Procedimento

## 1. Estabelecer o padrão de referência

Ler [apex-standards.md](../../../knowledge/apex-standards.md), [security-standards.md](../../../knowledge/security-standards.md) e [testing-standards.md](../../../knowledge/testing-standards.md).

Ler `CLAUDE.md` e `AGENTS.md` do projeto. **Quando o projeto seguir um padrão consistente diferente do global, o padrão do projeto é a referência** — avaliar consistência interna, não aderência forçada ao padrão global. Os limites dessa adaptação estão em [instruction-precedence.md](../../../knowledge/instruction-precedence.md#3-o-que-o-projeto-pode-e-não-pode-adaptar): convenção e arquitetura são adaptáveis; controles de segurança, não.

## 2. Ler o código no contexto

Revisar o diff **e** o código ao redor. Uma alteração correta isoladamente pode quebrar o comportamento da classe.

## 3. Percorrer os eixos de avaliação

| Eixo | O que verificar |
| --- | --- |
| Arquitetura | responsabilidade única, separação de camadas, trigger sem lógica, ausência de duplicação |
| Bulkificação | SOQL e DML fora de laços, uso de coleções, comportamento com 200 registros |
| SOQL | seletividade, campos necessários, filtros, tratamento de retorno vazio |
| DML | agrupamento, verificação de coleção vazia, operações parciais conforme a regra de negócio |
| Limites | CPU, heap, linhas de query, linhas de DML, callouts, jobs assíncronos |
| Segurança | sharing declarado, CRUD, FLS, modo de execução, SOQL dinâmica, ausência de segredos e Ids fixos |
| Exceções | captura específica, sem bloco vazio, contexto suficiente, erro funcional distinto de técnico |
| Recursão | risco de reentrada e controle adotado |
| Assincronismo | mecanismo justificado, tratamento de falha, observabilidade |
| Logs | suficientes para investigar, sanitizados, sem dado sensível |
| Manutenibilidade | nomes, tamanho dos métodos, constantes, Custom Metadata, Custom Labels, comentários úteis |
| Testes | cenários, asserts comportamentais, massa própria, mocks, ausência de `SeeAllData=true` |
| Regressão | consumidores identificados, assinatura pública preservada ou quebra justificada |
| Análise estática | violações críticas e altas tratadas; falsos positivos documentados |

## 4. Classificar por severidade

```text
Crítico
Alto
Médio
Baixo
Sugestão
```

- **Crítico** — erro produtivo, perda de dados, exposição indevida, falha de segurança, quebra de processo crítico.
- **Alto** — regressão relevante, falha sob volume, inconsistência de dados, débito técnico expressivo.
- **Médio** — impacto em manutenção, performance, clareza, rastreabilidade ou governança.
- **Baixo** — melhoria recomendada, sem efeito direto conhecido.
- **Sugestão** — preferência técnica, sem risco associado.

## 5. Escrever cada apontamento no formato obrigatório

```text
[SEVERIDADE] Título objetivo do problema

Arquivo:      caminho/do/arquivo.cls, linha N
Problema:     o que está incorreto
Impacto:      o que acontece na prática, sob quais condições
Evidência:    trecho do código que comprova o apontamento
Recomendação: o que fazer, de forma acionável
Referência:   documento e seção do padrão aplicável
```

Nenhum apontamento sem localização, evidência e recomendação. Apontamento sem evidência é opinião, não revisão.

## 6. Avaliar os testes

Verificar se os testes comprovam comportamento: cenários positivo, negativo, bulk, permissão e exceção; asserts com valor esperado e mensagem; massa própria; mocks para callouts; validação de processamento assíncrono.

Cobertura alta com asserts triviais deve ser apontada explicitamente.

## 7. Consolidar

Reunir apontamentos, avaliação dos testes, pontos positivos, bloqueios e decisão.

# Validações

- [ ] Todos os arquivos do escopo revisados.
- [ ] Padrão do projeto considerado antes do padrão global.
- [ ] Cada eixo de avaliação percorrido.
- [ ] Cada apontamento com arquivo, linha, evidência e recomendação.
- [ ] Severidade justificada.
- [ ] Testes avaliados quanto ao comportamento.
- [ ] Resultado da análise estática considerado, quando disponível.
- [ ] Nenhum arquivo alterado.
- [ ] Relatório salvo no projeto atual, nunca na Salesforce-AI-Base.

# Evidências

Trechos de código citados em cada apontamento; resultado real da execução dos testes, quando disponível; saída da análise estática, quando disponível; lista dos arquivos revisados.

# Situações de interrupção

- código incompleto ou não compilável;
- escopo muito além do declarado na demanda;
- **segredo detectado no código** — interromper e reportar imediatamente, antes de qualquer push, sem incluir o valor no relatório;
- padrão arquitetural do projeto indeterminado, com impacto direto na avaliação.

# Saída esperada

1. **Resumo** — escopo, arquivos revisados e conclusão geral.
2. **Apontamentos por severidade**, do mais grave ao menos grave.
3. **Avaliação dos testes**.
4. **Resultado da análise estática**, quando disponível.
5. **Pontos positivos** a preservar.
6. **Bloqueios** que impedem a aprovação.
7. **Decisão** — aprovado, aprovado com ressalvas ou não aprovado.
8. **Limitações da revisão** — o que não foi possível verificar e por quê.

Agente correspondente: [apex-code-reviewer](../../agents/apex-code-reviewer.md).
