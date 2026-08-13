---
title: "Padrões de integração"
description: "Autenticação, resiliência, idempotência, observabilidade e testes em integrações Salesforce com sistemas externos."
category: "knowledge"
status: "active"
version: "1.0"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - integration
  - api
  - platform-events
  - resilience
applies_to:
  - global
source_of_truth: true
source_references:
  - desenvolvimento.md
  - metaprompt-salesforce.md
  - arquitetura.md
---

# Padrões de integração

## Objetivo

Definir como projetar, implementar e operar integrações entre Salesforce e sistemas externos com segurança, resiliência e rastreabilidade.

Este documento é a **fonte da verdade** para integrações. Segurança geral em [security-standards.md](./security-standards.md); implementação Apex em [apex-standards.md](./apex-standards.md).

## Escopo

Integrações de saída (callouts), de entrada (APIs da plataforma), orientadas a evento e por captura de mudança de dados. Não cobre ferramentas específicas de middleware, que pertencem à arquitetura do projeto.

## Princípio

Antes de propor mecanismo externo — middleware, serviço intermediário, ferramenta de terceiros — justificar por que os recursos da própria plataforma não atendem. Cada componente adicional acrescenta ponto de falha, custo e superfície de segurança.

---

## 1. Escolha do mecanismo

| Mecanismo | Adequado para | Considerações |
| --- | --- | --- |
| **REST callout** (saída) | consulta e comando síncrono para sistema externo | limite de callouts por transação; timeout; não permitido após DML na mesma transação sem contexto assíncrono |
| **SOAP callout** (saída) | sistemas legados com contrato WSDL | contrato rígido; versionamento mais custoso |
| **REST/SOAP API** (entrada) | sistema externo consulta ou grava no Salesforce | autenticação e menor privilégio do usuário de integração |
| **Apex REST customizado** (entrada) | contrato próprio, regra na entrada | superfície exposta; validar tudo |
| **Platform Events** | desacoplamento, publicação para múltiplos consumidores | semântica de entrega e reprocessamento próprias |
| **Change Data Capture** | replicar alterações de registros para fora | volume alto; consumidor precisa tratar ordem e reprocessamento |
| **Outbound Message** | notificação declarativa simples | mecanismo legado; avaliar Platform Events antes |
| **Bulk API** (entrada) | cargas volumosas | assíncrono; tratamento de erro por lote |

Integração síncrona acopla o desempenho do Salesforce ao do sistema externo. Se a indisponibilidade externa não pode bloquear o usuário, o processo deve ser assíncrono.

---

## 2. Autenticação e autorização

### 2.1 Named Credentials e External Credentials

Toda integração de saída deve usar **Named Credential** com **External Credential**. Benefícios: segredos fora do código e do repositório, rotação sem redeploy, configuração por ambiente e gestão de acesso por Permission Set.

Nunca embutir endpoint, token, senha, client secret ou chave privada em código, metadata versionada, Custom Metadata, Custom Setting, Custom Label ou documentação.

### 2.2 OAuth

Escolher o fluxo adequado ao cenário: credenciais de cliente para comunicação entre sistemas sem usuário final; fluxo com usuário quando a operação precisa ocorrer sob a identidade de uma pessoa; asserção assinada quando o parceiro exigir.

Tratar explicitamente: expiração do token, renovação, falha de renovação e revogação. Falha de autenticação deve ser distinguida de falha de negócio no tratamento de erro e no log.

> Confirmar os fluxos suportados e sua configuração na documentação oficial correspondente à release do projeto.

### 2.3 Integrações de entrada

- usuário de integração dedicado, com Permission Set específico e menor privilégio;
- não reutilizar credencial de pessoa física;
- restringir acesso por IP quando a política do projeto permitir;
- validar integralmente o payload recebido antes de qualquer operação de dados;
- não confiar em identificadores enviados sem verificar pertinência e autorização.

---

## 3. Resiliência

### 3.1 Timeout

Definir timeout explícito em todo callout. Sem definição, o valor padrão pode consumir a transação inteira e provocar falha em cascata. O valor deve ser compatível com o tempo de resposta real do parceiro e com o limite de tempo da transação.

### 3.2 Retry e backoff

Retry só é seguro sobre operação **idempotente**.

- retentar apenas falhas transitórias: timeout, indisponibilidade temporária, erro de servidor;
- **não** retentar erro de validação, autenticação ou requisição malformada — a repetição produzirá o mesmo resultado;
- aplicar espera crescente entre tentativas;
- limitar o número de tentativas;
- registrar cada tentativa com o mesmo correlation ID.

### 3.3 Idempotência

Sem idempotência, um retry pode duplicar registros, cobranças ou notificações.

Estratégias: chave de idempotência enviada e reconhecida pelo parceiro; identificador único do evento registrado do lado que consome; verificação de estado antes da ação; campo de External Id com upsert em vez de insert.

### 3.4 Correlation ID

Cada operação recebe um identificador propagado em requisição, resposta, logs e registros relacionados. É o que permite reconstruir o caminho de uma transação entre sistemas quando algo falha.

### 3.5 Contingência

Definir o comportamento quando o sistema externo estiver indisponível:

- a operação é enfileirada para reprocessamento posterior?
- o usuário é informado e a ação é bloqueada?
- existe caminho degradado aceitável?
- há limite de tempo após o qual o item deve ser tratado manualmente?

Quando o volume e a criticidade justificarem, manter uma fila de itens não processados com estratégia explícita de reprocessamento e de descarte controlado — o equivalente funcional a uma dead letter queue. Itens que falham repetidamente precisam de destino definido; acumular indefinidamente é ausência de decisão.

---

## 4. Contrato e payload

- documentar o contrato: endpoint, método, cabeçalhos, estrutura de requisição e resposta, códigos de status esperados e significado de cada erro;
- enviar apenas os campos necessários — payload amplo aumenta exposição e acoplamento;
- validar a estrutura recebida antes de usar: campo ausente, tipo divergente e valor nulo são cenários reais;
- tratar mudanças de contrato como mudança de dependência externa, com versionamento e janela de compatibilidade;
- versionar a API exposta quando o Salesforce for o provedor, para não quebrar consumidores em produção.

---

## 5. Tratamento de erros

Distinguir claramente:

| Categoria | Exemplo | Tratamento |
| --- | --- | --- |
| Erro de negócio | dado inválido, regra não atendida | reportar ao usuário, não retentar |
| Erro de autenticação | token expirado ou revogado | renovar quando aplicável; alertar |
| Erro transitório | timeout, indisponibilidade momentânea | retry com backoff |
| Erro de contrato | estrutura inesperada | interromper, registrar, alertar; não tentar interpretar |
| Erro interno | falha na lógica local | corrigir; não mascarar com retry |

Tratar **status HTTP**, não apenas exceção: uma resposta com código de erro não gera exceção automaticamente e pode ser interpretada como sucesso se o código não for verificado.

---

## 6. Observabilidade

Registrar, para cada operação: momento, endpoint, método, status HTTP, correlation ID, identificador do registro relacionado, tempo de resposta, número da tentativa, resultado e mensagem de erro quando houver.

Payloads devem ser resumidos ou sanitizados. **Não registrar** dados pessoais, credenciais, cabeçalhos de autorização, conteúdo de documentos, dados financeiros ou clínicos.

```text
Authorization: Bearer ***
client_secret=***
```

Monitorar: taxa de erro, latência, volume por período, itens pendentes de reprocessamento e falhas recorrentes por parceiro. Integração sem monitoramento só é descoberta quando o problema chega ao usuário.

---

## 7. Limites

- callouts têm limite por transação e tempo total acumulado;
- callout não é permitido após DML na mesma transação sem contexto assíncrono;
- Platform Events e CDC têm limites próprios de publicação e entrega;
- APIs da plataforma têm limite de requisições por período, compartilhado pela org — uma integração mal dimensionada pode esgotar a cota de todas as outras;
- rate limits do parceiro precisam ser respeitados, com controle de concorrência do lado do Salesforce.

> Confirmar todos os limites vigentes na documentação oficial correspondente à release e à edição da org.

Dimensionar antes de implementar: volume esperado, pico, concorrência e crescimento projetado.

---

## 8. Processamento assíncrono

Usar quando: a operação não precisa de resposta imediata; o volume excede o limite síncrono; a indisponibilidade externa não deve bloquear o usuário; há necessidade de retry.

Mecanismos: Queueable para trabalho pontual; Batch Apex para grandes volumes; Platform Events para desacoplamento; Scheduled Apex para janelas periódicas. Ver [apex-standards.md](./apex-standards.md#6-processamento-assíncrono).

Todo processo assíncrono precisa de tratamento de falha e visibilidade — sem isso, a falha é silenciosa.

---

## 9. Testes

Callouts exigem mock: testes não realizam chamadas externas reais.

Cenários mínimos:

- resposta de sucesso;
- erro de negócio retornado pelo parceiro;
- erro de servidor;
- timeout;
- resposta com estrutura inesperada;
- falha de autenticação;
- reprocessamento (comprovando idempotência);
- volume, quando aplicável.

Além dos testes automatizados, validar o contrato real contra o ambiente de homologação do parceiro antes da promoção. Teste com mock comprova o código; não comprova o contrato.

Ver [testing-standards.md](./testing-standards.md).

---

## 10. Checklist de produção

**Segurança**
- [ ] Named Credential e External Credential configurados.
- [ ] Nenhum segredo em código, metadata ou documentação.
- [ ] Usuário de integração com menor privilégio.
- [ ] Payload de entrada validado.

**Resiliência**
- [ ] Timeout explícito.
- [ ] Política de retry definida e restrita a falhas transitórias.
- [ ] Idempotência garantida.
- [ ] Comportamento em indisponibilidade definido.
- [ ] Destino de itens com falha recorrente definido.

**Observabilidade**
- [ ] Correlation ID propagado.
- [ ] Logs sanitizados e suficientes.
- [ ] Monitoramento de erro, latência e volume definido.
- [ ] Responsável por acompanhar alertas identificado.

**Limites**
- [ ] Volume e pico dimensionados.
- [ ] Limites de callout e de API avaliados.
- [ ] Rate limits do parceiro respeitados.

**Contrato**
- [ ] Contrato documentado.
- [ ] Estratégia de versionamento definida.
- [ ] Validado contra ambiente de homologação do parceiro.

**Operação**
- [ ] Configuração por ambiente confirmada (DEV, UAT, Produção).
- [ ] Plano de rollback definido, incluindo efeitos não reversíveis.
- [ ] Testes com mock cobrindo sucesso, erro e timeout.

---

## 11. Antipadrões

| Antipadrão | Problema |
| --- | --- |
| Endpoint ou credencial no código | vazamento e quebra entre ambientes |
| Callout síncrono em trigger | falha e acoplamento de desempenho |
| Retry sem idempotência | duplicação de dados |
| Retry em erro de validação | repetição inútil e mascaramento do defeito |
| Sem timeout explícito | transação travada |
| Log com payload completo | vazamento de dados sensíveis |
| Verificar só exceção, ignorando status HTTP | erro tratado como sucesso |
| Sem correlation ID | impossível rastrear entre sistemas |
| Sem monitoramento | falha descoberta pelo usuário |
| Middleware sem justificativa | complexidade e ponto de falha adicionais |

---

## Referências cruzadas

- [security-standards.md](./security-standards.md) · [apex-standards.md](./apex-standards.md) · [testing-standards.md](./testing-standards.md) · [naming-conventions.md](./naming-conventions.md#7-configuração-e-integração)

## Fontes oficiais recomendadas

Salesforce Developer Documentation para integração e APIs; Apex Developer Guide (callouts); documentação oficial de Named Credentials e External Credentials; Platform Events Developer Guide; Change Data Capture Developer Guide; Salesforce Architecture Center e Well-Architected para padrões de integração; Salesforce Help para limites de API.

## Limitações

Limites de callout, de eventos e de requisições variam por edição, licenciamento e release. Recursos de autenticação evoluem entre versões. Confirmar na documentação oficial correspondente antes de tratar qualquer valor desta página como definitivo.

## Critérios de revisão

Revisar a cada release com mudança em integração ou autenticação, ao adicionar novo parceiro externo e quando o volume transacionado mudar de ordem de grandeza.
