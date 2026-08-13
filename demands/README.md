---
title: "Prompts do hackathon — quimicahackaton"
category: "demands"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Paulo Carvalho"
applies_to:
  - quimicahackaton
---

# Prompts do hackathon

Cada arquivo abaixo é um **prompt autocontido**, pronto para ser copiado inteiro e colado numa sessão do Claude Code operada pelo dev executor — que **não** tem acesso a este cofre. Copiar o arquivo inteiro, do título ao fim; não resumir, não linkar.

## Ordem de execução

| # | Prompt | Depende de | Status |
| --- | --- | --- | --- |
| 00 | [Kickoff e setup da org](00-kickoff-setup-org.md) | — | Pendente de envio |
| 01 | [Modelo de dados](01-modelo-de-dados.md) | 00 | Pendente de envio |
| 02 | [Sales Cloud](02-sales-cloud.md) | 01 | Pendente de envio |
| 03 | [Service Cloud](03-service-cloud.md) | 01 | Pendente de envio |
| 04 | [Automação cross-cloud](04-automacao-cross-cloud.md) | 02, 03 | Pendente de envio |
| 05 | [Relatórios e dashboards](05-relatorios-dashboards.md) | 02, 03, 04 | Pendente de envio |
| 06 | [Demo e pitch](06-demo-pitch.md) | 05 | Pendente de envio |

02 e 03 não dependem uma da outra — podem ser executadas em qualquer ordem entre si, mas sempre depois de 01 e sempre por um único dev em sequência (não em paralelo), conforme definido para este hackathon.

## Como usar

1. Confirmar que `docs/business-scenario.md` reflete o desafio real (ou aceitar o cenário fictício assumido).
2. Copiar o prompt da vez, colar na sessão do dev, aguardar a execução completa.
3. Pedir ao dev o link do commit/push e um resumo do que foi feito, do que ficou pendente e de qualquer bloqueio.
4. Atualizar a coluna Status nesta tabela.
5. Se o dev reportou desvio relevante (ex: licença ausente, decisão diferente do assumido), ajustar o próximo prompt **antes** de enviá-lo — não presumir que o próximo prompt ainda está correto sem checar.

## Atualizar o repositório Git do projeto

Diferente deste cofre, o **repositório do projeto Salesforce** é criado pelo dev no Prompt 00, fora daqui. Registrar o link dele assim que existir:

- **Repositório do projeto Salesforce:** _(preencher após o Prompt 00)_

## Notas de execução

_(registrar aqui, por prompt, qualquer desvio, bloqueio ou decisão tomada pelo dev que precise ser conhecida antes do próximo prompt)_
