---
title: "quimicahackaton — Instruções para sessão de IA neste cofre"
category: "instructions"
status: "active"
version: "1.1"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
source_of_truth: true
---

# quimicahackaton — instruções para quem trabalhar neste cofre

Este arquivo vale para uma sessão de IA aberta **dentro desta pasta** (`~/Desktop/cromatta`), ajudando o tech lead a planejar e executar.

## O que esta pasta é

Planejamento e execução de um hackathon Salesforce de 1 dia (Sales Cloud + Service Cloud, B2B e B2C, setor químico). Ver [docs/project-context.md](docs/project-context.md).

Nesta mesma pasta/repositório (`Squad2-Cromatta-quimica`) convivem:

- **Planejamento:** este arquivo, `project-context.md`, `business-scenario.md`, `architecture.md`, `decisions/` (e as cópias em `docs/`).
- **Projeto Salesforce DX:** `sfdx-project.json`, `force-app/`, `config/`, `manifest/`, `scripts/` — estrutura gerada via `sf project generate`, pronta para receber a metadata da execução.

O trabalho é guiado por um **documento de requisitos** (a ser adicionado a este repositório) — o modelo anterior de prompts autocontidos separados em `demands/` foi descontinuado.

## O que esta pasta não é

- Não é a Salesforce-AI-Base — não duplicar conteúdo de lá; referenciar por caminho relativo quando fizer sentido (`../Salesforce-AI-Base/...`).
- Não substitui a leitura da Salesforce-AI-Base para padrões técnicos gerais; este repositório guarda apenas o que é específico deste evento.

## Regra central deste projeto

**Antes de qualquer `git push`, sempre fazer `sf project retrieve start` (ou equivalente) primeiro.** A metadata commitada precisa refletir o estado real da org — nunca commitar/dar push às cegas sem confirmar o que a org realmente tem. Sem esse fluxo, o tech lead (sem acesso à org) acaba revisando um histórico que pode não corresponder à realidade.

## Fluxo de trabalho neste cofre

1. Ajustar `docs/business-scenario.md` se o desafio real divergir do cenário fictício assumido.
2. Trabalhar com base no documento de requisitos (quando adicionado a este repositório).
3. Antes de cada `git push`: `sf project retrieve start`, revisar o diff, comitar, só então dar push.
4. Registrar decisões arquiteturais relevantes em `decisions/` (ADR) e desvios de execução onde fizer sentido.

## Onde salvar o que for produzido durante o hackathon

Documentação técnica real do projeto Salesforce (metadata, manifests, evidências, package.xml) vive **neste mesmo repositório**, dentro de `force-app/`, `manifest/` e `config/` — não em um repositório separado.
