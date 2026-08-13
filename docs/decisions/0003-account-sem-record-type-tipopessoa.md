---
title: "ADR 0003 — Account como objeto único com TipoPessoa__c, sem Record Type"
category: "decision"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# ADR 0003 — Account como objeto único com TipoPessoa__c, sem Record Type

## Contexto

A [ADR 0001](0001-modelo-conta-b2b-b2c-sem-person-accounts.md) decidiu modelar PJ/PF via dois Record Types em Account (Business Account / Individual Customer), descartando Person Accounts.

O **BRD oficial** (`entregaveis/01_BRD_Cromatta_Quimica_Squad02.pdf`, v1.0, aprovado por Gabriel Jacob — cliente — e assinado com Paulo Carvalho como Tech Lead) define o modelo de Account de forma diferente, na seção 3.1: um único objeto Account, com um campo `TipoPessoa__c` (picklist PF/PJ) determinando o tipo de cliente — sem Record Type.

Adicionalmente, uma reanálise arquitetural (agente `salesforce-architect`, ver [evidencias/demandas/reanalise-demanda-01.md](../evidencias/demandas/reanalise-demanda-01.md)) confirmou via consulta direta à org `cromatta-hackathon` que:

- **Person Accounts já está habilitado nesta org** (existe o Record Type nativo `PersonAccount`, `IsPersonType = true`) — feature **irreversível**, habilitada fora do fluxo Claude/`/executar-demanda` (ver [ADR 0004](0004-reconciliacao-permissionsets-fora-do-fluxo.md) sobre a origem dessas alterações).
- Já existe um Record Type customizado `Business_Account` criado na org, hoje sem uso, remanescente da tentativa de seguir a ADR 0001 antes da divergência ser percebida.
- Nenhum dado real (`Account`/`Opportunity`) foi criado ainda — o custo de adotar o modelo do BRD agora é próximo de zero.

## Decisão

**O BRD prevalece.** Adotar Account como objeto único, com o campo `TipoPessoa__c` (picklist: PF | PJ) como campo de segmentação primário — não usar Record Type para essa distinção.

- `Account.RecordType` deixa de ser o campo de segmentação; relatórios, Flows e Permission Sets devem filtrar por `TipoPessoa__c`.
- O Record Type customizado `Business_Account`, já criado na org, **não deve ser usado** nem referenciado em nova automação — não será removido nesta fase (remoção de Record Type em uso incerto exige cuidado e não é prioridade do hackathon), mas fica marcado como órfão.
- Person Accounts, já habilitado na org, **não é utilizado** por este modelo — nenhum registro deve ser criado como Person Account; todo Account novo é o objeto padrão com `TipoPessoa__c` preenchido. A feature fica habilitada (é irreversível) mas inerte para os fins deste projeto.

## Consequências

- `business-scenario.md` e `architecture.md` precisam ser atualizados para refletir `TipoPessoa__c` em vez de "Business Account / Individual Customer (Record Type)".
- Qualquer Flow/relatório/dashboard que segmente por tipo de cliente usa `Account.TipoPessoa__c = 'PF'` ou `'PJ'`.
- Contact continua 1:N em relação a Account para ambos os tipos (o BRD não distingue cardinalidade de Contact por `TipoPessoa__c`) — diferente da ADR 0001, que previa 1:1 para o antigo "Individual Customer".
- Esta é uma decisão de negócio formalizada pelo cliente e pelo tech lead via documento aprovado — não deve ser revertida sem novo BRD ou CR (Change Request, ver Parte 7 do BRD).

## Alternativas descartadas

| Alternativa | Por que foi descartada |
| --- | --- |
| Manter Record Type (ADR 0001) | Diverge do BRD oficial, que é a fonte de verdade aprovada pelo cliente e pelo tech lead |
| Usar Person Accounts nativamente (já habilitado) | O BRD não define esse modelo; adotá-lo agora seria uma decisão de arquitetura nova, não solicitada, além de mudar o formato de conversão de Lead descrito na seção 3.2 do BRD |
