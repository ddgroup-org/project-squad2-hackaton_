---
title: "Template — Pull Request para UAT"
description: "Modelo de descrição de Pull Request de feature branch para a branch developer, com testes, evidências, riscos, instruções de UAT e rollback."
category: "template"
status: "active"
version: "1.1"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - pull-request
  - uat
  - template
applies_to:
  - global
source_of_truth: false
source_references:
  - desenvolvimento.md
  - execucao.md
---

# Template — Pull Request para UAT

```text
feature/* → developer
```

## Como usar

Copiar o bloco abaixo para a descrição do Pull Request e substituir os placeholders. Remover seções não aplicáveis, sem deixar placeholder vazio. Skill correspondente: [prepare-uat-pr](../.claude/skills/prepare-uat-pr/SKILL.md).

A descrição preenchida pertence ao Pull Request e ao repositório do projeto. **Nunca gravá-la nesta base global.**

As branches são placeholders: resolver `{FEATURE_BRANCH}` e `{UAT_TARGET_BRANCH}` com os nomes reais do projeto.

---

```markdown
## Demanda

**Identificador:** {ID_DEMANDA}
**Título:** {TITULO_DEMANDA}
**Origem:** {FEATURE_BRANCH} → **Destino:** {UAT_TARGET_BRANCH}
**Validado em:** {DEV_ORG_ALIAS}

## Objetivo

{O_QUE_A_ENTREGA_RESOLVE}

## Resumo da solução

{DESCRICAO_OBJETIVA_DO_QUE_FOI_IMPLEMENTADO}

## Componentes

### Criados

| Tipo | Componente | Finalidade |
| --- | --- | --- |
| {TIPO} | {NOME} | {FINALIDADE} |

### Alterados

| Tipo | Componente | Motivo da alteração |
| --- | --- | --- |
| {TIPO} | {NOME} | {MOTIVO} |

## Decisão técnica

**Alternativa escolhida:** {ALTERNATIVA}

**Justificativa:** {POR_QUE_ESSA_ABORDAGEM}

**Alternativas descartadas:**

| Alternativa | Motivo do descarte |
| --- | --- |
| {ALTERNATIVA} | {MOTIVO} |

**Fontes oficiais consultadas:** {DOCUMENTACAO_CONSULTADA}

## Segurança

- **Sharing:** {DECISAO_E_JUSTIFICATIVA}
- **CRUD e FLS:** {COMO_FOI_TRATADO}
- **Contexto de execução:** {USUARIO_OU_SISTEMA_E_MOTIVO}
- **Permissões necessárias:** {PERMISSION_SETS_E_CUSTOM_PERMISSIONS}
- **Exposição de dados:** {O_QUE_FICA_ACESSIVEL_E_PARA_QUEM}
- **Segredos:** nenhum valor real de credencial, token ou chave presente no diff.

## Performance e escalabilidade

- **Volume esperado:** {VOLUME}
- **Bulkificação:** {COMO_FOI_TRATADA}
- **Limites avaliados:** {LIMITES}
- **Comportamento em massa:** {RESULTADO}

## Testes

| Cenário | Tipo | Resultado |
| --- | --- | --- |
| {CENARIO} | positivo / negativo / bulk / permissão / exceção / regressão | {RESULTADO} |

**Comandos executados:**

```bash
{COMANDO_DE_TESTE}
```

**Resultado real:** {METODOS_EXECUTADOS_APROVADOS_FALHOS_E_COBERTURA}

**Testes Jest:** {RESULTADO_OU_NAO_APLICAVEL}

## Análise estática

**Resultado:** {RESULTADO}
**Apontamentos tratados:** {O_QUE_FOI_CORRIGIDO}
**Falsos positivos:** {QUAIS_E_POR_QUE}

## Evidências

- {EVIDENCIA_1}
- {EVIDENCIA_2}

## Dependências

- **De outras demandas:** {DEPENDENCIAS_OU_NENHUMA}
- **Entre commits:** {DEPENDENCIAS_OU_NENHUMA}
- **De configuração manual:** {DEPENDENCIAS_OU_NENHUMA}
- **De licença ou feature:** {DEPENDENCIAS_OU_NENHUMA}

## Passos manuais

### Pré-deploy

| Passo | Responsável |
| --- | --- |
| {PASSO} | {RESPONSAVEL} |

### Pós-deploy

| Passo | Responsável |
| --- | --- |
| {PASSO} | {RESPONSAVEL} |

Considerar: atribuição de Permission Set, registros de Custom Metadata, ativação de Flow, Remote Site Settings, Named Credentials, agendamentos e ajustes de dados.

## Riscos e pontos de atenção

| Risco | Severidade | Mitigação |
| --- | --- | --- |
| {RISCO} | crítico / alto / médio / baixo | {MITIGACAO} |

## Instruções para UAT

| # | Cenário | Perfil | Pré-condição | Passos | Resultado esperado | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | {CENARIO} | {PERFIL} | {PRE_CONDICAO} | {PASSOS} | {RESULTADO} | {EVIDENCIA} |

## Rollback

- **O que reverter:** {COMPONENTES}
- **Como:** {PROCEDIMENTO}
- **Commit-base:** {COMMIT_HASH}
- **Versão anterior de Flows:** {VERSOES}
- **Testes a repetir:** {TESTES}
- **Efeitos não reversíveis automaticamente:** {DADOS_INTEGRACOES_CONFIGURACOES}

## Limitações e pendências

| Item | Motivo | Risco residual | Responsável |
| --- | --- | --- | --- |
| {VALIDACAO_NAO_EXECUTADA} | {MOTIVO} | {RISCO} | {RESPONSAVEL} |

## Checklist

- [ ] Escopo da demanda integralmente atendido.
- [ ] Apenas arquivos da demanda alterados.
- [ ] `git status` e `git diff` revisados integralmente.
- [ ] Nenhum segredo, token ou dado sensível no diff.
- [ ] Sem SOQL ou DML em laço.
- [ ] Sharing, CRUD e FLS avaliados.
- [ ] Sem Id fixo nem credencial no código.
- [ ] Textos ao usuário em Custom Label, revisados ortograficamente.
- [ ] Testes criados ou ajustados e **executados**, com resultado real reportado.
- [ ] Cenários positivo, negativo e bulk cobertos.
- [ ] Análise estática executada e apontamentos tratados.
- [ ] Dependências identificadas.
- [ ] Passos manuais mapeados com responsável.
- [ ] Plano de rollback definido.
- [ ] Instruções de UAT verificáveis por outra pessoa.
- [ ] Documentação da demanda salva no repositório do projeto.
```

---

## Referências

[github-development-workflow.md](../knowledge/github-development-workflow.md) · [testing-standards.md](../knowledge/testing-standards.md) · [security-standards.md](../knowledge/security-standards.md) · Runbook: [promote-to-uat.md](../runbooks/promote-to-uat.md) · Template de Produção: [pull-request-production-template.md](./pull-request-production-template.md)
