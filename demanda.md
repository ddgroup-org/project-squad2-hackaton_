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
