---
title: "Contexto do projeto — quimicahackaton"
category: "context"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Paulo Carvalho"
applies_to:
  - quimicahackaton
source_of_truth: true
---

# Contexto do projeto

## O que é

Hackathon de **1 dia** para construir, do zero, uma solução Salesforce demonstrável cobrindo:

- **Sales Cloud** — pipeline de vendas
- **Service Cloud** — atendimento e suporte
- para dois modelos de cliente: **B2B** (empresas) e **B2C** (consumidores finais)
- no cenário de uma empresa do **setor químico** (ver [business-scenario.md](business-scenario.md))

## Papéis

| Papel | Quem | Acesso à org | Acesso a este cofre |
| --- | --- | --- | --- |
| Tech lead | Paulo Carvalho | **Não** | Sim |
| Dev executor | outra pessoa | Sim | **Não** |
| Agente executor | Claude Code, em sessão própria do dev | via ferramentas do dev | **Não** |

Consequência direta: Paulo não pode validar nada olhando a org. A única forma de acompanhamento é o **repositório Git do projeto Salesforce**, que o dev cria no Prompt 00 e deve manter atualizado via commit/push a cada etapa.

## Restrições conhecidas

- **Duração:** 1 dia — prioriza-se configuração declarativa (campos, record types, Flows, layouts, relatórios) sobre código customizado (Apex/LWC). Código customizado só quando a automação for inviável de forma declarativa, com justificativa registrada.
- **Org:** ainda não existe; será criada no Prompt 00 (Developer Edition, Trailhead Playground ou Scratch Org). **Nunca** uma org de produção real ou com dados reais de clientes.
- **Execução:** um único dev, sozinho, rodando os prompts em sequência — não há trilhas paralelas de equipe.
- **Sem supervisão em tempo real do tech lead** — os prompts precisam ser suficientemente específicos para que o agente decida sozinho dentro do escopo autorizado, em vez de travar esperando validação humana que não vai chegar a tempo.

## Critérios de sucesso do hackathon

Pendente de confirmação com a organização do hackathon (regras de julgamento, formato de pitch, tempo de apresentação). Assumido como padrão até confirmação:

- Demo funcional ao vivo, cobrindo ao menos um fluxo completo B2B e um fluxo completo B2C, em Sales Cloud e em Service Cloud.
- Dados de exemplo coerentes com o cenário (ver `business-scenario.md`).
- Repositório Git com a metadata versionada, permitindo revisão sem acesso à org.

## Pendências abertas

| Pendência | Responsável por confirmar |
| --- | --- |
| Regras/critérios de julgamento do hackathon | Paulo, junto à organização |
| Se o desafio de negócio é fictício (assumido) ou já definido pela organização | Paulo |
| Licenças disponíveis na org (Service Cloud, Omni-Channel, Knowledge, Entitlements) | Dev executor, no Prompt 00 |
| Repositório Git compartilhado (novo ou existente) para o projeto Salesforce | Paulo + dev executor, antes do Prompt 00 |
