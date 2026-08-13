---
title: "Template — Análise técnica Salesforce"
description: "Modelo genérico de análise técnica e arquitetural, com evidências, matriz de decisão, severidade, critérios de aceite, rollback e limitações."
category: "template"
status: "active"
version: "1.1"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - architecture
  - analysis
  - template
  - evidence
applies_to:
  - global
source_of_truth: false
source_references:
  - arquitetura.md
  - metaprompt-salesforce.md
---

# Template — Análise técnica Salesforce

## Como usar

Copiar o bloco abaixo, substituir os placeholders e salvar **no repositório do projeto** — por exemplo, em `{PROJECT_ROOT}/docs/technical-analysis/`. Nunca nesta base global.

Existe uma versão em HTML, com layout neutro em A4 pronto para conversão em PDF: [technical-analysis-report.html](./technical-analysis-report.html).

> **Procedência do HTML:** template genérico, sem identidade visual de cliente, **reconstruído a partir de requisitos e de fragmentos parciais**. Não é template oficial nem equivalente a um modelo corporativo completo, e está sujeito a substituição integral caso um arquivo oficial completo seja fornecido.

## Princípios de redação

- **Assertividade.** Evitar "parece", "talvez", "aparentemente está ok", "seria interessante validar". Preferir "A análise da metadata indica que...", "A evidência recuperada confirma que...", "Não há evidência suficiente para concluir que...", "O risco principal é...".
- **Evidência.** Toda conclusão técnica relevante sustentada por pelo menos uma evidência objetiva.
- **Sem invenção.** Informação não disponível é registrada como pendente, nunca preenchida por suposição.
- **Hipótese não é fato.** Distinguir explicitamente fato confirmado, inferência, premissa e informação pendente.
- **Limitações declaradas.** A seção de limitações nunca é omitida.
- **Conclusão compatível com a evidência.** Evidência forte permite conclusão assertiva; evidência parcial exige conclusão condicional; sem evidência suficiente, a conclusão é a ausência de conclusão.

---

```markdown
# Análise técnica — {TITULO_DA_ANALISE}

| Campo | Valor |
| --- | --- |
| Documento | {TITULO_DA_ANALISE} |
| Demanda | {ID_DEMANDA} |
| Cliente/Projeto | {CLIENTE_OU_PROJETO} |
| Org analisada / Ambiente | {ORG_OU_AMBIENTE} |
| Autor | {AUTOR} |
| Data | {DATA} |
| Versão | {VERSAO} |
| Status do artefato | {ATIVO_EM_ANALISE_OBSOLETO_REQUER_VALIDACAO} |
| Classificação | Interno / Confidencial |

## 1. Resumo executivo

{LEITURA_OBJETIVA_PARA_LIDERANCA}

Responder: o que foi analisado; qual é o impacto esperado; se há risco relevante; qual é a recomendação técnica; se há necessidade de validação em UAT, com o negócio ou em Produção.

## 2. Contexto

{QUAL_E_A_NECESSIDADE_E_O_PROBLEMA}

## 3. Escopo

{O_QUE_ESTA_INCLUIDO_NA_ANALISE}

## 4. Fora do escopo

{O_QUE_NAO_FOI_ANALISADO_E_POR_QUE}

## 5. Estado atual

{COMO_FUNCIONA_HOJE_COM_BASE_EM_EVIDENCIA}

Descrever o funcionamento atual dos artefatos. Não narrar histórico de mudanças — descrever o que existe e como opera hoje.

## 6. Evidências analisadas

| Tipo de evidência | Fonte | Resultado | Observação |
| --- | --- | --- | --- |
| Metadata | {COMPONENTE_RECUPERADO} | {RESULTADO} | {OBSERVACAO} |
| Consulta | {CONSULTA_REALIZADA} | {RESULTADO} | {OBSERVACAO} |
| Setup | {VERIFICACAO_REALIZADA} | {RESULTADO} | {OBSERVACAO} |
| Teste | {TESTE_EXECUTADO} | {RESULTADO_REAL} | {OBSERVACAO} |
| Análise estática | {ESCOPO_ANALISADO} | {RESULTADO} | {OBSERVACAO} |

Descrever as evidências pelo que foi verificado — consulta executada, metadata recuperada, verificação no Setup — sem citar o mecanismo interno ou a ferramenta utilizada para obtê-las.

## 7. Componentes envolvidos

| Tipo | Componente | Papel na análise | Status |
| --- | --- | --- | --- |
| {TIPO} | {API_NAME} | {PAPEL} | {STATUS} |

Todos os API Names listados foram confirmados. Componentes não confirmados são registrados como pendentes.

## 8. Matriz de dependências

| Artefato origem | Artefato dependente | Tipo de dependência | Direção | Impacto funcional | Impacto técnico | Risco de regressão | Evidência | Recomendação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {ORIGEM} | {DEPENDENTE} | {TIPO} | {DIRECAO} | {IMPACTO} | {IMPACTO} | {RISCO} | {EVIDENCIA} | {RECOMENDACAO} |

Tipos frequentes: Flow chama subflow; Flow atualiza campo; Flow chama Apex Invocable; Apex chama classe auxiliar; LWC chama método Apex; Validation Rule usa campo; Approval Process depende de status; Layout expõe campo; Permission Set concede acesso; integração consome campo; relatório utiliza campo; Custom Metadata controla regra; Named Credential usado por callout; Platform Event aciona processo assíncrono.

## 9. Alternativas avaliadas

### {ALTERNATIVA_1}
**Descrição:** {DESCRICAO}
**Vantagens:** {VANTAGENS}
**Limitações:** {LIMITACOES}

### {ALTERNATIVA_2}
**Descrição:** {DESCRICAO}
**Vantagens:** {VANTAGENS}
**Limitações:** {LIMITACOES}

## 10. Matriz de decisão

| Alternativa | Aderência | Complexidade | Performance | Escalabilidade | Segurança | Testabilidade | Manutenção | Risco | Recomendação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Reutilização | | | | | | | | | |
| Configuração | | | | | | | | | |
| Flow | | | | | | | | | |
| Solução híbrida | | | | | | | | | |
| Apex | | | | | | | | | |
| LWC | | | | | | | | | |
| Solução externa | | | | | | | | | |

Alternativas claramente inaplicáveis podem ser omitidas, com o motivo declarado.

## 11. Solução recomendada

**Decisão:** {DECISAO}

Classificação: aprovado tecnicamente | aprovado com ressalvas | não recomendado | requer validação funcional | requer validação técnica | requer redesenho | requer refatoração | requer saneamento | requer rollback | candidato à remoção | candidato à migração | sem evidência suficiente para decisão.

**Justificativa técnica:** {JUSTIFICATIVA}

**Fontes oficiais consultadas:** {DOCUMENTACAO}

## 12. Segurança, permissões e governança

- **Sharing e contexto de execução:** {ANALISE}
- **CRUD e FLS:** {ANALISE}
- **Permissionamento:** {ANALISE}
- **Exposição de dados:** {ANALISE}
- **Licenciamento:** {CONFIRMADO_OU_PENDENTE}

## 13. Performance e escalabilidade

- **Volume atual e projetado:** {VOLUME}
- **Limites relevantes:** {LIMITES}
- **Comportamento em massa:** {COMPORTAMENTO}
- **Pontos de atenção:** {PONTOS}

## 14. Impactos

| Dimensão | Impacto | Severidade |
| --- | --- | --- |
| Funcional | {IMPACTO} | {SEVERIDADE} |
| Técnico | {IMPACTO} | {SEVERIDADE} |
| Usuários | {IMPACTO} | {SEVERIDADE} |
| Dados | {IMPACTO} | {SEVERIDADE} |
| Automações | {IMPACTO} | {SEVERIDADE} |
| Integrações | {IMPACTO} | {SEVERIDADE} |
| Relatórios e dashboards | {IMPACTO} | {SEVERIDADE} |
| Segurança | {IMPACTO} | {SEVERIDADE} |
| Deploy | {IMPACTO} | {SEVERIDADE} |

## 15. Riscos

| # | Risco | Severidade | Causa | Consequência | Recomendação |
| --- | --- | --- | --- | --- | --- |
| 1 | {RISCO} | {SEVERIDADE} | {CAUSA} | {CONSEQUENCIA} | {RECOMENDACAO} |

**Níveis de severidade**

- **Crítico** — erro produtivo, perda de dados, falha de integração, quebra de processo crítico, exposição indevida de dados, indisponibilidade funcional ou impacto direto em usuários finais.
- **Alto** — regressão funcional relevante, duplicidade de automação, inconsistência de dados, falha em regra de negócio importante ou aumento expressivo de débito técnico.
- **Médio** — impacto em manutenção, performance, clareza técnica, rastreabilidade ou governança; risco controlado em cenários específicos.
- **Baixo** — impacto limitado, sem efeito direto conhecido em produção; melhoria recomendada por governança ou manutenção futura.

## 16. Critérios de aceite

| # | Critério | Verificação |
| --- | --- | --- |
| 1 | Dado que {CONTEXTO}, quando {ACAO}, então {RESULTADO_ESPERADO} | {COMO_VERIFICAR} |

## 17. Planejamento de testes

| # | Cenário | Perfil | Pré-condição | Massa de dados | Passos | Resultado esperado | Evidência |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | {CENARIO} | {PERFIL} | {PRE_CONDICAO} | {MASSA} | {PASSOS} | {RESULTADO} | {EVIDENCIA} |

Incluir, quando aplicável, cenários positivos, negativos, regressivos, integrados, de segurança e de volume.

## 18. Rollback

- **O que reverter:** {COMPONENTES}
- **Como:** {PROCEDIMENTO}
- **Em qual ambiente:** {AMBIENTE}
- **Dependências:** {DEPENDENCIAS}
- **Testes a repetir:** {TESTES}
- **Efeitos não reversíveis automaticamente:** {EFEITOS}

## 19. Limitações da análise

| # | O que não foi validado | Por quê | Risco residual | Validação necessária | Responsável |
| --- | --- | --- | --- | --- | --- |
| 1 | {ITEM} | {MOTIVO} | {RISCO} | {VALIDACAO} | {RESPONSAVEL} |

Esta seção não deve ser omitida. Quando toda a evidência necessária foi obtida, registrar explicitamente esse fato.

## 20. Próximos passos

| Prioridade | Ação | Responsável |
| --- | --- | --- |
| Imediato | {ACAO} | {RESPONSAVEL} |
| Antes do deploy | {ACAO} | {RESPONSAVEL} |
| Durante validação em UAT | {ACAO} | {RESPONSAVEL} |
| Após validação | {ACAO} | {RESPONSAVEL} |
| Pós-produção | {ACAO} | {RESPONSAVEL} |
| Melhoria futura | {ACAO} | {RESPONSAVEL} |
```

---

## Referências

[salesforce-development-principles.md](../knowledge/salesforce-development-principles.md) · [security-standards.md](../knowledge/security-standards.md) · [testing-standards.md](../knowledge/testing-standards.md) · Agente: [salesforce-architect](../.claude/agents/salesforce-architect.md) · Versão HTML: [technical-analysis-report.html](./technical-analysis-report.html)
