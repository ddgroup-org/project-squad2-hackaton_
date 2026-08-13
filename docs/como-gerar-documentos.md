---
title: "Como gerar documentos corporativos (PDF) — quimicahackaton"
category: "guide"
status: "active"
version: "1.0"
last_reviewed: "2026-08-13"
owner: "Tech lead"
applies_to:
  - quimicahackaton
---

# Como gerar documentos corporativos (PDF)

Todo entregável em PDF deste hackathon (Solution Design, BRD final, roteiro de demo, relatório da apresentação etc.) deve usar o **modelo oficial DDGroup × Cromatta**, não um estilo novo por documento.

## Modelo

[`templates/documento-corporativo-cromatta.html`](../templates/documento-corporativo-cromatta.html) — HTML + CSS com a identidade visual das duas marcas: logo da Cromatta e logo da DDGroup na capa (`imgs/01_Cromatta_Logo_Principal_Horizontal.png` e `imgs/DDGroup.png`), paleta de cores oficial da Cromatta. Contém no topo do arquivo as regras de uso (o que pode e o que não pode ser alterado) e um bloco de seção de exemplo para copiar.

**Footer obrigatório em toda seção (exceto a capa):** nome de quem gerou o documento, cargo, empresa, data de geração e a marca "CONFIDENCIAL" — já vem como bloco `.footer-note` pronto no template, só preencher os placeholders (`{NOME_GERADOR}`, `{CARGO_GERADOR}`, `{EMPRESA_GERADOR}`, `{DATA_GERACAO}`). Valores padrão sugeridos no comentário do próprio template (Paulo Carvalho, Tech Lead, DDGroup) — ajustar se outra pessoa gerar o documento.

Exemplo real e completo já implementado (capa, diagrama de objetos em SVG, tabelas, callouts): [`entregaveis/02_Solution_Design_Cromatta_Quimica_Squad02.pdf`](../entregaveis/02_Solution_Design_Cromatta_Quimica_Squad02.pdf) — resultado final do primeiro Solution Design, use como referência visual de como aplicar o modelo na prática (o `.html` de trabalho que gerou este PDF não foi mantido no repositório — só o PDF final, conforme o passo 5 abaixo).

## Passo a passo

1. Copiar `templates/documento-corporativo-cromatta.html` para um arquivo de trabalho (pode ficar em `/tmp` ou em qualquer pasta temporária — só o PDF final vai para o repositório).
2. Substituir o conteúdo entre `{chaves}` e o conteúdo de cada `<section>`, sem alterar as variáveis de cor em `:root` nem as classes existentes.
3. Garantir que o `<img src="file://...">` da logo aponte para o caminho **absoluto** de `imgs/01_Cromatta_Logo_Principal_Horizontal.png` neste repositório.
4. Gerar o PDF com o Chrome headless (já disponível na máquina, sem instalar nada):
   ```
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
     --headless=new --disable-gpu --no-pdf-header-footer \
     --print-to-pdf="/caminho/absoluto/entregaveis/NOME_DO_DOCUMENTO.pdf" \
     --virtual-time-budget=10000 \
     "file:///caminho/absoluto/do/arquivo-de-trabalho.html"
   ```
5. Salvar o PDF final em [`entregaveis/`](../entregaveis/) — e, se fizer sentido manter como referência editável, o `.html` de trabalho também (nome igual ao PDF, extensão `.html`).
6. Conferir visualmente antes de considerar concluído: captura de tela do HTML (`--screenshot=arquivo.png` no mesmo comando, trocando `--print-to-pdf`) ou abrir o PDF gerado.

## Por que Chrome headless, e não pandoc/wkhtmltopdf

Nenhuma dessas ferramentas estava disponível no ambiente no momento em que isso foi decidido, e instalar uma dependência nova no meio do hackathon é um risco desnecessário. O Google Chrome já vem instalado na máquina e dá controle total de CSS (cores da marca, tipografia, layout) — por isso é o caminho padrão deste projeto. Se isso mudar, atualizar esta nota.
