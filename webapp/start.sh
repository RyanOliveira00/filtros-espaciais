#!/bin/bash

# Script de inicialização da aplicação web
# Trabalho de Processamento de Imagens

echo "========================================================"
echo "  Aplicação Web - Processamento de Imagens"
echo "  Filtros Espaciais para Redução de Ruído"
echo "========================================================"
echo ""

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "Por favor, instale o Python 3.7 ou superior"
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"
echo ""

# Verificar se as dependências estão instaladas
echo "Verificando dependências..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "📦 Instalando dependências..."
    pip3 install -r requirements.txt
else
    echo "✓ Dependências já instaladas"
fi

echo ""

# Criar diretórios necessários
echo "Criando diretórios..."
mkdir -p uploads results static/js templates
echo "✓ Diretórios criados"
echo ""

# Obter endereço IP local
IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

echo "========================================================"
echo "  Iniciando servidor..."
echo "========================================================"
echo ""
echo "🌐 Acesse a aplicação em:"
echo ""
echo "   Local:    http://localhost:8000"
echo "   Rede:     http://$IP:8000"
echo ""
echo "📝 Páginas disponíveis:"
echo "   - /        Página inicial"
echo "   - /demo    Demo interativa"
echo "   - /sobre   Sobre o trabalho"
echo ""
echo "⚠️  Pressione Ctrl+C para parar o servidor"
echo ""
echo "========================================================"
echo ""

# Iniciar servidor
python3 main.py
