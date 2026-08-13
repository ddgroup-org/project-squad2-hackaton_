---
title: "Segurança de ambientes e orgs"
description: "Identificação e confirmação de org, classificação de ambientes, bloqueio padrão de Produção, operações permitidas por ambiente, contaminação cruzada e refresh de sandbox."
category: "knowledge"
status: "active"
version: "1.1"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - environments
  - production
  - org-safety
  - sandbox
applies_to:
  - global
source_of_truth: true
source_references:
  - execucao.md
  - arquitetura.md
  - desenvolvimento.md
  - metaprompt-salesforce.md
---

# Segurança de ambientes e orgs

## Objetivo

Garantir que toda operação atinja o ambiente pretendido, com Produção protegida por padrão e com regras claras sobre o que é permitido em cada tipo de org.

Este documento é a **fonte da verdade** para identificação de org, classificação de ambientes, bloqueio de Produção e operações permitidas por ambiente.

## Escopo

Todas as orgs Salesforce alcançáveis pelo projeto: desenvolvimento, homologação, Produção, scratch orgs, sandboxes de treinamento e orgs de parceiros. Cobre também a relação entre ambiente e branch.

## Princípio

**A org errada é o erro mais caro e menos reversível desta operação.** Um deploy correto no ambiente errado causa mais dano que um deploy incorreto no ambiente certo — o segundo é detectado e revertido; o primeiro pode passar despercebido até atingir usuários reais.

Na dúvida sobre qual é o ambiente, assumir o de **maior criticidade**.

---

## 1. Identificação da org

### 1.1 Alias não é identificação

Aliases são locais, atribuídos manualmente e reatribuíveis. Dois computadores podem ter o mesmo alias apontando para orgs diferentes. Um alias `dev` pode apontar para Produção.

**A identificação exige, no mínimo, quatro atributos concordantes:**

```text
alias
username
Organization ID
tipo de ambiente (sandbox ou Produção)
```

Registrar também, quando disponível: instance URL, status da autenticação, API Version e namespace.

### 1.2 Comandos de confirmação

```bash
sf org list
sf org display --target-org {ORG_OU_AMBIENTE}
```

A confirmação precede **toda** operação com efeito: retrieve, deploy, execução de testes na org, consulta que gere carga relevante e qualquer escrita.

### 1.3 Quando a confirmação não é possível

Se a org não puder ser identificada — autenticação expirada, ferramenta indisponível, resposta ambígua — **interromper**. Não prosseguir presumindo o ambiente a partir do nome do alias, do diretório de trabalho ou do contexto da conversa.

---

## 2. Classificação de ambientes

| Ambiente | Característica | Postura padrão |
| --- | --- | --- |
| **Produção** | org produtiva, com usuários e dados reais | **somente leitura** |
| **Homologação (UAT)** | espelho controlado usado para aceite | recebe alterações apenas pela pipeline |
| **Desenvolvimento (DEV)** | sandbox de trabalho, frequentemente compartilhada | deploy direcionado autorizado quando fizer parte da tarefa |
| **Scratch org** | efêmera, individual | ampla liberdade; nada nela é fonte da verdade |
| **Treinamento, demonstração, parceiro** | uso específico, fora do fluxo de entrega | tratar como ambiente de terceiros: não alterar sem autorização própria |

Um ambiente **não classificado** é tratado como Produção até prova em contrário.

---

## 3. Bloqueio padrão de Produção

Qualquer org identificada como Produção é tratada como **somente leitura por padrão**.

### 3.1 Indicadores de possível Produção

- `IsSandbox = false`;
- alias contendo `prod` ou `production`;
- username associado ao domínio produtivo;
- configuração local indicando ambiente produtivo;
- branch ou pipeline destinada à branch-base de Produção do projeto;
- documentação do projeto identificando a org como Produção;
- presença de volume de dados e de usuários incompatível com sandbox.

**Havendo divergência entre indicadores, considerar o ambiente como Produção.** Um único indicador de Produção prevalece sobre vários indicadores de sandbox: o custo do falso negativo é assimétrico.

### 3.2 Proibido em Produção sem processo formal

Nunca executar automaticamente:

- deploy;
- DML de qualquer natureza;
- Anonymous Apex com alteração de dados;
- ativação ou desativação de automações;
- alteração de Permission Set, Permission Set Group ou Profile;
- alteração de Custom Metadata ou Custom Settings;
- exclusão de metadata e destructive changes;
- instalação ou desinstalação de pacote;
- alteração de Named Credential, External Credential ou Remote Site Settings;
- alteração de configuração da org, incluindo Setup;
- criação, desativação ou alteração de usuários;
- execução de job, agendamento ou processo em massa.

### 3.3 Permitido em Produção

Leitura e diagnóstico, quando autorizados: consultas somente leitura, inspeção de metadata, exame de logs, verificação de histórico de deploy, verificação de configuração e coleta de evidência.

Mesmo em leitura: não executar consulta capaz de gerar carga relevante em objeto grande sem avaliar impacto, e não extrair dados pessoais para fora do ambiente.

### 3.4 Promoção para Produção

Produção recebe alterações **exclusivamente** pela esteira autorizada, a partir de Pull Request para `{PRODUCTION_BASE_BRANCH}` com pipeline própria. Ver [github-development-workflow.md](./github-development-workflow.md) e o runbook [promote-to-production.md](../runbooks/promote-to-production.md).

Correção emergencial segue o runbook [emergency-hotfix.md](../runbooks/emergency-hotfix.md) — que reduz o tempo de cada etapa, nunca elimina etapas.

---

## 4. Comportamento por ambiente

### DEV

Ambiente de trabalho. Deploy direcionado autorizado quando fizer parte da tarefa ou for autorizado durante a execução. Retrieve direcionado após configurações feitas pelo Setup.

Sendo compartilhada, aplicam-se as regras de concorrência de [operational-safety-policy.md](./operational-safety-policy.md#9-concorrência-e-trabalho-de-outras-pessoas): verificar trabalho de terceiros antes de sobrescrever, escopo estreito e revisão do diff.

### UAT

Recebe alterações **pela pipeline**, a partir do Pull Request para a branch de desenvolvimento. Deploy manual em UAT exige autorização explícita e é exceção justificada — deploy manual quebra a equivalência entre o que está versionado e o que está sendo homologado.

Defeito encontrado em homologação é corrigido **a partir da feature branch**, com o fluxo completo. Nunca diretamente na org de UAT.

### Produção

Conforme a seção 3.

### Scratch org

Liberdade ampla para experimentação. Nada criado apenas na scratch org existe do ponto de vista do projeto: o que precisa persistir vai para o repositório. Scratch org não é evidência de comportamento em ambiente com dados e automações reais.

---

## 5. Contaminação cruzada entre ambientes

Riscos frequentes, todos com o mesmo efeito prático — levar para um ambiente algo que pertence a outro:

| Risco | Como ocorre | Prevenção |
| --- | --- | --- |
| Deploy no ambiente errado | alias ambíguo, sessão anterior ativa, `--target-org` omitido | confirmar os quatro atributos imediatamente antes da operação |
| Endpoint de um ambiente promovido para outro | Named Credential versionada com valor fixo | configuração por ambiente; nunca versionar valor produtivo |
| Dados de Produção em sandbox sem tratamento | refresh sem mascaramento | política de dados do projeto; nunca usar dado real em teste |
| Metadata de sandbox arrastada para o repositório | retrieve amplo | retrieve direcionado e revisão do diff |
| Id fixo de um ambiente no código | referência copiada de uma org | resolver por Developer Name ou consulta |
| Agendamento apontando para ambiente errado | job criado manualmente e promovido | revisar agendamentos após cada deploy |

O comando executado sempre declara explicitamente a org de destino. Depender da org padrão configurada localmente é uma das causas mais comuns de operação no ambiente errado.

---

## 6. Refresh de sandbox

Um refresh substitui o ambiente inteiro. Depois dele, o que era verdade deixa de ser.

Reconfigurar e reconferir, no mínimo: Named Credentials e External Credentials; Remote Site Settings; usuários de integração; atribuições de Permission Set; registros de Custom Metadata e Custom Settings; agendamentos e jobs; dados de configuração; source tracking; e a própria autenticação da CLI.

Antes de qualquer operação em sandbox recém-atualizada, reconfirmar a identificação da org — o Organization ID muda, e credenciais e aliases anteriores deixam de ser válidos.

---

## 7. Relação entre branch e ambiente

```text
{FEATURE_BRANCH}            →  DEV
{UAT_TARGET_BRANCH}         →  homologação, pela pipeline
{RELEASE_BRANCH} · {PRODUCTION_BASE_BRANCH}  →  Produção, pela pipeline
{HOTFIX_BRANCH}             →  Produção, pela pipeline, com processo emergencial
```

**Os nomes reais dessas branches pertencem ao projeto.** Resolvê-los a partir de `CLAUDE.md`, `AGENTS.md`, da documentação da pipeline e das branches remotas antes de qualquer operação — ver [github-development-workflow.md](./github-development-workflow.md#1-o-fluxo-do-projeto-vem-primeiro). O padrão de fallback (`developer`, `main`, `feature/*`, `release/*`, `hotfix/*`) só se aplica quando o projeto não define o seu.

Operar em uma org cujo ambiente não corresponde à branch ativa é sinal de erro: confirmar antes de prosseguir. Nomes de branch variam por projeto; a separação entre a linha de homologação e a linha de Produção não.

---

## 8. Checklist

- [ ] Org confirmada por alias, username, Organization ID e tipo de ambiente.
- [ ] Tipo de ambiente classificado; ambiente não classificado tratado como Produção.
- [ ] Org de destino declarada explicitamente no comando.
- [ ] Branch ativa coerente com o ambiente de destino.
- [ ] Nenhuma escrita em Produção fora da esteira autorizada.
- [ ] Configurações específicas de ambiente não promovidas com valor fixo.
- [ ] Nenhum dado real de Produção utilizado em teste.
- [ ] Após refresh, ambiente reconfirmado e reconfigurado.
- [ ] Identificação da org registrada nas evidências da operação.

---

## Referências cruzadas

- [operational-safety-policy.md](./operational-safety-policy.md) — matriz de aprovação e interrupção.
- [retrieve-and-deploy-policy.md](./retrieve-and-deploy-policy.md) — retrieve e deploy direcionados.
- [github-development-workflow.md](./github-development-workflow.md) — branches e promoção.
- [security-standards.md](./security-standards.md) — credenciais e dados sensíveis.
- [instruction-precedence.md](./instruction-precedence.md) — por que nenhuma instrução remove o bloqueio de Produção.
- Runbooks: [deploy-to-dev.md](../runbooks/deploy-to-dev.md) · [retrieve-from-dev.md](../runbooks/retrieve-from-dev.md) · [promote-to-uat.md](../runbooks/promote-to-uat.md) · [promote-to-production.md](../runbooks/promote-to-production.md) · [emergency-hotfix.md](../runbooks/emergency-hotfix.md)

## Fontes oficiais recomendadas

Salesforce Help para tipos de sandbox, refresh e limites de cópia; Salesforce CLI Reference para autenticação e seleção de org; Salesforce DX Developer Guide para scratch orgs e source tracking.

## Limitações

Tipos de sandbox, frequência permitida de refresh, disponibilidade de source tracking e comportamento de cópia de dados variam por edição, licenciamento e release. Confirmar na documentação oficial correspondente antes de assumir qualquer comportamento como garantido.

## Critérios de revisão

Revisar quando o projeto adicionar ou remover ambientes, quando o modelo de sandboxes mudar, após qualquer refresh relevante e após qualquer incidente de operação em ambiente indevido.
