---
title: "Padrões de segurança Salesforce"
description: "Modelo de segurança da plataforma: menor privilégio, CRUD, FLS, sharing, contexto de execução, credenciais, dados sensíveis e checklist de revisão."
category: "knowledge"
status: "active"
version: "1.1"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - security
  - permissions
  - sharing
  - secrets
applies_to:
  - global
source_of_truth: true
source_references:
  - arquitetura.md
  - desenvolvimento.md
  - metaprompt-salesforce.md
---

# Padrões de segurança Salesforce

## Objetivo

Definir como tratar segurança, permissionamento e proteção de dados em qualquer implementação Salesforce.

Este documento é a **fonte da verdade** para segurança. Os documentos de Apex, LWC, Flow e integrações resumem e apontam para cá.

## Escopo

Modelo de permissões, contexto de execução, acesso a dados, proteção de segredos, exposição pública e revisão de segurança. Não cobre segurança da infraestrutura do cliente nem políticas corporativas de identidade, que pertencem ao projeto.

## Princípio geral

Segurança é decisão de projeto, tomada no início e justificada — não item de checklist no fim. Nenhuma técnica desta página é obrigatória em todos os cenários; cada uma tem contexto de uso e trade-offs. O que **é** obrigatório: decidir conscientemente e registrar o motivo.

---

## 1. Menor privilégio

Conceder o mínimo necessário para a função ser executada, pelo menor tempo necessário, ao menor conjunto de pessoas.

### 1.1 Permission Sets antes de Profile

Preferir Permission Sets e Permission Set Groups à ampliação de Profiles. Profile é atribuído a muitos usuários e cresce sem controle; Permission Set é granular, reversível e rastreável.

Ao propor acesso, informar sempre: **o que** é concedido, **para quem**, **por quê** e **como revogar**.

### 1.2 Custom Permissions

Custom Permissions permitem controlar funcionalidade sem depender de checagem por Profile, e são verificáveis em Apex, Flow, fórmulas e Validation Rules. Preferir Custom Permission a comparação por nome de Profile ou por Id de usuário — comparação por Profile quebra na primeira reorganização de perfis.

### 1.3 Alteração de permissões existentes

Modificar Profile ou Permission Set com usuários atribuídos exige autorização (ver matriz em [operational-safety-policy.md](./operational-safety-policy.md#3-matriz-de-aprovação-humana)). Antes de alterar, levantar: acesso atual, acesso necessário, usuários afetados e risco de privilégio excessivo.

Reduzir controle de segurança para contornar erro de implementação **não é uma opção**.

---

## 2. Camadas de acesso a dados

A plataforma controla acesso em camadas independentes. Conceder uma não substitui as outras.

| Camada | Controla | Onde se configura |
| --- | --- | --- |
| Objeto (CRUD) | criar, ler, editar, excluir por objeto | Profile, Permission Set |
| Campo (FLS) | leitura e escrita por campo | Profile, Permission Set |
| Registro (sharing) | quais registros o usuário enxerga | OWD, role hierarchy, sharing rules, sharing manual, Apex sharing |
| Funcionalidade | acesso a classes, Flows, apps, componentes | Profile, Permission Set, Custom Permission |

### 2.1 CRUD e FLS

Verificar CRUD e FLS sempre que houver exposição de dados a usuários. As abordagens principais:

- **User Mode** em operações de banco — a forma mais direta de garantir que a operação respeite as permissões do usuário;
- **`Security.stripInaccessible`** — remove campos inacessíveis de registros antes de retornar ou gravar, útil quando o resultado é devolvido a um componente;
- **checagem explícita** via `Schema.DescribeSObjectResult` / `DescribeFieldResult` — mais verboso, útil para decisões de fluxo antes da operação.

Nem toda operação precisa de checagem: processos de sistema que executam por definição fora do contexto do usuário (jobs de integração, cálculos internos) podem exigir System Mode. A regra é justificar a escolha, não aplicar uma fórmula única.

### 2.2 Sharing em Apex

```apex
public with sharing class ExemploService { }      // aplica regras de compartilhamento do usuário
public inherited sharing class ExemploHelper { }  // herda o contexto de quem chama
public without sharing class ExemploSystem { }    // ignora sharing — exige justificativa
```

Diretrizes:

- classes chamadas a partir de LWC, Aura, Visualforce ou Flow acionado por usuário tendem a `with sharing`;
- classes utilitárias e de serviço reutilizáveis tendem a `inherited sharing` — declarar explicitamente evita depender do padrão da linguagem;
- `without sharing` é exceção: usar apenas quando o processo precisa legitimamente enxergar registros além do alcance do usuário, com o motivo registrado em comentário e na documentação da demanda;
- omitir o modificador delega o comportamento ao contexto de invocação, o que dificulta a revisão. Declarar sempre.

Atenção: `with sharing` afeta visibilidade de **registros**; não aplica CRUD nem FLS automaticamente.

### 2.3 User Mode e System Mode

A plataforma permite executar operações de banco em modo usuário, aplicando CRUD, FLS e sharing de forma integrada, ou em modo sistema. A escolha deve ser consciente e registrada.

Perguntas que orientam a decisão:

- os dados serão devolvidos a um usuário final?
- o processo precisa acessar registros fora do alcance do usuário para funcionar corretamente?
- há requisito de auditoria que exige rastrear o acesso sob a identidade do usuário?

> Validar a sintaxe e a disponibilidade dos modos de execução na documentação oficial correspondente à API Version do projeto.

---

## 3. Consultas e entradas

### 3.1 SOQL injection

Nunca concatenar entrada não confiável em SOQL dinâmica. Preferir consultas estáticas com bind de variável. Quando a consulta dinâmica for inevitável, usar mecanismo de escape oficial para literais e validar rigidamente nomes de campo e de objeto contra uma lista conhecida — nome de campo não pode ser escapado, precisa ser validado.

### 3.2 Validação de entradas

Validar no servidor, sempre. Validação de front-end é conveniência para o usuário, não controle de segurança: qualquer chamada pode ser feita diretamente ao método Apex.

Validar: tipo, formato, faixa de valores, tamanho, obrigatoriedade, pertinência do registro ao contexto do usuário e coerência com o estado atual do dado.

### 3.3 XSS e conteúdo dinâmico

Não renderizar HTML construído a partir de entrada de usuário. Em LWC, o binding padrão do template já escapa conteúdo — a exposição aparece quando se recorre a APIs que injetam HTML diretamente. Se houver necessidade real, sanitizar com biblioteca reconhecida e restringir drasticamente o que é permitido.

Ver [lwc-standards.md](./lwc-standards.md).

### 3.4 Lightning Web Security

O modelo de segurança do lado do cliente isola componentes e restringe acesso ao DOM global e a objetos compartilhados. Bibliotecas de terceiros podem se comportar de forma diferente sob esse isolamento.

> Confirmar na documentação oficial o comportamento vigente e as diferenças em relação ao modelo anterior para a release do projeto.

---

## 4. Acesso a código e automações

- classes Apex expostas a usuários exigem acesso concedido por Permission Set — método `@AuraEnabled` sem acesso à classe falha para o usuário, ainda que o código esteja correto;
- Flows acionados por usuário exigem acesso ao Flow;
- `@AuraEnabled(cacheable=true)` deve ser usado apenas para operações de leitura, sem efeito colateral;
- métodos expostos representam superfície de ataque: expor o mínimo, com assinatura restrita e validação de entrada.

---

## 5. Credenciais e segredos

### 5.1 Named Credentials e External Credentials

Toda integração deve usar Named Credential com External Credential para autenticação. Isso mantém segredos fora do código e do repositório, e permite rotação sem redeploy.

**Nunca** armazenar em código, metadata versionada, Custom Metadata, Custom Setting, Custom Label ou documentação:

- senhas, tokens de acesso, refresh tokens;
- client secrets;
- chaves privadas e certificados privados;
- cookies, session IDs, cabeçalhos de autorização com valor real.

### 5.2 Detecção antes de versionar

Antes de commit, push, geração de documentação ou entrega de evidência, verificar a presença de segredos. Termos genéricos em texto conceitual não são vazamento; o que importa é a existência de **valor real** associado.

Padrões que merecem verificação:

```text
token
password
secret
client_secret
private_key
BEGIN PRIVATE KEY
Authorization: Bearer
```

Encontrando segredo real: interromper antes de qualquer push, remover o valor, avaliar se houve exposição anterior e tratar a credencial como comprometida — rotacionar, não apenas apagar.

### 5.3 Mascaramento

Dados sensíveis em logs, documentação, exemplos, testes e Pull Requests devem ser mascarados:

```text
client_secret=***
Authorization: Bearer ***
CPF=***.***.***-**
```

---

## 6. Logs e dados sensíveis

Logs precisam ser suficientes para investigar e insuficientes para vazar.

Registrar: identificador do registro, usuário, operação, momento, status, correlation ID, mensagem de erro técnica.

Não registrar: payload completo com dados pessoais, credenciais, conteúdo de documentos, dados clínicos, dados financeiros e informações confidenciais do cliente.

Mensagens de erro exibidas ao usuário não devem expor detalhes internos: nomes de classes, stack traces, nomes de campos internos ou trechos de query. A mensagem técnica vai para o log; a mensagem amigável vai para a tela.

---

## 7. Guest User e Experience Cloud

Acesso público é a superfície de maior risco da plataforma. Quando houver Experience Cloud ou Site com Guest User:

- revisar o que o perfil Guest enxerga por objeto, campo e registro;
- confirmar que o compartilhamento com Guest User está restrito ao mínimo;
- revisar classes Apex expostas ao contexto público e o sharing declarado nelas;
- não confiar em parâmetro de URL para determinar autorização;
- validar no servidor a pertinência de cada registro solicitado;
- revisar arquivos e conteúdo público: um arquivo acessível por link é acessível por qualquer pessoa com o link;
- revisar o que é retornado por métodos `@AuraEnabled` acessíveis publicamente.

Alteração de acesso Guest tem impacto imediato e amplo. Tratar como mudança de alto risco, com validação em ambiente controlado antes de qualquer promoção.

---

## 8. Arquivos e URLs

- validar tipo e tamanho de arquivos recebidos;
- não confiar na extensão informada pelo cliente;
- avaliar quem tem acesso ao registro ao qual o arquivo está vinculado;
- não construir URLs de redirecionamento a partir de entrada não validada;
- não embutir identificadores sensíveis em URLs registradas em logs de terceiros.

---

## 9. Segurança em integrações

Resumo — o detalhamento está em [integration-standards.md](./integration-standards.md):

- autenticação por Named Credential e External Credential, nunca por credencial embutida;
- princípio do menor privilégio também para o usuário de integração;
- validação do payload recebido antes de qualquer operação de dados;
- proteção contra reprocessamento indevido por meio de idempotência;
- logs sanitizados com correlation ID;
- tratamento explícito de indisponibilidade do sistema externo.

---

## 10. Auditoria e licenciamento

**Auditoria.** Para investigar alterações e comportamento, considerar: Setup Audit Trail, Field History Tracking, Login History, Debug Logs e histórico de deploy. Definir na demanda quais desses registros serão a evidência.

**Licenciamento.** Recursos que dependem de licença, feature license, permission set license ou pacote gerenciado precisam ser confirmados na org de destino antes de serem propostos. Consultas úteis, quando houver acesso autorizado de leitura:

```sql
SELECT Name, TotalLicenses, UsedLicenses, Status FROM UserLicense
SELECT DeveloperName, TotalLicenses, UsedLicenses FROM PermissionSetLicense
SELECT AssigneeId, PermissionSetLicenseId FROM PermissionSetLicenseAssign
```

Não confirmando: registrar como pendência e apresentar alternativa compatível com o licenciamento atual.

> Licenciamento/feature não confirmado na org. Necessário validar antes de prosseguir com esta solução.

---

## 11. Checklist de revisão de segurança

**Permissões**
- [ ] Acesso concedido por Permission Set, com escopo mínimo e justificativa.
- [ ] Impacto em usuários existentes avaliado.
- [ ] Custom Permission usada no lugar de checagem por Profile.

**Dados**
- [ ] CRUD avaliado e decisão registrada.
- [ ] FLS avaliado e decisão registrada.
- [ ] Sharing declarado explicitamente nas classes Apex.
- [ ] Modo de execução (usuário ou sistema) escolhido conscientemente.
- [ ] Comportamento verificado para usuário com e sem permissão.

**Código**
- [ ] Sem SOQL dinâmica com entrada não confiável.
- [ ] Entradas validadas no servidor.
- [ ] Sem renderização de HTML a partir de entrada de usuário.
- [ ] Métodos expostos limitados ao necessário.
- [ ] `cacheable=true` apenas em leitura.

**Segredos**
- [ ] Nenhuma credencial no código, na metadata ou na documentação.
- [ ] Integrações usando Named Credential e External Credential.
- [ ] Logs sanitizados.
- [ ] Diff verificado quanto a segredos antes do commit.

**Exposição**
- [ ] Acesso Guest revisado, quando houver Experience Cloud ou Site.
- [ ] Arquivos e URLs públicos revisados.
- [ ] Mensagens de erro sem detalhes internos.

**Governança**
- [ ] Licenciamento confirmado quando aplicável.
- [ ] Evidência de auditoria definida.
- [ ] Riscos residuais declarados.

---

## 12. Riscos frequentes

| Risco | Consequência | Mitigação |
| --- | --- | --- |
| `without sharing` sem justificativa | exposição de registros fora do alcance do usuário | rever necessidade; usar `with` ou `inherited sharing` |
| Ausência de FLS em dados devolvidos a componente | exposição de campos restritos | User Mode ou `stripInaccessible` |
| SOQL dinâmica com entrada de usuário | injeção e vazamento | bind de variável; validação de identificadores |
| Credencial em Custom Setting ou código | vazamento no repositório e em logs | Named Credential e External Credential |
| Guest User com sharing amplo | exposição pública de dados | revisão de OWD e sharing para o perfil Guest |
| Validação apenas no front-end | contorno direto via chamada ao método | validar no servidor |
| Profile ampliado para resolver erro | privilégio excessivo permanente | Permission Set específico e temporário |

---

## Referências cruzadas

- [salesforce-development-principles.md](./salesforce-development-principles.md) — matriz de aprovação e bloqueio de Produção.
- [apex-standards.md](./apex-standards.md) · [lwc-standards.md](./lwc-standards.md) · [flow-standards.md](./flow-standards.md) · [integration-standards.md](./integration-standards.md) · [testing-standards.md](./testing-standards.md)

## Fontes oficiais recomendadas

Salesforce Security Guide; Secure Coding Guide; Apex Developer Guide (capítulos de segurança e sharing); Lightning Web Components Developer Guide (Lightning Web Security); Salesforce Help para modelo de compartilhamento e Experience Cloud; Salesforce Code Analyzer Documentation.

## Limitações

Sintaxe, disponibilidade e comportamento de recursos de segurança variam por release e por API Version. Toda afirmação técnica desta página deve ser confirmada na documentação oficial correspondente à release do projeto antes de ser aplicada como regra absoluta.

## Critérios de revisão

Revisar a cada release da Salesforce com mudança em segurança, ao adotar Experience Cloud ou acesso público, e sempre que houver incidente de segurança relacionado à plataforma.
