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
- para dois modelos de cliente: **PJ** (empresas, modelado como Business Account) e **PF** (consumidores finais, modelado como Individual Customer)
- no cenário real da **Cromatta Química** (indústria química, cliente simulado do hackathon — ver [business-scenario.md](business-scenario.md) e a transcrição completa da reunião de requisitos em [docs/transcricao.md](docs/transcricao.md))

## Papéis

| Papel | Quem | Acesso à org | Acesso a este cofre |
| --- | --- | --- | --- |
| Tech lead | — | **Não** | Sim |
| Dev executor | outra pessoa | Sim | **Não** |
| Agente executor | Claude Code, em sessão própria do dev | via ferramentas do dev | **Não** |

Consequência direta: o tech lead não pode validar nada olhando a org. A única forma de acompanhamento é este mesmo **repositório Git** (planejamento + projeto Salesforce DX unificados), que o dev deve manter atualizado via commit/push a cada etapa.

## Restrições conhecidas

- **Duração:** 1 dia.
- **Regra de ouro do hackathon: nenhuma configuração manual na UI do Salesforce.** Tudo deve ser feito via Claude/IA — é o critério de maior peso na avaliação (25%). Configuração manual só é aceitável quando comprovadamente impossível via IA, e isso deve ficar registrado como decisão explícita.
- Dentro do que pode ser feito via Claude: prioriza-se configuração declarativa (campos, record types, Flows, layouts, relatórios) sobre código customizado (Apex/LWC). Código customizado só quando a automação for inviável de forma declarativa, com justificativa registrada.
- **Org:** ainda não existe; será criada no início da execução (Developer Edition, Trailhead Playground ou Scratch Org). **Nunca** uma org de produção real ou com dados reais de clientes.
- **Execução:** um único dev, sozinho, com base no documento de requisitos (`business-scenario.md` + `architecture.md`, ambos derivados de `docs/transcricao.md`) — não há trilhas paralelas de equipe.
- **Sem supervisão em tempo real do tech lead** — os documentos de requisitos precisam ser suficientemente específicos para que o agente decida sozinho dentro do escopo autorizado, em vez de travar esperando validação humana que não vai chegar a tempo.

## Critérios de avaliação do hackathon

Confirmados na reunião de kickoff (ver [docs/transcricao.md](docs/transcricao.md)):

- **25%** — aderência: os requisitos foram implementados corretamente.
- **25%** — uso do Claude/IA na implementação.
- Qualidade de implementação — validação de todos os fluxos entregues.
- Organização ágil — backlog no Tarefai bem estruturado.
- **15%** — apresentação final (clareza, didática, demo ao vivo).

## Entregáveis esperados pela organização do hackathon

- **BRD** (documento de levantamento de requisitos) — este repositório (`business-scenario.md` + `docs/transcricao.md`) cobre esse papel.
- **Solution Design** — este repositório (`architecture.md`) cobre esse papel.
- **Repositório GitHub** com evidência do uso do Claude — este mesmo repositório.
- **Backlog organizado** no Tarefai.
- **Apresentação final** (PPT + demo ao vivo dos principais fluxos: oportunidade, cases).

## Critérios de sucesso funcional (derivados dos requisitos)

- Demo funcional ao vivo cobrindo pelo menos: um fluxo completo de Oportunidade (Lead → conversão → Oportunidade → amostra → fechamento) e um fluxo completo de Case (amostra reprovada → fila do laboratório → resolução).
- Dados de exemplo coerentes com o cenário real (ver `business-scenario.md`).
- Repositório Git com a metadata versionada, permitindo revisão sem acesso à org.

## Pendências abertas

**Resolvido:** o repositório Git compartilhado para o projeto Salesforce já existe — [github.com/inaldojunior-a11y/Squad2-Cromatta-quimica](https://github.com/inaldojunior-a11y/Squad2-Cromatta-quimica), o mesmo repositório deste cofre. **Resolvido:** o desafio de negócio já é real (Cromatta Química), não mais fictício.

| Pendência | Responsável por confirmar |
| --- | --- |
| Licenças disponíveis na org (Service Cloud etc.) | Dev executor, no início da execução |
| Nomes exatos dos dois químicos responsáveis pela fila do laboratório | Tech lead / cliente |
| Lista de produtos e lista de vendedores com papéis/acessos detalhados (cliente combinou compartilhar) | Tech lead / cliente |
| Regra de priorização entre chamados comerciais vs. técnicos no Service Cloud | Tech lead / cliente |
| Limite exato de concentração de receita que deve disparar alerta (hoje só sabemos que 60% já é alarmante) | Tech lead / cliente |
