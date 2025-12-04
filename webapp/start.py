#!/usr/bin/env python3
"""
Script de inicialização da aplicação web
Compatível com Windows, Linux e macOS
"""

import os
import sys
import subprocess
import socket


def get_local_ip():
    """Obtém o IP local da máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


def print_header():
    """Imprime cabeçalho"""
    print("=" * 60)
    print(" " * 10 + "Aplicação Web - Processamento de Imagens")
    print(" " * 8 + "Filtros Espaciais para Redução de Ruído")
    print("=" * 60)
    print()


def check_python():
    """Verifica versão do Python"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("⚠️  Python 3.7+ é recomendado")
    print()


def check_dependencies():
    """Verifica e instala dependências"""
    print("Verificando dependências...")

    try:
        import fastapi
        import uvicorn
        import cv2
        import numpy
        import plotly
        print("✓ Todas as dependências estão instaladas")
    except ImportError:
        print("📦 Instalando dependências...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Dependências instaladas")

    print()


def create_directories():
    """Cria diretórios necessários"""
    print("Criando diretórios...")

    dirs = ["uploads", "results", "static/js", "templates"]
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

    print("✓ Diretórios criados")
    print()


def print_access_info(port=8000):
    """Imprime informações de acesso"""
    ip = get_local_ip()

    print("=" * 60)
    print(" " * 15 + "Iniciando servidor...")
    print("=" * 60)
    print()
    print("🌐 Acesse a aplicação em:")
    print()
    print(f"   Local:    http://localhost:{port}")
    print(f"   Rede:     http://{ip}:{port}")
    print()
    print("📝 Páginas disponíveis:")
    print("   - /        Página inicial")
    print("   - /demo    Demo interativa")
    print("   - /sobre   Sobre o trabalho")
    print()
    print("⚠️  Pressione Ctrl+C para parar o servidor")
    print()
    print("=" * 60)
    print()


def start_server(port=8000):
    """Inicia o servidor uvicorn"""
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n✓ Servidor encerrado")
        print("Até logo!")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        print("\nTente:")
        print(f"  python -m uvicorn main:app --port {port+1}")
        sys.exit(1)


def main():
    """Função principal"""
    print_header()
    check_python()
    check_dependencies()
    create_directories()
    print_access_info()
    start_server()


if __name__ == "__main__":
    main()
