# Demanda atual

> Escreva aqui a descrição da tarefa a ser executada — pode ser um pedaço do backlog do Tarefai, uma pergunta nova do cliente, ou qualquer trabalho de implementação. Depois de escrever, rode `/executar-demanda NN` no Claude Code (NN = número sequencial, ex.: 01, 02...). Ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md).

## O que fazer

[Cromatta Química] - [Tarefa 9 - Service] Estruturação de Casos para Envio e Teste de Amostras

**Contexto:** O processo de envio e teste de amostras é o coração da venda de produtos novos e necessita de registro formal para rastreamento técnico entre vendedor e químico.

**Objetivo:** Criar a estrutura do objeto Amostra vinculado à Oportunidade, tipo de registro de Caso para envio/teste de amostra, campos de causa técnica e automação de cobrança a cada 10 dias sem retorno.

**Descrição Detalhada:**
- Criar o Objeto Customizado `Amostra__c` com os campos:
  * Oportunidade__c (Master-Detail ou Lookup para Opportunity)
  * ProdutoAmostrado__c (Lookup para Product2 ou Text)
  * PesoVolumeEnviado__c (Text / Number)
  * DataEnvio__c (Date)
  * NumeroTentativa__c (Auto-number ou Number)
  * Resultado__c (Picklist: Aprovado, Reprovado, Em Teste)
  * CustoEstimado__c (Currency)
- Criar Record Type no objeto Case: "Envio e Teste de Amostra".
- Criar campos customizados no objeto Case:
  * CausaTecnicaReprovacao__c (Picklist: Incompatibilidade com Substrato, Incompatibilidade com Base do Cliente, Instabilidade do Produto, Entupimento de Cabeçote, Aspecto/Aparência Fora do Esperado)
  * MarcacaoVisitaTecnica__c (Checkbox e/ou Date) -> Para controle de visita presencial do químico
  * Amostra__c (Lookup para o objeto Amostra__c)
- Criar um Flow (Record-Triggered Flow / Scheduled Flow) ou Tarefa/Alerta automático para acompanhamento/cobrança de retorno do teste do cliente após envio (alerta de 10 dias).
- Adicionar os campos e listas relacionadas (Related Lists) aos Page Layouts dos objetos envolvidos (Opportunity, Amostra__c e Case) e garantir visibilidade (FLS).

## Critério de aceite

- Objeto Amostra funcionando e vinculado à Oportunidade (com histórico visível).
- Tipo de registro de Caso para Amostra funcionando com campo de causa técnica.
- Teste Apex criando uma Oportunidade com 2 amostras reprovadas para validar o histórico e a criação de Casos de suporte.

---

## Execução — registro (via Claude/CLI + Flow + Apex, org `hackaton2`)

**Status: concluída.**

1. **`Amostra__c` como Lookup, não Master-Detail:** a demanda oferecia as duas opções, mas `architecture.md`/BRD 3.5.2 já haviam decidido isso — Lookup em Opportunity e em Product2, para permitir OWD próprio em `Amostra__c` (implementado: `sharingModel=Read`, Public Read Only). Segui a decisão já registrada em vez de escolher livremente entre as opções oferecidas.
2. **7 campos criados:** `Oportunidade__c` (Lookup, required, deleteConstraint=Restrict), `ProdutoAmostrado__c` (Lookup para Product2, reaproveitando o catálogo da demanda-07), `PesoVolumeEnviado__c` (Text — unidades variam por linha), `DataEnvio__c`, `NumeroTentativa__c`, `Resultado__c` (Picklist, default "Em Teste"), `CustoEstimado__c`.
3. **`NumeroTentativa__c` implementado como Number, não AutoNumber:** o AutoNumber declarativo do Salesforce incrementa globalmente no objeto, não por Oportunidade — não atenderia "1ª, 2ª tentativa desta oportunidade" sem lógica adicional (Flow/Apex), fora do escopo explícito desta demanda. A demanda oferecia essa alternativa ("Auto-number ou Number"); optei pela que reflete corretamente a regra de negócio.
4. **Record Type "Envio e Teste de Amostra" em Case** + Business Process (`Envio_e_Teste_de_Amostra`, baseado no campo Status: New/On Hold/Escalated/Closed) — descoberto por erro de deploy que Case também exige `businessProcess` no Record Type, assim como Opportunity (lição da demanda-08).
5. **4 campos em Case:** `CausaTecnicaReprovacao__c`, `Amostra__c` (Lookup), e para "Checkbox e/ou Date" — implementei **os dois**: `MarcacaoVisitaTecnica__c` (Checkbox) + `DataVisitaTecnica__c` (Date), para cobrir completamente o que a demanda descreveu, já que ela ofereceu ambos os formatos como válidos.
6. **2 Flows (declarativos, sem Apex/trigger):**
   - `Amostra_Reprovada_Cria_Case`: Record-Triggered Flow em `Amostra__c`, dispara quando `Resultado__c = "Reprovado"` (create ou update), cria Case (RecordType "Envio e Teste de Amostra") atribuído à Queue Laboratório, com `Amostra__c`/`AccountId` preenchidos. IDs de RecordType e Queue resolvidos via "Get Records" dentro do Flow (por DeveloperName), não hardcoded — portável entre orgs.
   - `Amostra_Cobranca_Retorno`: Record-Triggered Flow com **Scheduled Path** (10 dias após `DataEnvio__c`, reagenda automaticamente se a data mudar) que cria uma Task de cobrança — só se `Resultado__c` ainda for "Em Teste" no momento em que o path executa (revalidado via Decision, não no momento da criação). Preferi Scheduled Path a um Scheduled Flow separado porque é o mecanismo desenhado pela própria plataforma para "X dias após um campo de data", sem precisar de um campo de controle de duplicidade.
7. **FLS + Page Layouts + Related Lists:** campos novos com FLS nos profiles Admin/Standard e nos 3 Permission Sets (Administrador_Comercial: CRUD completo em `Amostra__c`; Vendedor: CRUD sem viewAll/modifyAll, mesmo padrão "lê tudo, edita só o próprio"; Laboratório: leitura em quase tudo, edição em `Resultado__c`/campos de Case — são eles que atualizam o resultado do teste). Layout único de Amostra__c com todos os campos + related list de Cases; layout de Case com nova seção "Envio e Teste de Amostra"; layout de Opportunity com related list de Amostras. `layoutAssignments` e `recordTypeVisibilities` (com `default=true` na nova Record Type de Case, já que Case não tinha nenhuma antes — lição repetida da demanda-08 sobre exigir um default explícito).
8. **Teste via Apex (`sf apex run`, script não commitado):** 1 Account + 1 Opportunity (Caminho B - Produto Novo) + 2 Amostras Reprovadas (tentativas 1 e 2). Confirmado via SOQL: histórico de amostras da Oportunidade completo e ordenado; **2 Cases criados automaticamente pelo Flow**, RecordType correto, `Owner = Laboratório` (Queue), `Amostra__c` apontando para a amostra de origem. Registros de teste removidos após validação.
9. **Fila do laboratório de cobrança de retorno não testada via Apex** (não é possível simular a passagem de 10 dias em um teste síncrono) — validado apenas por leitura do Flow e da lógica; recomendo teste manual/observação ao vivo passado o prazo, ou um teste futuro com `Test.setCreatedDate`/ajuste de data em ambiente de teste dedicado, fora do escopo desta execução.
