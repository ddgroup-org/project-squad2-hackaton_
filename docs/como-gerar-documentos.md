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

Todo entregável em PDF deste hackathon (Solution Design, BRD final, roteiro de demo, relatório da apresentação etc.) deve usar o **modelo oficial da Cromatta**, não um estilo novo por documento.

## Modelo

[`templates/documento-corporativo-cromatta.html`](../templates/documento-corporativo-cromatta.html) — HTML + CSS com a identidade visual da marca (logo e paleta de cores em `imgs/`). Contém no topo do arquivo as regras de uso (o que pode e o que não pode ser alterado) e um bloco de seção de exemplo para copiar.

Exemplo real e completo já implementado (capa, diagrama de objetos em SVG, tabelas, callouts): [`entregaveis/02_Solution_Design_Cromatta_Quimica_Squad02.html`](../entregaveis/02_Solution_Design_Cromatta_Quimica_Squad02.html) — este é o código-fonte que gerou o primeiro Solution Design; use como referência de como aplicar o modelo na prática, especialmente o padrão de diagrama SVG (caixas + setas coloridas por tipo de objeto).

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
