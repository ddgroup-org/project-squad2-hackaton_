---
title: "quimicahackaton — Instruções para sessão de IA neste cofre"
category: "instructions"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Paulo Carvalho"
applies_to:
  - quimicahackaton
source_of_truth: true
---

# quimicahackaton — instruções para quem trabalhar neste cofre

Este arquivo vale para uma sessão de IA aberta **dentro desta pasta** (`~/Desktop/quimicahackaton`), ajudando Paulo a planejar. **Não vale para a sessão que executa os prompts na org** — aquela não tem acesso a este arquivo, e por isso cada prompt em `docs/demands/` é escrito para ser lido sem nenhum contexto externo.

## O que este cofre é

Planejamento de um hackathon Salesforce de 1 dia (Sales Cloud + Service Cloud, B2B e B2C, setor químico). Ver [docs/project-context.md](docs/project-context.md).

## O que este cofre não é

- Não é o repositório do projeto Salesforce (esse é criado pelo dev executor, fora daqui, no Prompt 00).
- Não é a Salesforce-AI-Base — não duplicar conteúdo de lá; referenciar por caminho relativo quando fizer sentido (`../Salesforce-AI-Base/...`), sabendo que quem lê isso aqui é só Paulo, não o dev executor.
- Não substitui a leitura da Salesforce-AI-Base para padrões técnicos gerais; este cofre guarda apenas o que é específico deste evento.

## Regra central deste projeto

**Todo prompt destinado à sessão executora deve ser autocontido.** Antes de considerar um prompt em `docs/demands/` pronto para envio, verificar:

- [ ] Não referencia nenhum arquivo fora do próprio texto do prompt (nem este cofre, nem a Salesforce-AI-Base, nem prompts anteriores).
- [ ] Repete o cenário de negócio, o objetivo do hackathon e as restrições relevantes.
- [ ] Declara papel, escopo, fora de escopo, critérios de aceite e quando parar para perguntar.
- [ ] Exige retrieve + commit/push da metadata alterada ao final, para visibilidade do tech lead sem acesso à org.
- [ ] Não presume dado de negócio, licença ou configuração de org sem checar antes — trata isso como pendência a confirmar na execução, nunca como suposição silenciosa.
- [ ] Está em português, tom direto, sem depender de conhecimento tácito da conversa com Paulo.

## Fluxo de trabalho neste cofre

1. Ajustar `docs/business-scenario.md` se o desafio real divergir do cenário fictício assumido.
2. Preparar/ajustar o prompt da vez em `docs/demands/`.
3. Entregar o prompt a Paulo para colar na sessão do dev executor.
4. Registrar o retorno do dev (o que foi feito, pendências, bloqueios) nas notas do prompt correspondente ou em `docs/demands/README.md`.
5. Ajustar o próximo prompt com base no que realmente aconteceu — não repetir cegamente o planejado se o dev reportou desvio.

## Onde salvar o que for produzido durante o hackathon

Documentação técnica real do projeto Salesforce (metadata, manifests, evidências, package.xml) pertence ao **repositório do projeto Salesforce**, criado pelo dev executor — nunca a este cofre nem à Salesforce-AI-Base. Este cofre guarda apenas planejamento, decisões e os prompts em si.
