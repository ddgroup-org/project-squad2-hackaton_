---
title: "ADR 0007 — CI/CD multiambiente com promoção por fila segura"
category: "decision"
status: "active"
version: "1.0"
last_reviewed: "2026-08-27"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# ADR 0007 — CI/CD multiambiente com promoção por fila segura

## Contexto

O repositório nasceu para um hackathon com uma única branch e uma única org. Esse modelo não separa homologação de Produção, não serializa deploys concorrentes e não oferece uma promoção auditável entre ambientes. A evolução solicitada adota uma esteira com branches protegidas, validação automática, aprovações humanas e uma fila por ambiente.

Essa evolução não reduz as proteções de [segurança operacional](../knowledge/operational-safety-policy.md) e [segurança de ambientes](../knowledge/environment-safety.md). Em especial, deploy em homologação, deploy em Produção, merge e destructive changes continuam exigindo as aprovações aplicáveis; uma aprovação não substitui outra.

## Decisão

Adotar o seguinte fluxo de promoção:

```text
feature/* ─┐
           ├─ PR → developer → homologação (HML)
hotfix/* ──┘

developer ─── PR → main → Produção (PRD)
```

- `developer` é a única branch de destino para `feature/*` e `hotfix/*`.
- `developer` é a única branch de origem admitida em PR para `main`.
- Hotfix não ignora homologação nem abre caminho direto para `main`.
- Push direto em `developer` e `main` é proibido; ambas devem ser protegidas.
- O merge padrão é squash, preservando um commit auditável por PR.

### Qualidade e validação

Todo PR executa verificações sem credenciais de org: formatação, lint, testes unitários, validação dos scripts Python e análise estática. Código vindo do PR não recebe segredo nem token de escrita.

Depois da qualidade, uma execução confiável, carregada a partir da branch padrão, resolve novamente o PR e confirma repositório, branch de origem, branch de destino, `head SHA` e `base SHA`. Mudança de código, troca de base, reabertura ou qualquer divergência invalida a prontidão anterior e exige nova validação.

Alterações Salesforce são validadas contra a org correspondente antes de entrarem na fila. Delta vazio é um no-op de Salesforce, não um deploy vazio; o PR ainda segue os gates de merge. Os manifests de adição e remoção são tratados separadamente, e destructive changes nunca são inferidas pela simples ausência de um arquivo.

### Identidade da org

Antes de cada validação ou deploy, a execução deve:

1. autenticar a credencial do GitHub Environment com um alias efêmero e conhecido;
2. obter o username autenticado com `sf org display`;
3. consultar a própria org para obter o Organization ID e `Organization.IsSandbox`;
4. comparar username, Organization ID e tipo de ambiente com os valores esperados do Environment;
5. declarar `--target-org` em todo comando que alcance a org.

Qualquer ausência ou divergência interrompe a operação. Alias, nome do Environment ou nome da branch, isoladamente, não identificam uma org.

### Aprovações por GitHub Environments

Os gates humanos são implementados com GitHub Environments protegidos, required reviewers e prevenção de autoaprovação:

| Environment | Finalidade |
| --- | --- |
| `salesforce-homologation` | autorizar operação Salesforce em HML |
| `salesforce-production` | autorizar operação Salesforce em PRD |
| `salesforce-homologation-destructive` | aprovação adicional e explícita para remoções em HML |
| `salesforce-production-destructive` | aprovação adicional e explícita para remoções em PRD |
| `salesforce-github-merge` | autorização humana separada para o merge |
| `salesforce-queue-recovery` | recuperação manual e auditável de uma fila bloqueada |

Um deploy com remoção requer tanto a aprovação do ambiente de destino quanto a aprovação destructive correspondente. Aprovação de PR, validação bem-sucedida, aprovação de deploy, aprovação destructive e autorização de merge são decisões distintas.

### Fila e concorrência

Cada destino (`developer`/HML e `main`/PRD) tem uma fila FIFO independente. Um item só fica pronto depois que todas as verificações e aprovações anteriores à fila estiverem válidas. A ordem é definida pelo instante confiável de prontidão, com o número do PR como desempate estável.

O orquestrador Python é a fonte da decisão de fila e deve:

- aceitar somente registros produzidos por execuções confiáveis e verificáveis;
- excluir PR fechado, draft, inelegível, desatualizado ou com `head SHA`/`base SHA` divergente;
- criar um claim com execução e expiração antes de selecionar um item;
- voltar a verificar elegibilidade imediatamente antes do deploy e imediatamente antes do merge;
- tornar registro e seleção idempotentes;
- nunca selecionar dois itens simultaneamente para o mesmo destino.

Uma falha antes de qualquer escrita pode adiar o item sem bloquear os demais, desde que a operação seja comprovadamente idempotente. Falha, timeout ou estado ambíguo depois de iniciar uma escrita Salesforce aciona um **hard lock por destino**: nenhum outro PR daquele destino pode ser processado até recuperação humana pelo Environment `salesforce-queue-recovery`. Não há retentativa automática de deploy, destructive change ou merge após falha parcial.

Se o deploy concluir e o merge não concluir, a fila também fica em hard lock, pois org e Git deixam de estar comprovadamente sincronizados. A recuperação deve verificar o estado real nos dois lados, registrar evidência e escolher conscientemente entre concluir a promoção ou executar uma reversão autorizada.

### Produção

O PR `developer` → `main` usa validação de Produção associada ao mesmo delta e aos mesmos SHAs. O deploy rápido só pode reutilizar uma validação ainda válida e confirmada para a org produtiva correta. Imediatamente antes do deploy e do merge, a esteira reconfirma os SHAs e a identidade da org.

Nenhuma automação desta ADR concede autorização permanente para Produção. Cada execução continua sujeita aos gates humanos e à matriz de aprovação do projeto.

### Bootstrap

Workflows privilegiados só são confiáveis depois que sua versão revisada existe na branch padrão. Por isso, a implantação inicial admite uma única exceção controlada:

1. um PR de bootstrap pode levar somente a esteira, seu orquestrador, testes, dependências fixadas e esta documentação diretamente a `main`;
2. esse PR não executa deploy, merge automático nem lê credenciais Salesforce;
3. revisão e merge são manuais e exigem autorização explícita;
4. após o merge, cria-se `developer` a partir do `main` vigente, configuram-se Environments e proteções, e executa-se um smoke test sem escrita;
5. concluído o bootstrap, a exceção deixa de existir e todo PR para `main` deve vir de `developer`.

O procedimento completo e os pré-requisitos externos estão em [docs/ci-cd.md](../docs/ci-cd.md).

## Consequências

- Homologação e Produção passam a ter linhas de promoção separadas e rastreáveis.
- Deploys para a mesma org são serializados; falha ambígua favorece interrupção e investigação, não throughput.
- A ativação depende de configuração externa no GitHub e de credenciais/identidades confirmadas; versionar os workflows, sozinho, não ativa a esteira.
- O tempo de entrega inclui aprovações humanas distintas para operação na org, remoções e merge.
- A branch `main` continua sendo a fonte versionada de Produção, enquanto `developer` representa o estado promovido para homologação.
- O fluxo local `demanda.md` → `/executar-demanda` continua válido para execução e evidências, mas a entrega remota passa obrigatoriamente pelo modelo de branches desta ADR.

## Alternativas descartadas

| Alternativa | Por que foi descartada |
| --- | --- |
| Continuar com uma branch e uma org | não separa homologação de Produção nem oferece promoção auditável |
| Permitir `hotfix/*` diretamente em `main` | ignora homologação e cria um segundo caminho produtivo menos controlado |
| Usar somente `concurrency` do GitHub | serializa execuções, mas não modela elegibilidade, obsolescência, idempotência nem recuperação após escrita parcial |
| Retentar deploy automaticamente | uma falha pode ter produzido efeito parcial; nova escrita sem conhecer o estado viola a política operacional |
| Tratar aprovação de PR como autorização de deploy e merge | agrega decisões com impactos diferentes e viola a matriz de aprovação humana |
| Confiar no alias para escolher a org | alias é local e reatribuível; não comprova username, Organization ID nem tipo de ambiente |

