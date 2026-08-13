---
name: salesforce-preflight-check
description: Use antes de qualquer alteração em um projeto Salesforce para verificar projeto, Git, modelo de desenvolvimento, org, ambiente, alterações preexistentes, escopo, riscos e autorizações. Somente leitura — não altera nada.
---

# Objetivo

Produzir um retrato verificado do estado atual antes de qualquer alteração: onde estamos, contra qual org, em qual branch, sob qual modelo de desenvolvimento, com o que já existe no working tree e com quais autorizações.

**Esta skill é somente leitura.** Não cria, não altera, não remove, não faz checkout, não faz deploy, não faz retrieve.

# Quando usar

Antes de implementar, antes de recuperar ou implantar metadata, antes de criar branch e sempre que houver dúvida sobre o estado do ambiente. Também isoladamente, como diagnóstico.

# Pré-condições

- caminho do projeto conhecido;
- acesso de leitura ao repositório;
- quando houver org envolvida, autenticação já estabelecida.

# Entradas

```text
{PROJECT_ROOT}       caminho absoluto do projeto
{ORG_OU_AMBIENTE}    org a verificar, quando houver
{DEMANDA}            demanda prevista, quando houver
```

# Documentos aplicáveis

[instruction-precedence.md](../../../knowledge/instruction-precedence.md) · [operational-safety-policy.md](../../../knowledge/operational-safety-policy.md) · [environment-safety.md](../../../knowledge/environment-safety.md) · [salesforce-development-principles.md](../../../knowledge/salesforce-development-principles.md#3-pre-flight-obrigatório)

---

# Procedimento

## 1. Projeto

```bash
pwd
ls -la
```

Verificar e registrar:

- [ ] caminho absoluto e se é o projeto esperado;
- [ ] existência de `sfdx-project.json`;
- [ ] diretório considerado raiz do projeto;
- [ ] existência e conteúdo de `CLAUDE.md`;
- [ ] existência e conteúdo de `AGENTS.md`;
- [ ] `README.md` e documentação em `docs/`;
- [ ] package directories declarados;
- [ ] API Version do projeto;
- [ ] links simbólicos no caminho, que possam redirecionar escrita para fora do projeto.

**Ponto de decisão:** ausência de `sfdx-project.json` não invalida o projeto — pode ser org-driven ou ter outra raiz. Confirmar antes de prosseguir, não presumir.

## 2. Instruções aplicáveis

Ler e registrar o que se aplica:

- [ ] regras obrigatórias em `CLAUDE.md` e `AGENTS.md`;
- [ ] convenções locais de nomenclatura e arquitetura;
- [ ] ADRs vigentes relacionados ao escopo;
- [ ] documentação da pipeline;
- [ ] template de Pull Request do repositório.

**As regras do projeto prevalecem** sobre os padrões globais, nos limites de [instruction-precedence.md](../../../knowledge/instruction-precedence.md#3-o-que-o-projeto-pode-e-não-pode-adaptar).

## 3. Modelo de desenvolvimento e de branches

Não presumir. Confirmar e registrar:

| Item | Valor confirmado | Origem da confirmação |
| --- | --- | --- |
| Modelo de desenvolvimento | {DEVELOPMENT_MODEL} | |
| Modelo de packages | {PACKAGE_MODEL} | |
| Branch-base do desenvolvimento | {DEVELOPMENT_BASE_BRANCH} | |
| Branch da homologação | {UAT_TARGET_BRANCH} | |
| Branch-base de Produção | {PRODUCTION_BASE_BRANCH} | |
| Estratégia de promoção | {PROMOTION_STRATEGY} | |
| Política de cherry-pick | {CHERRY_PICK_POLICY} | |
| Estratégia de retrieve e deploy | {RETRIEVE_DEPLOY_STRATEGY} | |
| Source tracking | {SOURCE_TRACKING} | |

**Ponto de decisão:** item não confirmado é **pendência**, não valor padrão. O fallback da base (`developer`/`main`, source-driven, cherry-pick) só se aplica quando o projeto explicitamente não define o seu — e essa adoção precisa ser declarada.

## 4. Git

```bash
git rev-parse --is-inside-work-tree
git branch --show-current
git branch -a
git status
git log --oneline -10
git remote -v
git fetch --dry-run
```

Verificar e registrar:

- [ ] é repositório Git;
- [ ] branch atual;
- [ ] branches remotas existentes e proteções conhecidas;
- [ ] remote configurado;
- [ ] estado do working tree;
- [ ] arquivos modificados;
- [ ] arquivos não rastreados;
- [ ] commits locais não enviados;
- [ ] divergência em relação ao remoto;
- [ ] `stash` existente;
- [ ] **operações Git incompletas**: merge, rebase ou cherry-pick em andamento.

**Ponto de decisão:** operação Git incompleta **interrompe** o pre-flight. Resolver o estado antes de qualquer coisa — ver [recover-failed-operation.md](../../../runbooks/recover-failed-operation.md).

## 5. Alterações preexistentes

Para cada arquivo modificado ou não rastreado:

| Arquivo | Pertence a esta demanda | Origem provável | Ação |
| --- | --- | --- | --- |

**Alterações preexistentes são preservadas.** Não descartar, não incorporar automaticamente, não executar comando que possa sobrescrevê-las.

**Ponto de decisão:** alteração de origem desconhecida ou pertencente a outra demanda → registrar e **perguntar** antes de prosseguir.

## 6. Org e ambiente

```bash
sf org list
sf org display --target-org {ORG_OU_AMBIENTE}
```

Verificar e registrar:

- [ ] alias;
- [ ] username;
- [ ] Organization ID;
- [ ] instance URL;
- [ ] tipo de ambiente (sandbox ou Produção);
- [ ] status de autenticação;
- [ ] API Version da org;
- [ ] namespace, quando aplicável;
- [ ] coerência entre a branch ativa e o ambiente.

**Alias isolado não é identificação suficiente.** Comparar no mínimo alias, username, Organization ID e tipo de ambiente.

**Ponto de decisão:** qualquer indício de Produção — ou impossibilidade de confirmar o ambiente — **interrompe**. Ver [environment-safety.md](../../../knowledge/environment-safety.md#31-indicadores-de-possível-produção).

## 7. Escopo previsto

Registrar antes de qualquer alteração:

```text
Demanda e objetivo
Componentes previstos
Arquivos previstos
Componentes e arquivos que NÃO devem ser modificados
Dependências conhecidas
Testes esperados
Riscos identificados
Estratégia de rollback
```

## 8. Autorizações

Listar as ações previstas e confrontá-las com a matriz de [operational-safety-policy.md](../../../knowledge/operational-safety-policy.md#3-matriz-de-aprovação-humana):

| Ação prevista | Exige autorização | Autorização concedida |
| --- | --- | --- |

**Ponto de decisão:** ação prevista sem autorização correspondente não é executada. Solicitar antes, de forma separada por ação.

## 9. Consolidar o retrato

Produzir o relatório da seção "Saída esperada" e **parar**. Esta skill não implementa.

---

# Validações

- [ ] Projeto identificado e confirmado como o esperado.
- [ ] Instruções locais lidas.
- [ ] Modelo de desenvolvimento e de branches confirmado, não presumido.
- [ ] Estado do Git levantado, incluindo operações incompletas.
- [ ] Alterações preexistentes identificadas e classificadas.
- [ ] Org confirmada por alias, username, Organization ID e tipo de ambiente.
- [ ] Coerência entre branch e ambiente verificada.
- [ ] Escopo previsto registrado, incluindo o que não deve ser tocado.
- [ ] Autorizações necessárias mapeadas.
- [ ] Nenhuma alteração realizada.

# Evidências

Saída de cada comando executado; conteúdo relevante de `CLAUDE.md` e `AGENTS.md`; tabela de confirmação do modelo com a origem de cada valor; classificação das alterações preexistentes; identificação completa da org.

# Situações de interrupção

- diretório não é o projeto esperado, ou raiz indeterminada;
- operação Git incompleta;
- org não confirmada ou com indício de Produção;
- branch incoerente com o ambiente de destino;
- alterações locais de origem desconhecida;
- modelo de desenvolvimento ou de branches indeterminado, com impacto na operação prevista;
- ação prevista sem autorização compatível;
- caminho de escrita que redireciona para fora do projeto.

Informar: o que foi detectado, qual risco existe, qual decisão é necessária e qual alternativa segura existe.

# Saída esperada

1. **Projeto** — caminho, raiz, instruções encontradas, API Version, package directories.
2. **Modelo confirmado** — desenvolvimento, packages, branches, promoção, retrieve/deploy, com a origem de cada confirmação e as pendências.
3. **Git** — branch, working tree, divergências, operações incompletas.
4. **Alterações preexistentes** — classificadas, com ação recomendada.
5. **Org e ambiente** — identificação completa e coerência com a branch.
6. **Escopo previsto** — incluindo o que não deve ser modificado.
7. **Autorizações** — necessárias e concedidas.
8. **Bloqueios** — o que impede prosseguir.
9. **Pendências** — o que não foi possível confirmar e quem confirma.
10. **Confirmação explícita de que nenhuma alteração foi realizada.**

# Ações proibidas nesta skill

Criar, alterar ou remover arquivos; `git checkout`, `git pull`, `git stash` ou qualquer alteração do working tree; criar branch; retrieve; deploy; commit; push; qualquer escrita em org; instalar dependências; gravar o relatório na Salesforce-AI-Base — o registro pertence ao projeto atual.

Runbook relacionado: [start-new-demand.md](../../../runbooks/start-new-demand.md) · Skill seguinte: [validate-change-scope](../validate-change-scope/SKILL.md)
