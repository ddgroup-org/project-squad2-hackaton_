# Demanda atual

> Escreva aqui a descrição da tarefa a ser executada — pode ser um pedaço do backlog do Tarefai, uma pergunta nova do cliente, ou qualquer trabalho de implementação. Depois de escrever, rode `/executar-demanda NN` no Claude Code (NN = número sequencial, ex.: 01, 02...). Ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md).

## O que fazer

[Tarefa 2 - SETUP] Configuração da Org Salesforce e Cadastro de Usuários/Perfis

**Contexto:** a Cromatta tem 6 vendedores em 3 linhas de produto, 2 químicos no laboratório e o próprio Jacob como aprovador único. O modelo de acesso definido em reunião: Jacob vê e valida tudo; vendedores veem todos os registros mas só editam os próprios.

**Objetivo:** ter a org configurada com todos os usuários, perfis e regras de compartilhamento certas antes de começar a modelar Lead/Oportunidade.

**Descrição Detalhada:**
- Via Claude, configurar o Company Profile como "Cromatta Química".
- Criar perfil/Permission Set Administrador Comercial para Gabriel Jacob (acesso total, aprova preços e valida relatórios).
- Criar perfil/Permission Set Vendedor com Organization-Wide Default de Conta/Oportunidade em Public Read Only, e uma regra de compartilhamento (ou automação) que garanta edição apenas quando o usuário for o Owner do registro.
- Cadastrar os 6 vendedores com o perfil de Vendedor e o campo de Linha de Produto vinculado:
  * Camila — Flexa (couro/calçado)
  * Ronaldo — Cromatta (dispersão/verniz), representante externo
  * Marcelo — Cromatta (dispersão) + brinquedo
  * Diego — Jato + geral
  * Bruno — Jato (ramp-up)
  * Thiago — Jato (ramp-up)
- Criar perfil/fila Laboratório e cadastrar os químicos Sérgio e André (usuários que vão receber os casos de reprovação de amostra).
- Cadastrar Gabriel Jacob com o perfil de Administrador Comercial.

**Validação:** Gabriel Moraes e Paulo Carvalho testam login de um usuário Vendedor e confirmam que ele vê todos os registros mas só consegue editar os que possui como Owner.

## Critério de aceite

- 9 usuários cadastrados (6 vendedores + 2 químicos + Jacob) com perfis corretos.
- Teste de acesso de Vendedor validado: lê tudo, edita só o próprio.
- Pendência: usar perfil de vendedor padrão para Ronaldo como premissa até resposta.

---

## Execução — registro (via Claude/CLI + MCP, org `hackaton2`)

**Status: concluída**, com os desvios/premissas abaixo registrados por transparência (regra central 3 do `CLAUDE.md` — não presumir requisito não confirmado sem registrar):

1. **Company Info:** `Organization.Name` atualizado para "Cromatta Química" via `sf data update record` (não há metadata deployável para esse campo — é dado, não configuração).
2. **Linhas de produto — grafia corrigida:** este texto usa "Flexa" e "Cromatta" para as linhas de Camila/Ronaldo/Marcelo, mas `business-scenario.md` (fonte confirmada com o cliente) usa **"Flecha"** e **"Cromata"** (a empresa é "Cromatta", a linha de produto é "Cromata" — sem o segundo "t"). Assumi que são erros de digitação neste arquivo e usei a grafia de `business-scenario.md` no campo `User.Linha_de_Produto__c` (picklist Cromata/Flecha/Jato). Detalhes extras não confirmados na fonte (Marcelo "+ brinquedo", Diego "+ geral", Bruno/Thiago "ramp-up", Ronaldo representante externo) foram tratados como anotação de contexto, não como valor de campo — não inventei novos valores de picklist sem confirmação.
3. **Sobrenomes:** não fornecidos em nenhum documento-fonte para os 9 usuários — cadastrados apenas com o primeiro nome (`LastName` = primeiro nome, `FirstName` vazio, exceto Gabriel Jacob que já tem "Jacob" como sobrenome conhecido).
4. **Modelo de segurança implementado** (via metadata declarativa, `sf project deploy start`):
   - OWD `Public Read Only` (sharingModel `Read`) em Account, Opportunity e Case.
   - Campo customizado `User.Linha_de_Produto__c` (picklist Cromata/Flecha/Jato).
   - 3 Permission Sets: `Administrador_Comercial` (CRUD + View/Modify All em Lead/Account/Contact/Opportunity/Case/Product2/PricebookEntry), `Vendedor` (CRUD sem View/Modify All — combinado ao OWD Public Read Only, isso entrega "lê tudo, edita só o próprio" sem precisar de sharing rule extra, conforme já previsto em `architecture.md`), `Laboratorio` (CRUD em Case, leitura em Account/Contact/Opportunity).
   - Queue `Laboratório` (objeto Case) com Sérgio e André como membros.
   - Todos os 9 usuários criados (perfil base "Standard User" + Permission Set correspondente) e Permission Set atribuído via `PermissionSetAssignment`.
   - Exceção técnica registrada: o custom field `User.Linha_de_Produto__c` precisou de FLS explícita no profile "System Administrator" (`profiles/Admin.profile-meta.xml`) para o próprio usuário de automação conseguir popular o campo via API — Salesforce não concede FLS automática a um field novo, mesmo para o admin.
5. **Validação:** confirmado via SOQL/Tooling API (não só pela CLI, regra central 4) — `Organization.Name`, `EntityDefinition.InternalSharingModel` (Account/Opportunity/Case = `Read`), `User` + `PermissionSetAssignments` + `Linha_de_Produto__c` para os 9 usuários, `Group`/`GroupMember` da fila Laboratório. Ver `evidencias/log.md` para o resumo.
6. **Pendente do critério de aceite:** o teste de login real como um Vendedor (Gabriel Moraes/Paulo Carvalho confirmando "lê tudo, edita só o próprio" na UI) não foi feito por mim — é um teste manual do time, não uma etapa de configuração via Claude. A configuração que sustenta esse comportamento (OWD Public Read Only + Permission Set Vendedor sem View/Modify All) está implementada e validada via API.
