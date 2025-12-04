#!/usr/bin/env python3
"""
Script para gerar imagens de teste para o trabalho
Útil caso você não tenha imagens próprias ainda
"""

import cv2
import numpy as np
import os


def criar_imagem_circulos(tamanho=(500, 500), num_circulos=15, seed=None):
    """
    Cria uma imagem com círculos aleatórios.

    Args:
        tamanho: Tupla (largura, altura)
        num_circulos: Número de círculos a desenhar
        seed: Seed para reprodutibilidade

    Returns:
        Imagem em tons de cinza
    """
    if seed is not None:
        np.random.seed(seed)

    # Criar imagem de fundo
    img = np.ones((tamanho[1], tamanho[0]), dtype=np.uint8) * 220

    # Adicionar círculos
    for _ in range(num_circulos):
        center_x = np.random.randint(60, tamanho[0] - 60)
        center_y = np.random.randint(60, tamanho[1] - 60)
        center = (center_x, center_y)

        radius = np.random.randint(20, 60)
        color = int(np.random.randint(40, 180))

        cv2.circle(img, center, radius, color, -1)

        # Adicionar borda mais escura em alguns círculos
        if np.random.random() > 0.5:
            border_color = max(0, color - 50)
            cv2.circle(img, center, radius, border_color, 3)

    return img


def criar_imagem_retangulos(tamanho=(500, 500), num_retangulos=12, seed=None):
    """
    Cria uma imagem com retângulos aleatórios.
    """
    if seed is not None:
        np.random.seed(seed)

    img = np.ones((tamanho[1], tamanho[0]), dtype=np.uint8) * 200

    for _ in range(num_retangulos):
        x1 = np.random.randint(20, tamanho[0] - 100)
        y1 = np.random.randint(20, tamanho[1] - 100)
        w = np.random.randint(30, 80)
        h = np.random.randint(30, 80)

        color = int(np.random.randint(50, 200))

        cv2.rectangle(img, (x1, y1), (x1 + w, y1 + h), color, -1)

        # Borda
        if np.random.random() > 0.6:
            border_color = max(0, color - 40)
            cv2.rectangle(img, (x1, y1), (x1 + w, y1 + h), border_color, 2)

    return img


def criar_imagem_grade(tamanho=(500, 500), espacamento=50, seed=None):
    """
    Cria uma imagem com padrão de grade e objetos.
    """
    if seed is not None:
        np.random.seed(seed)

    img = np.ones((tamanho[1], tamanho[0]), dtype=np.uint8) * 240

    # Desenhar grade
    for x in range(0, tamanho[0], espacamento):
        cv2.line(img, (x, 0), (x, tamanho[1]), 200, 1)

    for y in range(0, tamanho[1], espacamento):
        cv2.line(img, (0, y), (tamanho[0], y), 200, 1)

    # Adicionar círculos nos cruzamentos
    for x in range(0, tamanho[0], espacamento):
        for y in range(0, tamanho[1], espacamento):
            if np.random.random() > 0.6:
                radius = np.random.randint(8, 20)
                color = int(np.random.randint(80, 160))
                cv2.circle(img, (x, y), radius, color, -1)

    return img


def criar_imagem_texto(tamanho=(500, 500), seed=None):
    """
    Cria uma imagem com texto e formas geométricas.
    """
    if seed is not None:
        np.random.seed(seed)

    img = np.ones((tamanho[1], tamanho[0]), dtype=np.uint8) * 230

    # Adicionar algumas formas
    shapes = ['circle', 'rectangle', 'ellipse']

    for _ in range(10):
        shape = np.random.choice(shapes)

        if shape == 'circle':
            center = (np.random.randint(60, tamanho[0]-60),
                     np.random.randint(60, tamanho[1]-60))
            radius = np.random.randint(25, 55)
            color = int(np.random.randint(60, 170))
            cv2.circle(img, center, radius, color, -1)

        elif shape == 'rectangle':
            pt1 = (np.random.randint(20, tamanho[0]-100),
                  np.random.randint(20, tamanho[1]-100))
            pt2 = (pt1[0] + np.random.randint(40, 90),
                  pt1[1] + np.random.randint(40, 90))
            color = int(np.random.randint(60, 170))
            cv2.rectangle(img, pt1, pt2, color, -1)

        elif shape == 'ellipse':
            center = (np.random.randint(60, tamanho[0]-60),
                     np.random.randint(60, tamanho[1]-60))
            axes = (np.random.randint(25, 55), np.random.randint(20, 45))
            angle = np.random.randint(0, 180)
            color = int(np.random.randint(60, 170))
            cv2.ellipse(img, center, axes, angle, 0, 360, color, -1)

    # Adicionar texto
    fonts = [cv2.FONT_HERSHEY_SIMPLEX, cv2.FONT_HERSHEY_PLAIN, cv2.FONT_HERSHEY_DUPLEX]
    texts = ['ABC', '123', 'XYZ', 'TEST', '456']

    for i in range(5):
        text = np.random.choice(texts)
        font = np.random.choice(fonts)
        pos = (np.random.randint(20, tamanho[0]-80),
              np.random.randint(40, tamanho[1]-20))
        size = np.random.uniform(0.5, 1.5)
        color = int(np.random.randint(40, 140))

        cv2.putText(img, text, pos, font, size, color, 2)

    return img


def main():
    print("="*60)
    print(" "*15 + "GERADOR DE IMAGENS DE TESTE")
    print("="*60)

    # Criar pasta
    os.makedirs('images', exist_ok=True)

    # Configurações
    tamanho = (600, 600)

    # Gerar imagens
    print("\nGerando imagens de teste...\n")

    print("1. Imagem com círculos (moedas/botões)...")
    img1 = criar_imagem_circulos(tamanho, num_circulos=20, seed=42)
    cv2.imwrite('images/teste_circulos.jpg', img1)
    print("   ✓ images/teste_circulos.jpg")

    print("\n2. Imagem com retângulos (placas/objetos)...")
    img2 = criar_imagem_retangulos(tamanho, num_retangulos=15, seed=123)
    cv2.imwrite('images/teste_retangulos.jpg', img2)
    print("   ✓ images/teste_retangulos.jpg")

    print("\n3. Imagem com grade (células/padrão)...")
    img3 = criar_imagem_grade(tamanho, espacamento=60, seed=456)
    cv2.imwrite('images/teste_grade.jpg', img3)
    print("   ✓ images/teste_grade.jpg")

    # Variações extras
    print("\n4. Imagem com formas mistas (variação 1)...")
    img4 = criar_imagem_texto(tamanho, seed=789)
    cv2.imwrite('images/teste_misto1.jpg', img4)
    print("   ✓ images/teste_misto1.jpg")

    print("\n5. Imagem com formas mistas (variação 2)...")
    img5 = criar_imagem_texto(tamanho, seed=999)
    cv2.imwrite('images/teste_misto2.jpg', img5)
    print("   ✓ images/teste_misto2.jpg")

    print("\n6. Imagem com círculos (variação 2)...")
    img6 = criar_imagem_circulos(tamanho, num_circulos=25, seed=111)
    cv2.imwrite('images/teste_circulos2.jpg', img6)
    print("   ✓ images/teste_circulos2.jpg")

    print("\n" + "="*60)
    print("✓ 6 imagens de teste geradas com sucesso!")
    print("="*60)

    print("\n📝 Próximos passos:")
    print("  1. Escolha 3 das imagens geradas")
    print("  2. Atualize o notebook ou script com os nomes dos arquivos")
    print("  3. Execute o processamento")

    print("\n💡 Dica:")
    print("  Você também pode usar suas próprias imagens!")
    print("  Coloque-as na pasta 'images/' e atualize os nomes.")

    print("\n📂 Exemplo para o notebook:")
    print("  image_files = [")
    print("      'images/teste_circulos.jpg',")
    print("      'images/teste_retangulos.jpg',")
    print("      'images/teste_grade.jpg'")
    print("  ]")

    print("\n📂 Exemplo para o script Python:")
    print("  python processamento_imagens.py \\")
    print("    --images images/teste_circulos.jpg \\")
    print("             images/teste_retangulos.jpg \\")
    print("             images/teste_grade.jpg")

    print()


if __name__ == '__main__':
    main()
