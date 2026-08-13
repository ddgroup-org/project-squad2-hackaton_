#!/bin/bash
# Captura um screenshot da tela inteira e salva em evidencias/prints/, como
# evidência visual de execução (critério de avaliação: uso do Claude/IA).
#
# Uso: scripts/capturar-print.sh [rotulo]
#
# ATENÇÃO: este repositório é público. O screenshot é da tela inteira — feche
# ou minimize qualquer coisa fora do escopo do hackathon antes de rodar, e
# confira o arquivo gerado antes de dar commit/push.

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PRINTS_DIR="$DIR/evidencias/prints"
mkdir -p "$PRINTS_DIR"

LABEL="${1:-print}"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
FILE="$PRINTS_DIR/${TIMESTAMP}-${LABEL}.png"

screencapture -x "$FILE"

echo "Screenshot salvo em: $FILE"
echo "Confira o conteúdo antes de dar commit/push — este repositório é público."
