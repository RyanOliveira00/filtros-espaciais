#!/usr/bin/env python3
"""
Script para testar se todas as dependências estão instaladas corretamente
Execute antes de começar o trabalho para verificar o ambiente
"""

import sys

def test_imports():
    """Testa importação de todas as bibliotecas necessárias."""

    print("="*60)
    print(" "*15 + "TESTE DE INSTALAÇÃO")
    print(" "*10 + "Verificando dependências...")
    print("="*60)
    print()

    all_ok = True

    # Lista de bibliotecas a testar
    libraries = [
        ('cv2', 'OpenCV', 'opencv-python'),
        ('numpy', 'NumPy', 'numpy'),
        ('matplotlib', 'Matplotlib', 'matplotlib'),
        ('scipy', 'SciPy', 'scipy'),
        ('pandas', 'Pandas', 'pandas'),
    ]

    for module_name, display_name, pip_name in libraries:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✓ {display_name:15s} [{version}]")
        except ImportError:
            print(f"✗ {display_name:15s} [NÃO INSTALADO]")
            print(f"  → Instale com: pip install {pip_name}")
            all_ok = False

    print()

    # Teste do Jupyter (opcional)
    print("Componentes opcionais:")
    try:
        import jupyter
        print(f"✓ Jupyter Notebook [instalado]")
    except ImportError:
        print(f"⚠ Jupyter Notebook [não instalado - opcional]")
        print(f"  → Para usar o notebook: pip install jupyter")

    print()
    print("="*60)

    if all_ok:
        print("✓ TODAS AS DEPENDÊNCIAS ESTÃO INSTALADAS!")
        print("="*60)
        print()
        print("Próximos passos:")
        print("  1. Coloque suas imagens na pasta 'images/'")
        print("  2. Execute: jupyter notebook processamento_imagens.ipynb")
        print("     OU: python processamento_imagens.py --images [suas imagens]")
        print()
        return True
    else:
        print("✗ ALGUMAS DEPENDÊNCIAS ESTÃO FALTANDO!")
        print("="*60)
        print()
        print("Para instalar todas de uma vez:")
        print("  pip install -r requirements.txt")
        print()
        print("Ou instale manualmente as que estão faltando.")
        print()
        return False


def test_opencv_functionality():
    """Testa funcionalidades básicas do OpenCV."""

    print("Testando funcionalidades do OpenCV...")
    print()

    try:
        import cv2
        import numpy as np

        # Criar imagem de teste
        test_img = np.ones((100, 100), dtype=np.uint8) * 128

        # Testar filtros
        tests = [
            ("Filtro de Média", lambda: cv2.blur(test_img, (3, 3))),
            ("Filtro Gaussiano", lambda: cv2.GaussianBlur(test_img, (3, 3), 0)),
            ("Filtro de Mediana", lambda: cv2.medianBlur(test_img, 3)),
        ]

        for name, func in tests:
            try:
                result = func()
                print(f"  ✓ {name}")
            except Exception as e:
                print(f"  ✗ {name}: {e}")
                return False

        print()
        print("✓ OpenCV está funcionando corretamente!")
        print()
        return True

    except Exception as e:
        print(f"✗ Erro ao testar OpenCV: {e}")
        print()
        return False


def test_matplotlib():
    """Testa se matplotlib pode criar figuras."""

    print("Testando Matplotlib...")
    print()

    try:
        import matplotlib
        import matplotlib.pyplot as plt

        # Configurar backend não-interativo para teste
        matplotlib.use('Agg')

        # Criar figura de teste
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        plt.close(fig)

        print("  ✓ Matplotlib pode criar figuras")
        print()
        print("✓ Matplotlib está funcionando corretamente!")
        print()
        return True

    except Exception as e:
        print(f"✗ Erro ao testar Matplotlib: {e}")
        print()
        return False


def check_python_version():
    """Verifica versão do Python."""

    print("Verificando versão do Python...")
    print()

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print(f"  Python {version_str}")
    print()

    if version.major == 3 and version.minor >= 7:
        print("✓ Versão do Python é compatível (Python 3.7+)")
        print()
        return True
    else:
        print("⚠ Python 3.7 ou superior é recomendado")
        print("  Sua versão pode funcionar, mas não é garantido")
        print()
        return False


def test_file_structure():
    """Verifica estrutura de arquivos do projeto."""

    import os

    print("Verificando estrutura de arquivos...")
    print()

    required_files = [
        'processamento_imagens.ipynb',
        'processamento_imagens.py',
        'requirements.txt',
        'README.md',
    ]

    optional_files = [
        'gerar_imagens_teste.py',
        'exemplo_uso.md',
        'GUIA_RAPIDO.md',
        'TEMPLATE_RELATORIO.md',
    ]

    print("Arquivos principais:")
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} [FALTANDO]")
            all_present = False

    print()
    print("Arquivos auxiliares:")
    for file in optional_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  - {file}")

    print()

    # Verificar pastas
    print("Estrutura de pastas:")
    if os.path.exists('images'):
        num_images = len([f for f in os.listdir('images')
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"  ✓ images/ ({num_images} imagem(ns))")
    else:
        print(f"  - images/ [não existe - será criada]")

    if os.path.exists('results'):
        print(f"  ✓ results/")
    else:
        print(f"  - results/ [será criada ao executar]")

    print()

    if all_present:
        print("✓ Estrutura de arquivos OK!")
        print()
    else:
        print("⚠ Alguns arquivos estão faltando")
        print()

    return all_present


def main():
    """Executa todos os testes."""

    results = []

    # Teste 1: Versão do Python
    results.append(check_python_version())

    # Teste 2: Dependências
    results.append(test_imports())

    # Teste 3: OpenCV
    if results[-1]:  # Só testa se imports OK
        results.append(test_opencv_functionality())

    # Teste 4: Matplotlib
    if results[1]:  # Só testa se imports OK
        results.append(test_matplotlib())

    # Teste 5: Estrutura de arquivos
    results.append(test_file_structure())

    # Resumo final
    print("="*60)
    print(" "*20 + "RESUMO FINAL")
    print("="*60)
    print()

    if all(results):
        print("🎉 TUDO PRONTO PARA COMEÇAR O TRABALHO!")
        print()
        print("Sugestões:")
        print("  1. Se não tem imagens: python gerar_imagens_teste.py")
        print("  2. Leia o GUIA_RAPIDO.md para instruções")
        print("  3. Execute o notebook ou script Python")
        print()
        return 0
    else:
        print("⚠ ALGUNS PROBLEMAS FORAM ENCONTRADOS")
        print()
        print("Revise as mensagens acima e corrija os problemas.")
        print()
        print("Dica: Execute 'pip install -r requirements.txt'")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
