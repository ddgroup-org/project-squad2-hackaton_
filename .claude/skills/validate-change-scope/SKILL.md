---
name: validate-change-scope
description: Use antes de concluir uma demanda para comparar o que foi alterado com o que estava previsto, detectando alterações fora do escopo, segredos, temporários, arquivos no diretório errado e mudanças concorrentes. Bloqueia a conclusão quando houver alteração não justificada.
---

# Objetivo

Comprovar que o que foi alterado corresponde ao que foi planejado — e que nada além disso entrou.

**Esta skill bloqueia a conclusão** quando encontrar alteração não justificada. Ela não corrige: reporta e interrompe.

# Quando usar

Antes de declarar uma demanda concluída; antes de preparar um Pull Request; após um retrieve; após qualquer operação que possa ter trazido conteúdo inesperado.

# Pré-condições

- escopo previsto registrado no pre-flight (arquivos e componentes previstos, e os que não devem ser modificados);
- alterações realizadas e disponíveis para inspeção.

Sem escopo previsto registrado, esta skill não tem referência de comparação — nesse caso, reconstruí-lo a partir da demanda e declarar que foi reconstruído após o fato, o que reduz a confiança da validação.

# Entradas

```text
{ESCOPO_PREVISTO}    arquivos e componentes planejados
{NAO_MODIFICAR}      arquivos e componentes explicitamente fora do escopo
{DEMANDA}            identificador e critérios de aceite
{PROJECT_ROOT}       caminho absoluto do projeto
```

# Documentos aplicáveis

[operational-safety-policy.md](../../../knowledge/operational-safety-policy.md) · [security-standards.md](../../../knowledge/security-standards.md#52-detecção-antes-de-versionar) · [instruction-precedence.md](../../../knowledge/instruction-precedence.md) · [environment-safety.md](../../../knowledge/environment-safety.md#5-contaminação-cruzada-entre-ambientes)

---

# Procedimento

## 1. Levantar o que foi de fato alterado

```bash
git status
git diff --stat
git diff
```

Listar todos os arquivos criados, alterados, removidos e não rastreados.

## 2. Comparar arquivos previstos × alterados

| Arquivo alterado | Estava previsto | Justificativa | Situação |
| --- | --- | --- | --- |

Classificar cada arquivo em uma das quatro situações:

```text
Previsto e alterado             esperado
Previsto e não alterado         verificar se a demanda está incompleta
Não previsto e alterado         exige justificativa — bloqueia se não houver
Explicitamente fora do escopo   bloqueio, sem exceção
```

**A segunda situação é a mais esquecida:** um arquivo previsto e não alterado pode indicar entrega incompleta, não escopo bem controlado.

## 3. Comparar componentes previstos × recuperados

Quando houver retrieve, comparar o que foi planejado recuperar com o que efetivamente veio:

| Componente | Previsto | Recuperado | Pertence à demanda | Ação |
| --- | --- | --- | --- | --- |

Retrieve traz ruído com frequência. Verificar especificamente:

- alteração de API Version não solicitada;
- reordenação de elementos em XML;
- entradas de Profile, Permission Set ou Layout de outras demandas;
- campos, Record Types ou automações criados por outra pessoa;
- remoção de elementos que existiam localmente e não vieram no retrieve.

## 4. Identificar alterações fora do escopo

Para cada arquivo não previsto:

```text
1. Por que foi alterado?
2. A alteração era necessária para a demanda?
3. É consequência de ferramenta (formatação, reordenação)?
4. Pertence a outra demanda ou a outra pessoa?
5. É débito técnico corrigido por conta própria?
```

**Ponto de decisão:** débito técnico corrigido fora do pedido é **alteração fora do escopo**, ainda que a correção seja boa. Reverter e registrar como recomendação separada — ver [salesforce-development-principles.md](../../../knowledge/salesforce-development-principles.md#15-alteração-mínima-necessária).

## 5. Verificar dependências do que foi alterado

Alteração dentro do escopo pode ter efeito fora dele:

- consumidores das classes e métodos alterados;
- assinaturas públicas modificadas;
- campos referenciados por Flows, fórmulas, relatórios e integrações;
- permissões alteradas e quem é afetado;
- testes existentes que cobrem o comportamento alterado.

Efeito não previsto sobre um dependente é **expansão de escopo**, mesmo sem arquivo adicional alterado.

## 6. Verificar mudanças concorrentes

```bash
git fetch origin
git log HEAD..origin/{DEVELOPMENT_BASE_BRANCH} --oneline
```

- houve commit novo na branch-base tocando os mesmos arquivos?
- há Pull Request aberto sobre os mesmos componentes?
- alguém alterou os mesmos componentes na org compartilhada?

**Ponto de decisão:** mudança concorrente no mesmo artefato **interrompe**. Ver [handle-metadata-conflict.md](../../../runbooks/handle-metadata-conflict.md).

## 7. Verificar segredos

Inspecionar o diff completo procurando **valor real** associado a:

```text
token            password         secret
client_secret    private_key      BEGIN PRIVATE KEY
Authorization: Bearer             session id
certificado      chave de API
```

Termo genérico em documentação conceitual não é vazamento; **valor real associado é**.

**Ponto de decisão:** segredo detectado **interrompe imediatamente**, antes de qualquer push. Remover o valor, tratar a credencial como comprometida e reportar sem incluir o valor no relatório.

## 8. Verificar arquivos temporários e gerados

Não devem entrar no commit:

```text
logs e saídas de execução        arquivos de cobertura
relatórios de análise estática   resultados de teste em arquivo
arquivos de trabalho e rascunho  backups (.bak, .orig, .rej)
metadata recuperada fora do escopo
capturas de tela e evidências binárias, salvo quando o projeto exigir
```

Conflitos mal resolvidos deixam `.orig` e `.rej` — verificar explicitamente.

## 9. Verificar arquivos gerados no diretório errado

Dois erros distintos:

**9.1 Dentro do projeto, no lugar errado**
Análise em `docs/`? Manifest em `manifest/`? Script em `scripts/`? Evidência em `docs/evidence/`? Arquivo correto no diretório errado dificulta a manutenção e some na próxima demanda.

**9.2 Fora do projeto**
Verificar se algum arquivo foi criado fora de `{PROJECT_ROOT}` — em outro projeto, no diretório de configuração global ou **dentro da Salesforce-AI-Base**.

**Ponto de decisão:** artefato de demanda gravado na Salesforce-AI-Base é **bloqueio**. Mover para o projeto e remover da base. Ver [operational-safety-policy.md](../../../knowledge/operational-safety-policy.md#41-a-base-não-é-diretório-de-saída).

## 10. Emitir a decisão

```text
APROVADO             escopo íntegro; nenhuma pendência
APROVADO COM RESSALVA alterações fora do escopo justificadas e aceitas por quem decide
BLOQUEADO            alteração não justificada, segredo, temporário, arquivo em local indevido
                     ou mudança concorrente não tratada
```

**Bloqueado impede a conclusão da demanda.** Não é recomendação: é gate.

---

# Validações

- [ ] Todos os arquivos alterados listados e classificados.
- [ ] Arquivos previstos e não alterados verificados quanto a entrega incompleta.
- [ ] Nenhum arquivo explicitamente fora do escopo modificado.
- [ ] Componentes recuperados conferidos contra o previsto.
- [ ] Dependências do que foi alterado avaliadas.
- [ ] Mudanças concorrentes verificadas.
- [ ] Nenhum segredo no diff.
- [ ] Nenhum arquivo temporário, gerado ou de backup no commit.
- [ ] Nenhum artefato criado fora do projeto ou na Salesforce-AI-Base.
- [ ] Decisão explícita emitida.

# Evidências

Saída de `git status` e `git diff --stat`; tabela de previsto × alterado; tabela de previsto × recuperado; resultado da verificação de segredos, com valores mascarados; lista de dependências avaliadas; registro de mudanças concorrentes.

# Situações de interrupção

- alteração fora do escopo sem justificativa;
- alteração em componente explicitamente listado como intocável;
- segredo detectado;
- arquivo temporário ou gerado no diff;
- artefato criado fora do projeto ou dentro da Salesforce-AI-Base;
- mudança concorrente no mesmo artefato;
- assinatura pública alterada sem avaliação de consumidores;
- escopo significativamente maior do que o planejado.

# Saída esperada

1. **Resumo** — escopo previsto × escopo real, em uma frase.
2. **Arquivos alterados**, classificados nas quatro situações.
3. **Componentes recuperados**, quando houver retrieve.
4. **Alterações fora do escopo**, com justificativa ou ausência dela.
5. **Dependências afetadas**.
6. **Mudanças concorrentes detectadas**.
7. **Verificação de segredos** — resultado, com valores mascarados.
8. **Arquivos temporários, gerados ou em local indevido**.
9. **Decisão** — aprovado, aprovado com ressalva ou **bloqueado**.
10. **Ações necessárias** antes de concluir.

# Ações proibidas nesta skill

Corrigir por conta própria as alterações fora do escopo detectadas; reverter arquivos sem autorização; executar comandos destrutivos para "limpar" o working tree; commit, push ou abertura de Pull Request; aprovar escopo com alteração não justificada; gravar o relatório na Salesforce-AI-Base.

Skill anterior: [salesforce-preflight-check](../salesforce-preflight-check/SKILL.md) · Runbooks relacionados: [handle-metadata-conflict.md](../../../runbooks/handle-metadata-conflict.md), [resolve-org-repository-drift.md](../../../runbooks/resolve-org-repository-drift.md)
