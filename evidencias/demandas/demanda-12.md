# Demanda atual

> Escreva aqui a descrição da tarefa a ser executada — pode ser um pedaço do backlog do Tarefai, uma pergunta nova do cliente, ou qualquer trabalho de implementação. Depois de escrever, rode `/executar-demanda NN` no Claude Code (NN = número sequencial, ex.: 01, 02...). Ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md).

## O que fazer

Bug reportado pelo tech lead: na conversão de Lead, quando o campo `Company` está em branco, o Salesforce converte automaticamente para **Person Account** em vez de criar uma Account "normal" (Business) com `TipoPessoa__c`.

Isso é comportamento padrão documentado do Salesforce: quando Person Accounts está habilitado na org (confirmado — RecordType `PersonAccount` ativo em Account, ver ADR 0003/0004) e o Lead não tem `Company` preenchido, o botão/API de conversão de Lead cria uma Person Account automaticamente, em vez da Account única com `TipoPessoa__c` (PF|PJ) definida pela arquitetura (ADR 0003). Isso afeta especificamente Leads PF: a Validation Rule `Lead_PF_Campos_Obrigatorios` (demanda-06) não exige `Company` para PF (corretamente — pessoa física não tem razão social) — mas isso deixa o campo em branco até a conversão, disparando o comportamento indesejado.

Resolver via automação declarativa (Flow), sem tornar `Company` obrigatório para PF (isso violaria a regra de negócio) e sem tentar desabilitar Person Accounts (recurso irreversível uma vez habilitado na org).

## Critério de aceite

- Lead PF sem `Company` preenchido, ao ser convertido, deve gerar uma Account **normal** (Business, `IsPersonAccount = false`), com `TipoPessoa__c = 'PF'` mapeado corretamente (mapeamento já existe em `LeadConvertSettings`, demanda-06) — nunca uma Person Account.
- Fluxo declarativo (Flow before-save, sem Apex), preenchendo `Company` automaticamente a partir do nome do Lead quando `TipoPessoa__c = 'PF'` e `Company` estiver em branco — sem tornar o campo obrigatório e sem alterar a Validation Rule existente.
- Validado com teste real de conversão (Lead PF de teste, sem Company, convertido via Apex/API) confirmando `Account.IsPersonAccount = false` — registro de teste removido após validação.
- Sem impacto em Leads PJ (já têm `Company` obrigatório pela Validation Rule `Lead_PJ_Campos_Obrigatorios`).
- Documentar a decisão (novo ADR) e atualizar `business-scenario.md`/`architecture.md` se fizer sentido.
