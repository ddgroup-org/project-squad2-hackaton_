---
title: "CI/CD Salesforce — configuração e operação"
category: "operations"
status: "active"
version: "1.0"
last_reviewed: "2026-08-27"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# CI/CD Salesforce — configuração e operação

## Objetivo

Explicar como ativar e operar a esteira definida pela [ADR 0007](../decisions/0007-cicd-multiambiente-com-fila-segura.md). Os arquivos versionados implementam a automação, mas não criam branches, GitHub Environments, credenciais, required reviewers ou branch protections. Esses controles externos precisam ser configurados antes da ativação.

## Fluxo autorizado

| Origem | Destino do PR | Ambiente | Regra |
| --- | --- | --- | --- |
| `feature/*` | `developer` | HML | caminho normal de demanda |
| `hotfix/*` | `developer` | HML | caminho emergencial, sem pular homologação |
| `developer` | `main` | PRD | única promoção permitida para Produção |

Qualquer outra combinação é inelegível. Em especial, PR para `main` cuja origem não seja `developer` deve falhar antes de acessar segredo ou org. Push direto para `developer` ou `main` deve ser impedido por proteção de branch.

```text
feature/* ou hotfix/*
          │
          ▼
     PR → developer ── gate HML ── deploy HML ── gate de merge
                                                  │
                                                  ▼
                                             developer
                                                  │
                                                  ▼
                                    PR developer → main
                                                  │
                                                  ▼
                                  gate PRD ── deploy PRD ── gate de merge
```

## O que cada etapa garante

1. **Quality:** roda em contexto sem segredos e sem token de escrita; verifica formatação, lint, testes, Python e análise estática.
2. **Resolve/validate:** uma execução confiável confirma repositório, evento, PR, branches e SHAs; calcula o delta e valida contra a org correta quando necessário.
3. **Record:** o orquestrador registra somente validação cuja proveniência foi confirmada.
4. **Queue:** o item elegível entra na fila FIFO de seu destino; seleção cria um claim temporário e exclusivo.
5. **Verify:** imediatamente antes de escrever, o orquestrador reconfirma PR, SHAs, validação, aprovações e posição na fila.
6. **Deploy:** o comando declara explicitamente a org. Produção usa somente validação rápida ainda válida para o mesmo delta e a mesma org.
7. **Merge gate:** aprovação de deploy não autoriza merge; o merge tem gate humano próprio.
8. **Final verify/merge:** SHAs são reconfirmados, e o merge squash usa o `head SHA` esperado.

Uma alteração no PR, troca de base, fechamento/reabertura, perda de aprovação ou avanço incompatível da branch de destino invalida o item anterior. O PR volta a passar por qualidade e validação; não reaproveita uma decisão obsoleta.

## Pré-requisitos no GitHub

### 1. GitHub Environments

Criar os seguintes Environments. Em todos, habilitar required reviewers adequados e **prevent self-review**. Wait timers e regras corporativas mais restritivas podem ser adicionados.

| Environment | Conteúdo | Aprovação |
| --- | --- | --- |
| `salesforce-homologation` | credencial e identidade esperada de HML | operação Salesforce em HML |
| `salesforce-production` | credencial e identidade esperada de PRD | operação Salesforce em PRD |
| `salesforce-homologation-destructive` | credencial/identidade de HML, quando o job de remoção precisar acessá-las | adicional para destructive changes em HML |
| `salesforce-production-destructive` | credencial/identidade de PRD, quando o job de remoção precisar acessá-las | adicional para destructive changes em PRD |
| `salesforce-github-merge` | nenhum segredo Salesforce | merge separado do deploy |
| `salesforce-queue-recovery` | nenhum segredo Salesforce | liberar ou reconciliar hard lock após investigação |

Os Environments destructive não substituem o gate normal de destino: um delta com exclusão precisa das duas decisões humanas. Se a implementação separar aprovação e execução em jobs diferentes, o job de aprovação destructive não deve expor credenciais desnecessariamente.

### 2. Segredos e variáveis de org

Nos Environments que executam comandos Salesforce, configurar:

| Tipo | Nome | Valor esperado |
| --- | --- | --- |
| secret | `SFDX_AUTH_URL` | URL de autenticação da conta de integração daquele ambiente |
| variable | `SF_ORG_USERNAME` | username exato da conta autenticada |
| variable | `SF_ORG_ID` | Organization ID exato, sem inferência por alias |
| variable | `SF_ORG_IS_SANDBOX` | `true` para HML e `false` para PRD |

Nunca salvar `SFDX_AUTH_URL` como secret de repositório compartilhado entre ambientes, escrever seu valor em log ou expô-lo a workflow executado a partir do código do PR. A conta de integração deve ter o menor privilégio compatível com validate/deploy e não deve ser reutilizada para tarefas administrativas gerais.

A autenticação é necessária, mas insuficiente. Antes de cada operação, a esteira cria o alias efêmero esperado, obtém username, Organization ID e `IsSandbox` da sessão/org e compara os quatro atributos. Divergência interrompe a execução antes do deploy.

### 3. Proteções de branch

Configurar rulesets ou branch protection para `developer` e `main`:

- exigir Pull Request e pelo menos a quantidade de aprovações definida pelo time;
- dispensar aprovações obsoletas quando houver novo commit;
- exigir resolução de conversas;
- exigir os checks de qualidade e validação publicados pela esteira;
- exigir branch atualizada antes do merge;
- bloquear force push e exclusão;
- restringir push direto, inclusive para automações que não façam parte da esteira;
- usar squash merge e impedir que o merge ignore o `head SHA` verificado.

Adicionar a `main` uma regra de origem na própria esteira: somente `developer` é elegível. Branch protection nativa não expressa sozinha todas as combinações de origem/destino, portanto essa validação continua obrigatória no workflow confiável.

### 4. Permissões de Actions

Manter o token padrão somente leitura. Cada job declara a permissão mínima que usa. Apenas os jobs confiáveis que registram checks, coordenam a fila ou executam o merge recebem escrita pontual em Checks, Issues/Pull Requests ou Contents. Jobs de PR não recebem segredos e não recebem escrita.

Actions e plugins devem usar versões imutáveis/fixadas. Atualização de dependência é uma mudança revisada, conforme [segurança da cadeia de suprimentos](../knowledge/supply-chain-security.md).

## Bootstrap inicial

O bootstrap resolve o problema de confiança inicial: um workflow privilegiado ainda não está disponível de forma confiável enquanto sua versão revisada não existir na branch padrão.

1. Revisar um PR de bootstrap para `main` limitado a `.github/`, arquivos de teste da esteira, dependências de desenvolvimento fixadas e documentação de CI/CD.
2. Confirmar que esse PR não altera metadata Salesforce e não executa qualquer comando com `SFDX_AUTH_URL`.
3. Rodar os checks não privilegiados e revisar o diff manualmente.
4. Obter autorização humana explícita e fazer o merge manual; não usar o orquestrador ainda.
5. Criar `developer` a partir do SHA aprovado de `main`.
6. Criar os GitHub Environments, segredos, variáveis e required reviewers descritos acima.
7. Aplicar as proteções de `developer` e `main`, incluindo os checks realmente publicados após o bootstrap.
8. Confirmar que workflows têm somente as permissões mínimas necessárias.
9. Executar um smoke test sem delta Salesforce para cada destino; confirmar resolução do PR, fila, gates e merge bloqueado até aprovação.
10. Executar uma validação controlada e não destrutiva em HML antes de habilitar o caminho de PRD.
11. Registrar os responsáveis, IDs esperados das orgs e evidências da ativação sem registrar segredos.

Depois do passo 5, a exceção termina. Toda promoção futura para `main` parte de `developer`, inclusive correções urgentes.

## Operação da fila

Há uma fila independente para cada branch de destino. FIFO considera o instante confiável em que o item ficou pronto; em empate, vence o menor número de PR. Um novo commit ou nova base gera nova prontidão, não preserva uma posição obsoleta.

O claim registra o item, a execução proprietária e sua expiração. Seleção e registro são idempotentes, mas uma escrita Salesforce ou merge nunca é repetido apenas porque o job foi reiniciado.

### Hard lock

O destino entra em hard lock quando não é possível provar que org e Git permanecem sincronizados, incluindo:

- falha, timeout ou cancelamento após o início de deploy ou destructive change;
- resposta ambígua da Salesforce sobre o resultado da operação;
- deploy concluído seguido de falha ou bloqueio no merge;
- inconsistência detectada entre o ledger da fila, o PR e a org.

Enquanto existir hard lock, nenhum outro PR daquele destino é selecionado. O outro destino continua independente, desde que não compartilhe a mesma org e esteja consistente.

Recuperação não significa “marcar como pronto”. Um operador autorizado pelo Environment `salesforce-queue-recovery` deve:

1. identificar alias, username, Organization ID e tipo da org;
2. consultar o resultado real do deploy e comparar metadata/SHAs relevantes;
3. confirmar o estado do PR e da branch de destino;
4. decidir se conclui o merge, executa uma reversão autorizada ou invalida a promoção;
5. registrar evidências e a justificativa;
6. somente então liberar a fila.

Reversão, destructive change, merge e nova escrita continuam exigindo suas aprovações próprias durante a recuperação.

## Destructive changes

Remoções usam manifesto separado (`destructiveChanges/destructiveChanges.xml`) e são detectadas pela presença efetiva de tipos, não apenas pela existência do arquivo. Antes de qualquer escrita:

- listar de forma legível os componentes que serão removidos;
- obter a aprovação destructive correspondente ao ambiente;
- reconfirmar os SHAs e a identidade da org;
- preservar o manifesto executado como evidência;
- interromper e acionar hard lock se o resultado ficar parcial ou ambíguo.

Não há retentativa automática de remoção. Um delta sem tipos no `package.xml` e sem tipos no manifesto destructive é no-op de Salesforce.

## Checklist de prontidão

- [ ] `developer` existe a partir do `main` aprovado.
- [ ] `developer` e `main` estão protegidas contra push direto, force push e exclusão.
- [ ] A esteira rejeita qualquer origem diferente de `developer` em PR para `main`.
- [ ] Todos os seis GitHub Environments existem com reviewers e prevenção de autoaprovação.
- [ ] Credenciais ficam somente nos Environments Salesforce correspondentes.
- [ ] `SF_ORG_USERNAME`, `SF_ORG_ID` e `SF_ORG_IS_SANDBOX` foram obtidos e revisados para cada org.
- [ ] Jobs de PR não têm segredo nem permissão de escrita.
- [ ] Checks obrigatórios correspondem aos nomes publicados pela versão ativa dos workflows.
- [ ] Smoke tests sem escrita passaram para os dois destinos.
- [ ] HML foi validada antes de habilitar PRD.
- [ ] Responsáveis por deploy, destructive, merge e recovery conhecem suas aprovações separadas.

## Limites e responsabilidades

A fila reduz concorrência; não transforma deploy + merge em uma transação atômica. Por isso existe o hard lock. GitHub Environments aplicam gates, mas os administradores do repositório continuam responsáveis por reviewers, proteções e bypasses. A esteira não cria credenciais, não cria orgs, não cria ambientes e não substitui a validação humana exigida pela política operacional.

