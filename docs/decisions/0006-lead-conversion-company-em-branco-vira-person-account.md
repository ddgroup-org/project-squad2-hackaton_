---
title: "ADR 0006 — Conversão de Lead sem Company: Flow before-save evita Person Account indesejada"
category: "decision"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# ADR 0006 — Conversão de Lead sem Company: Flow before-save evita Person Account indesejada

## Contexto

Bug reportado pelo tech lead: ao converter um Lead sem o campo `Company` preenchido, o Salesforce cria automaticamente uma **Person Account** em vez de uma Account normal.

Isso é comportamento padrão documentado da plataforma: quando Person Accounts está habilitado na org — confirmado (RecordType `PersonAccount`, `IsPersonType = true`, ativo em Account, ver [ADR 0003](0003-account-sem-record-type-tipopessoa.md)/[ADR 0004](0004-reconciliacao-permissionsets-fora-do-fluxo.md)) — e o Lead convertido não tem `Company`, a conversão usa a Person Account em vez da Account padrão, por não haver nome de empresa para nomear uma Account de negócio.

Isso conflita diretamente com a decisão da ADR 0003 (Account como objeto único, com `TipoPessoa__c`, **sem** Person Accounts) e afeta principalmente Leads PF: a Validation Rule `Lead_PF_Campos_Obrigatorios` (demanda-06) exige `LastName`, `CNPJ_CPF__c` e `Email` para PF, mas **não** exige `Company` — corretamente, pessoa física não tem razão social. Isso deixa o campo em branco até a conversão, disparando o bug.

Person Accounts não pode ser desabilitado (feature irreversível uma vez habilitada na org). Tornar `Company` obrigatório para Lead PF violaria a regra de negócio (BRD 1.3.3, resposta do cliente: PJ tem razão social, PF não).

**Achado crítico durante a revisão** (agente `flow-reviewer`, ver `evidencias/demandas/demanda-12.md`): `TipoPessoa__c` não é campo obrigatório em Lead — um Lead pode ser salvo com `TipoPessoa__c` em branco. Uma primeira versão desta automação, restrita a `TipoPessoa__c = 'PF'`, deixava esse terceiro caso (Lead sem `TipoPessoa__c` e sem `Company`) reexposto ao mesmo bug. Isso não é uma decisão de negócio sobre o que fazer com Leads não classificados — é uma lacuna puramente técnica no critério de entrada da automação.

## Decisão

Criar um Flow **before-save** (`Lead_BeforeSave_PreencheCompany`, `RecordBeforeSave`, Create and Update) no objeto Lead que preenche `Company` automaticamente com o nome do Lead (`FirstName + LastName`, ou só `LastName` quando `FirstName` estiver em branco) sempre que `Company` estiver em branco no momento do save — **sem filtrar por `TipoPessoa__c`**, para cobrir também o caso de Leads sem classificação de tipo de pessoa.

- Não torna `Company` obrigatório — a Validation Rule `Lead_PF_Campos_Obrigatorios` não é alterada.
- Não desabilita nem tenta contornar Person Accounts — apenas garante que a pré-condição do bug (`Company` em branco) nunca ocorra no momento da conversão.
- Para Lead PJ, é um no-op: `Company` já é obrigatório pela Validation Rule `Lead_PJ_Campos_Obrigatorios`, então o Flow nunca encontra `Company` em branco nesse caso.
- Automação 100% declarativa (Flow), sem Apex — consistente com a ordem de preferência declarativa do projeto (`architecture.md`).

### Validação

Testado via `sf apex run` (matriz completa, registros de teste removidos após validação):

| Cenário | Resultado |
| --- | --- |
| Lead PF sem `Company` | `Company` preenchido automaticamente; conversão gera Account com `IsPersonAccount = false`, `TipoPessoa__c = 'PF'` |
| Lead PF com `Company` já preenchido | Inalterado (Flow não interfere) |
| Lead PJ | Inalterado (já tinha `Company` pela Validation Rule) |
| Lead com `TipoPessoa__c` em branco e `Company` em branco (achado crítico) | `Company` preenchido automaticamente; conversão gera Account com `IsPersonAccount = false` |
| 3 Leads PF sem `Company` na mesma transação (bulk) | Todos preenchidos corretamente |

### Nota operacional — versão anterior do Flow

Uma primeira versão (`Lead_PF_Preenche_Company_Automatico`, restrita a `TipoPessoa__c = 'PF'`) foi deployada, revisada pelo `flow-reviewer`, e substituída por esta (`Lead_BeforeSave_PreencheCompany`) após o achado crítico. A tentativa de excluir a versão antiga via `sf project delete source --metadata "Flow:..."` falhou com o erro da plataforma `insufficient access rights on cross-reference id` — limitação conhecida da Metadata API para exclusão/desativação de Flow (a operação "Deactivate" do Setup UI não tem equivalente direto via deploy/delete de metadata). A versão antiga permanece **ativa** na org, mas não está no `manifest/package.xml` nem será versionada no repositório a partir desta demanda.

Isso não é uma alteração manual na org (não viola a regra central 1 do `CLAUDE.md`) — é uma automação já criada via Claude que não pôde ser removida via Claude. Fica registrado como pendência de limpeza manual (Setup → Fluxo → Desativar, ~10 segundos, exceção explícita da regra central 1) para quem tiver acesso à org. Risco enquanto não for feita: nenhum — a lógica da versão antiga é idêntica e idempotente (só preenche `Company` se estiver em branco), então rodar em paralelo com a versão nova não causa comportamento incorreto, apenas redundância.

## Consequências

- Nenhum Lead deve gerar Person Account a partir desta demanda em diante, incluindo o caso de `TipoPessoa__c` em branco.
- `Account.Name` de clientes PF convertidos sem `Company` original passa a ser o nome da pessoa (ex.: "Ana Silva") — consistente com o modelo de Account único da ADR 0003.
- Pendência de limpeza manual: desativar `Lead_PF_Preenche_Company_Automatico` (obsoleto) via Setup UI quando alguém com acesso à org estiver disponível.
- Pendência de negócio (não decidida por esta ADR): o que fazer, a longo prazo, com Leads sem `TipoPessoa__c` classificado — esta ADR só garante que esse caso não quebra o modelo de Account, não define regra de captação/obrigatoriedade do campo.

## Alternativas descartadas

| Alternativa | Por que foi descartada |
| --- | --- |
| Tornar `Company` obrigatório para todo Lead | Viola a regra de negócio confirmada pelo cliente (PF não tem razão social) |
| Desabilitar Person Accounts na org | Feature irreversível uma vez habilitada — não é uma opção técnica disponível |
| Restringir o Flow a `TipoPessoa__c = 'PF'` | Deixava exposto o caso de `TipoPessoa__c` em branco (achado crítico da revisão `flow-reviewer`) |
| Apex trigger em vez de Flow | Sem ganho sobre a automação declarativa para esta lógica simples; contraria a ordem de preferência declarativa do projeto |
