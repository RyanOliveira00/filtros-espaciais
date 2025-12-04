#!/bin/bash

# Script para gerar PDF do RELATORIO.md
# Remove emojis e caracteres Unicode incompatíveis com LaTeX

echo "Gerando RELATORIO.pdf..."

# Remove emojis e caracteres Unicode especiais
sed 's/🥇 //g; s/✅/**/g; s/❌/X/g; s/⚠️/!/g; s/➕/+/g; s/➖/-/g; s/⭐ //g; s/⭐//g; s/📊/>/g; s/↔/<->/g' RELATORIO.md > RELATORIO_temp.md

# Adiciona BasicTeX ao PATH
export PATH="/Library/TeX/texbin:$PATH"

# Gera o PDF com imagens
echo "Processando markdown e imagens..."
pandoc RELATORIO_temp.md -s -o RELATORIO.pdf \
    --pdf-engine=pdflatex \
    --variable geometry:margin=1in \
    --variable fontsize=11pt \
    --toc \
    --toc-depth=3

# Remove arquivo temporário
rm RELATORIO_temp.md

if [ -f "RELATORIO.pdf" ]; then
    echo "✓ PDF gerado com sucesso: RELATORIO.pdf"
    ls -lh RELATORIO.pdf
    echo ""
    echo "O PDF inclui:"
    echo "  - Sumário navegável"
    echo "  - Todas as imagens de results/"
    echo "  - Tabelas de métricas"
    echo "  - Gráficos comparativos"
else
    echo "✗ Erro ao gerar PDF"
    exit 1
fi
