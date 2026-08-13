---
title: "Template — Pull Request para Produção"
description: "Modelo de descrição de Pull Request de branch de release para main, com validação de equivalência, plano de deploy, configurações manuais, rollback e responsáveis."
category: "template"
status: "active"
version: "1.1"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - pull-request
  - production
  - release
  - template
applies_to:
  - global
source_of_truth: false
source_references:
  - execucao.md
  - metaprompt-salesforce.md
---

# Template — Pull Request para Produção

```text
release/* → main
```

## Como usar

Copiar o bloco abaixo para a descrição do Pull Request e substituir os placeholders. Skill correspondente: [prepare-production-pr](../.claude/skills/prepare-production-pr/SKILL.md).

A descrição preenchida pertence ao Pull Request e ao repositório do projeto. **Nunca gravá-la nesta base global.**

As branches são placeholders: resolver `{RELEASE_BRANCH}` e `{PRODUCTION_BASE_BRANCH}` com os nomes reais do projeto.

**Este Pull Request é independente do Pull Request de homologação** sempre que a estratégia do projeto permitir separá-los. No padrão de fallback, a branch de release é criada a partir da branch-base de Produção atualizada e recebe apenas o conteúdo homologado.

---

```markdown
## Identificação

**Demanda:** {ID_DEMANDA} — {TITULO_DEMANDA}
**Pull Request de UAT:** {PR_UAT}
**Origem:** {RELEASE_BRANCH} → **Destino:** {PRODUCTION_BASE_BRANCH}
**Org de destino:** {PROD_ORG_ALIAS}
**Janela de implantação:** {JANELA_OU_NAO_APLICAVEL}

## Aprovação e homologação

| Item | Situação | Responsável | Data |
| --- | --- | --- | --- |
| Homologação em UAT | {CONCLUIDA} | {RESPONSAVEL} | {DATA} |
| Aprovação do Tech Lead | {REGISTRADA} | {RESPONSAVEL} | {DATA} |
| Aprovação funcional | {REGISTRADA_OU_NAO_APLICAVEL} | {RESPONSAVEL} | {DATA} |

**Evidências de homologação:** {ONDE_ESTAO_REGISTRADAS}

## Commits incluídos

| Hash | Descrição | Homologado em UAT |
| --- | --- | --- |
| {COMMIT_HASH} | {DESCRICAO} | sim |

**Dependências entre commits:** {DEPENDENCIAS_OU_NENHUMA}

**Método de aplicação:** {CHERRY_PICK_OU_OUTRO} — {JUSTIFICATIVA}

## Componentes promovidos

| Tipo | Componente | Ação | Motivo |
| --- | --- | --- | --- |
| {TIPO} | {NOME} | criado / alterado | {MOTIVO} |

## Validação de equivalência

Confirmação de que o conteúdo promovido corresponde ao homologado em UAT:

- [ ] Todos os componentes homologados estão presentes.
- [ ] Nenhum componente adicional foi incluído.
- [ ] Nenhuma alteração de comportamento foi introduzida durante a preparação.

**Diferenças em relação ao homologado:** {NENHUMA_OU_LISTA_JUSTIFICADA}

**Comando de comparação executado:**

```bash
git diff {PRODUCTION_BASE_BRANCH}...{RELEASE_BRANCH} --stat
```

## Dependências em Produção

| Dependência | Existe em Produção | Incluída nesta promoção | Observação |
| --- | --- | --- | --- |
| {DEPENDENCIA} | {SIM_NAO} | {SIM_NAO} | {OBSERVACAO} |

Considerar: campos referenciados, classes chamadas, Custom Metadata consumida, Record Types, permissões, Named Credentials e configurações de integração.

## Testes e validação

**Testes executados:** {CENARIOS_E_RESULTADO_REAL}
**Cobertura obtida:** {COBERTURA}
**Análise estática:** {RESULTADO}
**Validação sem deploy em Produção:** {RESULTADO_OU_NAO_EXECUTADA_E_MOTIVO}

```bash
sf project deploy validate --manifest {MANIFEST_PATH} --target-org {PROD_ORG_ALIAS} --test-level {TEST_LEVEL}
```

## Plano de deploy

| Ordem | Etapa | Componentes | Responsável |
| --- | --- | --- | --- |
| 1 | {ETAPA} | {COMPONENTES} | {RESPONSAVEL} |

**Nível de teste na pipeline:** {TEST_LEVEL}
**Tempo estimado:** {TEMPO}

## Configurações manuais

### Pré-deploy

| # | Configuração | Responsável | Confirmada |
| --- | --- | --- | --- |
| 1 | {CONFIGURACAO} | {RESPONSAVEL} | [ ] |

### Pós-deploy

| # | Configuração | Responsável | Confirmada |
| --- | --- | --- | --- |
| 1 | {CONFIGURACAO} | {RESPONSAVEL} | [ ] |

Considerar: atribuição de Permission Set, registros de Custom Metadata, ativação de Flow **na versão correta**, Remote Site Settings, Named Credentials, External Credentials, agendamentos e ajustes de dados.

## Validação pós-deploy

| # | Cenário crítico | Passos | Resultado esperado | Responsável |
| --- | --- | --- | --- | --- |
| 1 | {CENARIO} | {PASSOS} | {RESULTADO} | {RESPONSAVEL} |

**Período de monitoramento:** {PERIODO}
**O que monitorar:** {ERROS_LOGS_INTEGRACOES_VOLUME}

## Riscos

| Risco | Severidade | Probabilidade | Mitigação |
| --- | --- | --- | --- |
| {RISCO} | crítico / alto / médio / baixo | {PROBABILIDADE} | {MITIGACAO} |

## Rollback

**Commit-base:** {COMMIT_HASH}

| # | Passo | Responsável |
| --- | --- | --- |
| 1 | Redeploy da versão anterior dos componentes afetados | {RESPONSAVEL} |
| 2 | Reativação da versão anterior dos Flows: {VERSOES} | {RESPONSAVEL} |
| 3 | Reversão das configurações manuais aplicadas | {RESPONSAVEL} |
| 4 | Repetição dos testes dos processos afetados | {RESPONSAVEL} |
| 5 | Comunicação aos envolvidos | {RESPONSAVEL} |

**Efeitos NÃO reversíveis automaticamente:**

- {DADOS_ALTERADOS_OU_CRIADOS}
- {INTEGRACOES_ACIONADAS}
- {NOTIFICACOES_ENVIADAS}
- {CONFIGURACOES_EXTERNAS}

**Responsável pela decisão de reverter:** {RESPONSAVEL}

## Responsáveis

| Papel | Nome |
| --- | --- |
| Desenvolvimento | {RESPONSAVEL} |
| Revisão técnica | {RESPONSAVEL} |
| Aprovação | {RESPONSAVEL} |
| Execução da pipeline | {RESPONSAVEL} |
| Validação pós-deploy | {RESPONSAVEL} |

## Limitações e riscos residuais aceitos

| Item | Motivo | Risco | Aceito por |
| --- | --- | --- | --- |
| {ITEM} | {MOTIVO} | {RISCO} | {RESPONSAVEL} |

## Checklist

- [ ] Homologação em UAT concluída, com evidências.
- [ ] Aprovação do Tech Lead registrada.
- [ ] Estratégia de promoção do projeto confirmada e aplicada.
- [ ] Conteúdo a promover isolado do trabalho não homologado.
- [ ] Somente commits homologados incluídos.
- [ ] Dependências entre commits satisfeitas.
- [ ] **Equivalência com o conteúdo homologado confirmada.**
- [ ] Dependências existentes em Produção ou incluídas na promoção.
- [ ] Nenhum segredo, token ou dado sensível no diff.
- [ ] Testes executados com resultado real.
- [ ] Análise estática sem violação crítica ou alta pendente.
- [ ] Validação sem deploy executada, quando autorizada.
- [ ] Ordem de deploy definida.
- [ ] Configurações manuais mapeadas com responsável.
- [ ] Plano de validação pós-deploy definido.
- [ ] Plano de rollback executável, com efeitos irreversíveis declarados.
- [ ] Janela de implantação acordada, quando aplicável.
- [ ] Autorização explícita obtida para push, abertura do PR e execução da pipeline.
```

---

## Referências

[github-development-workflow.md](../knowledge/github-development-workflow.md) · [retrieve-and-deploy-policy.md](../knowledge/retrieve-and-deploy-policy.md) · [testing-standards.md](../knowledge/testing-standards.md) · Runbooks: [promote-to-production.md](../runbooks/promote-to-production.md), [emergency-hotfix.md](../runbooks/emergency-hotfix.md) · Template de UAT: [pull-request-uat-template.md](./pull-request-uat-template.md)
