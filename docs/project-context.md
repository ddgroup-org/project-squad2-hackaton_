---
title: "Contexto do projeto — quimicahackaton"
category: "context"
status: "active"
version: "2.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
source_of_truth: true
---

# Contexto do projeto

## O que é

Hackathon de **1 dia** para construir, do zero, uma solução Salesforce demonstrável cobrindo:

- **Sales Cloud** — pipeline de vendas
- **Service Cloud** — atendimento e suporte (fila de laboratório, casos de amostra e pós-venda)
- para dois modelos de cliente: **PJ** e **PF** (mesmo objeto Account, distinguidos pelo campo `TipoPessoa__c` — ver [ADR 0003](decisions/0003-account-sem-record-type-tipopessoa.md))
- no cenário real da **Cromatta Química** (indústria química, cliente simulado do hackathon — ver [business-scenario.md](business-scenario.md), a transcrição completa da reunião de requisitos em [transcricao.md](transcricao.md), e o **BRD oficial** em [entregaveis/BRD_Cromatta_Quimica_Squad02_final.pdf](entregaveis/BRD_Cromatta_Quimica_Squad02_final.pdf))

## Papéis

| Papel | Quem | Acesso à org | Acesso a este cofre |
| --- | --- | --- | --- |
| Tech lead | — | **Não** | Sim |
| Dev executor | outra pessoa | Sim | **Não** |
| Agente executor | Claude Code, em sessão própria do dev | via ferramentas do dev | **Não** |

Consequência direta: o tech lead não pode validar nada olhando a org. A única forma de acompanhamento é este mesmo **repositório Git** (planejamento + projeto Salesforce DX unificados), que o dev deve manter atualizado via commit/push a cada etapa.

## Restrições conhecidas

- **Duração:** 1 dia.
- **Regra de ouro do hackathon: tudo via Claude/IA, como padrão** — é o critério de maior peso na avaliação (25%). **Exceção explícita:** o que não for possível fazer via Claude pode ser feito direto na UI da org (a exceção é sobre viabilidade técnica, não preferência) — sempre registrando o que foi feito manualmente e por quê.
- Dentro do que pode ser feito via Claude: prioriza-se configuração declarativa (campos, record types, Flows, layouts, relatórios) sobre código customizado (Apex/LWC). Código customizado só quando a automação for inviável de forma declarativa, com justificativa registrada.
- **Org:** ainda não existe; será criada no início da execução (Developer Edition, Trailhead Playground ou Scratch Org). **Nunca** uma org de produção real ou com dados reais de clientes.
- **Execução:** um único dev, sozinho, com base no documento de requisitos — o **BRD oficial** (`entregaveis/BRD_Cromatta_Quimica_Squad02_final.pdf`) é a fonte de verdade mais recente; `business-scenario.md` e `architecture.md` são o resumo estruturado de apoio, atualizados para refletir o BRD onde há divergência — não há trilhas paralelas de equipe.
- **Sem supervisão em tempo real do tech lead** — os documentos de requisitos precisam ser suficientemente específicos para que o agente decida sozinho dentro do escopo autorizado, em vez de travar esperando validação humana que não vai chegar a tempo.

## Critérios de avaliação do hackathon

Confirmados na reunião de kickoff (ver [transcricao.md](transcricao.md)):

- **25%** — aderência: os requisitos foram implementados corretamente.
- **25%** — uso do Claude/IA na implementação.
- Qualidade de implementação — validação de todos os fluxos entregues.
- Organização ágil — backlog no Tarefai bem estruturado.
- **15%** — apresentação final (clareza, didática, demo ao vivo).

## Entregáveis esperados pela organização do hackathon

- **BRD** (documento de levantamento de requisitos) — [entregaveis/BRD_Cromatta_Quimica_Squad02_final.pdf](entregaveis/BRD_Cromatta_Quimica_Squad02_final.pdf), v1.0, aprovado pelo cliente e pelo tech lead.
- **Solution Design** — este repositório (`architecture.md`) cobre esse papel.
- **Repositório GitHub** com evidência do uso do Claude — este mesmo repositório, pasta [`evidencias/`](evidencias/README.md) (gerada automaticamente pelo fluxo `/executar-demanda`, ver [docs/como-executar-demandas.md](docs/como-executar-demandas.md)).
- **Backlog organizado** no Tarefai.
- **Apresentação final** (PPT + demo ao vivo dos principais fluxos: oportunidade, cases).

## Critérios de sucesso funcional (derivados dos requisitos)

- Demo funcional ao vivo cobrindo pelo menos: um fluxo completo de Oportunidade (Lead → conversão → Oportunidade → amostra → fechamento) e um fluxo completo de Case (amostra reprovada → fila do laboratório → resolução).
- Dados de exemplo coerentes com o cenário real (ver `business-scenario.md`).
- Repositório Git com a metadata versionada, permitindo revisão sem acesso à org.

## Pendências abertas

**Resolvido:** o repositório Git compartilhado para o projeto Salesforce já existe — [github.com/inaldojunior-a11y/SQUAD_02_HACKATON_DDGROUP_2026](https://github.com/inaldojunior-a11y/SQUAD_02_HACKATON_DDGROUP_2026), o mesmo repositório deste cofre. **Resolvido:** o desafio de negócio já é real (Cromatta Química), não mais fictício. **Resolvido:** o BRD oficial existe e confirmou os nomes dos químicos (Sérgio e André) e o threshold de concentração de receita (40%). **Resolvido:** Permission Set `Administrador Comercial` e Queue "Laboratório" já existem na org, com usuários atribuídos (demanda 02). **Resolvido:** 6 de 8 pendências do BRD 1.3.3 já têm resposta do cliente — ver [business-scenario.md](business-scenario.md#pendências-a-confirmar-com-o-cliente).

Pendências específicas do cliente que ainda restam: catálogo de produtos (cliente disse que ia enviar, ainda não chegou); escopo exato de "PF não vamos fazer" (impacto sobre o `TipoPessoa__c` já deployado). Pendências de execução deste cofre:

| Pendência | Responsável por confirmar |
| --- | --- |
| Licenças disponíveis na org (Service Cloud etc.) | Dev executor, no início da execução |
| Modelo de acesso restrito para o Ronaldo (só os próprios clientes, diferente do Permission Set `Vendedor` padrão) — demanda nova, ainda sem implementação | Dev executor |
| Confirmar com o cliente o escopo exato de "PF não vamos fazer" antes de alterar o modelo de Account | Tech lead / cliente |
