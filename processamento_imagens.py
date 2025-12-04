#!/usr/bin/env python3
"""
Trabalho de Processamento de Imagens
Aplicação de Filtros Espaciais para Redução de Ruído

Script alternativo para execução sem Jupyter Notebook
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.stats import mode
import pandas as pd
import os
import argparse


# =============================================================================
# FUNÇÕES DE GERAÇÃO DE RUÍDO
# =============================================================================

def add_salt_pepper_noise(image, salt_prob=0.01, pepper_prob=0.01):
    """Adiciona ruído sal e pimenta à imagem."""
    noisy = image.copy()

    # Ruído sal (branco)
    salt_mask = np.random.random(image.shape) < salt_prob
    noisy[salt_mask] = 255

    # Ruído pimenta (preto)
    pepper_mask = np.random.random(image.shape) < pepper_prob
    noisy[pepper_mask] = 0

    return noisy


def add_gaussian_noise(image, mean=0, sigma=25):
    """Adiciona ruído gaussiano à imagem."""
    gaussian = np.random.normal(mean, sigma, image.shape)
    noisy = image + gaussian
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy


# =============================================================================
# FUNÇÕES DE FILTROS ESPACIAIS
# =============================================================================

def apply_mean_filter(image, kernel_size=3):
    """Aplica filtro de média."""
    return cv2.blur(image, (kernel_size, kernel_size))


def apply_gaussian_filter(image, kernel_size=3):
    """Aplica filtro gaussiano."""
    sigma = 0.3 * ((kernel_size - 1) * 0.5 - 1) + 0.8
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)


def apply_median_filter(image, kernel_size=3):
    """Aplica filtro de mediana."""
    return cv2.medianBlur(image, kernel_size)


def apply_mode_filter(image, kernel_size=3):
    """Aplica filtro de moda."""
    pad = kernel_size // 2
    padded = np.pad(image, pad, mode='edge')
    output = np.zeros_like(image)

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            window = padded[i:i+kernel_size, j:j+kernel_size]
            output[i, j] = mode(window, axis=None, keepdims=False)[0]

    return output.astype(np.uint8)


# =============================================================================
# FUNÇÕES DE AVALIAÇÃO QUANTITATIVA
# =============================================================================

def calculate_mse(original, filtered):
    """Calcula o Mean Squared Error (MSE) entre duas imagens."""
    mse = np.mean((original.astype(float) - filtered.astype(float)) ** 2)
    return mse


def calculate_psnr(original, filtered):
    """Calcula o Peak Signal-to-Noise Ratio (PSNR) entre duas imagens."""
    mse = calculate_mse(original, filtered)
    if mse == 0:
        return float('inf')

    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr


# =============================================================================
# PROCESSAMENTO PRINCIPAL
# =============================================================================

def process_image_with_filters(original, noisy):
    """
    Processa uma imagem aplicando todos os filtros e calcula as métricas.
    """
    results = {}

    filters = [
        ('Média 3x3', apply_mean_filter, 3),
        ('Média 7x7', apply_mean_filter, 7),
        ('Gaussiano 3x3', apply_gaussian_filter, 3),
        ('Gaussiano 7x7', apply_gaussian_filter, 7),
        ('Mediana 3x3', apply_median_filter, 3),
        ('Mediana 7x7', apply_median_filter, 7),
        ('Moda 3x3', apply_mode_filter, 3),
        ('Moda 7x7', apply_mode_filter, 7),
    ]

    print("  Aplicando filtros:")
    for filter_name, filter_func, kernel_size in filters:
        print(f"    - {filter_name}...", end=' ', flush=True)

        # Aplicar filtro
        filtered = filter_func(noisy, kernel_size)

        # Calcular métricas
        mse = calculate_mse(original, filtered)
        psnr = calculate_psnr(original, filtered)

        results[filter_name] = {
            'image': filtered,
            'mse': mse,
            'psnr': psnr
        }

        print("OK")

    return results


def save_comparison_figures(original_images, noisy_images, all_results, noise_type, output_dir):
    """Gera e salva figuras comparativas."""

    print("\nGerando figuras comparativas...")

    # Figura 1: Original vs Ruidosa
    print("  - Comparação Original vs Ruidosa...", end=' ', flush=True)
    fig, axes = plt.subplots(len(original_images), 2, figsize=(12, 4*len(original_images)))

    if len(original_images) == 1:
        axes = axes.reshape(1, -1)

    for i in range(len(original_images)):
        axes[i, 0].imshow(original_images[i], cmap='gray', vmin=0, vmax=255)
        axes[i, 0].set_title(f'Imagem {i+1} - Original')
        axes[i, 0].axis('off')

        axes[i, 1].imshow(noisy_images[i], cmap='gray', vmin=0, vmax=255)
        axes[i, 1].set_title(f'Imagem {i+1} - Com Ruído ({noise_type})')
        axes[i, 1].axis('off')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/comparacao_original_ruido.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("OK")

    # Figura 2: Comparação selecionada para relatório
    selected_filters = ['Média 3x3', 'Média 7x7', 'Gaussiano 7x7', 'Mediana 3x3']

    for img_idx in range(len(all_results)):
        print(f"  - Comparação para relatório (Imagem {img_idx+1})...", end=' ', flush=True)

        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        # Original
        axes[0].imshow(original_images[img_idx], cmap='gray', vmin=0, vmax=255)
        axes[0].set_title('Original', fontsize=14, fontweight='bold')
        axes[0].axis('off')

        # Ruidosa
        axes[1].imshow(noisy_images[img_idx], cmap='gray', vmin=0, vmax=255)
        axes[1].set_title(f'Com Ruído ({noise_type})', fontsize=14, fontweight='bold')
        axes[1].axis('off')

        # Filtros selecionados
        for i, filter_name in enumerate(selected_filters):
            if filter_name in all_results[img_idx]:
                filtered_img = all_results[img_idx][filter_name]['image']
                psnr = all_results[img_idx][filter_name]['psnr']
                mse = all_results[img_idx][filter_name]['mse']

                axes[i+2].imshow(filtered_img, cmap='gray', vmin=0, vmax=255)
                axes[i+2].set_title(f'{filter_name}\nPSNR: {psnr:.2f} dB | MSE: {mse:.2f}', fontsize=12)
                axes[i+2].axis('off')

        plt.suptitle(f'Comparação Visual - Imagem {img_idx+1}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/comparacao_relatorio_imagem{img_idx+1}.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("OK")

    # Figura 3: Gráficos de métricas
    print("  - Gráficos de métricas...", end=' ', flush=True)
    filter_names = list(all_results[0].keys())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Gráfico de MSE
    for img_idx in range(len(all_results)):
        mse_values = [all_results[img_idx][f]['mse'] for f in filter_names]
        ax1.plot(filter_names, mse_values, marker='o', label=f'Imagem {img_idx+1}', linewidth=2)

    ax1.set_xlabel('Filtro', fontsize=12, fontweight='bold')
    ax1.set_ylabel('MSE', fontsize=12, fontweight='bold')
    ax1.set_title('Mean Squared Error por Filtro', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)

    # Gráfico de PSNR
    for img_idx in range(len(all_results)):
        psnr_values = [all_results[img_idx][f]['psnr'] for f in filter_names]
        ax2.plot(filter_names, psnr_values, marker='s', label=f'Imagem {img_idx+1}', linewidth=2)

    ax2.set_xlabel('Filtro', fontsize=12, fontweight='bold')
    ax2.set_ylabel('PSNR (dB)', fontsize=12, fontweight='bold')
    ax2.set_title('Peak Signal-to-Noise Ratio por Filtro', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/graficos_metricas.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("OK")


def main():
    parser = argparse.ArgumentParser(description='Processamento de Imagens - Filtros Espaciais')
    parser.add_argument('--images', nargs='+', required=True, help='Caminhos das imagens a processar')
    parser.add_argument('--noise', choices=['salt_pepper', 'gaussian'], default='salt_pepper',
                        help='Tipo de ruído (default: salt_pepper)')
    parser.add_argument('--output', default='results', help='Diretório de saída (default: results)')

    args = parser.parse_args()

    # Criar diretórios
    os.makedirs(args.output, exist_ok=True)

    print("="*70)
    print(" "*15 + "PROCESSAMENTO DE IMAGENS")
    print(" "*10 + "Filtros Espaciais para Redução de Ruído")
    print("="*70)

    # Carregar imagens
    print(f"\n1. Carregando imagens...")
    original_images = []

    for img_path in args.images:
        if os.path.exists(img_path):
            img = cv2.imread(img_path)
            if img is None:
                print(f"  ⚠️ Erro ao carregar: {img_path}")
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            original_images.append(gray)
            print(f"  ✓ {img_path} ({gray.shape[1]}x{gray.shape[0]})")
        else:
            print(f"  ⚠️ Não encontrado: {img_path}")

    if len(original_images) == 0:
        print("\n❌ Nenhuma imagem foi carregada!")
        return

    print(f"\n✓ {len(original_images)} imagem(ns) carregada(s)")

    # Gerar ruído
    print(f"\n2. Aplicando ruído ({args.noise})...")
    noisy_images = []

    for i, img in enumerate(original_images):
        if args.noise == 'salt_pepper':
            noisy = add_salt_pepper_noise(img, salt_prob=0.02, pepper_prob=0.02)
        else:
            noisy = add_gaussian_noise(img, mean=0, sigma=25)
        noisy_images.append(noisy)
        print(f"  ✓ Imagem {i+1}")

    # Processar imagens
    print(f"\n3. Aplicando filtros e calculando métricas...")
    all_results = []

    for i, (original, noisy) in enumerate(zip(original_images, noisy_images)):
        print(f"\nImagem {i+1}:")
        results = process_image_with_filters(original, noisy)
        all_results.append(results)

    # Salvar tabelas
    print(f"\n4. Gerando tabelas de resultados...")

    for i, results in enumerate(all_results):
        data = []
        for filter_name, metrics in results.items():
            data.append({
                'Filtro': filter_name,
                'MSE': f"{metrics['mse']:.4f}",
                'PSNR (dB)': f"{metrics['psnr']:.4f}"
            })

        df = pd.DataFrame(data)
        csv_path = f'{args.output}/metricas_imagem_{i+1}.csv'
        df.to_csv(csv_path, index=False)
        print(f"  ✓ {csv_path}")

    # Tabela média
    if len(all_results) > 1:
        filter_names = list(all_results[0].keys())
        avg_data = []

        for filter_name in filter_names:
            avg_mse = np.mean([r[filter_name]['mse'] for r in all_results])
            avg_psnr = np.mean([r[filter_name]['psnr'] for r in all_results])

            avg_data.append({
                'Filtro': filter_name,
                'MSE Médio': f"{avg_mse:.4f}",
                'PSNR Médio (dB)': f"{avg_psnr:.4f}"
            })

        df_avg = pd.DataFrame(avg_data)
        df_avg.to_csv(f'{args.output}/metricas_media.csv', index=False)
        print(f"  ✓ {args.output}/metricas_media.csv")

    # Salvar figuras
    print(f"\n5. Gerando figuras...")
    save_comparison_figures(original_images, noisy_images, all_results, args.noise, args.output)

    # Salvar imagens processadas
    print(f"\n6. Salvando imagens processadas...")

    for img_idx, results in enumerate(all_results):
        img_folder = f'{args.output}/imagem_{img_idx+1}'
        os.makedirs(img_folder, exist_ok=True)

        cv2.imwrite(f'{img_folder}/original.png', original_images[img_idx])
        cv2.imwrite(f'{img_folder}/ruidosa.png', noisy_images[img_idx])

        for filter_name, data in results.items():
            filename = filter_name.lower().replace(' ', '_').replace('x', '')
            cv2.imwrite(f'{img_folder}/{filename}.png', data['image'])

        print(f"  ✓ {img_folder}/ ({len(results)+2} arquivos)")

    # Resumo final
    print("\n" + "="*70)
    print(" "*20 + "RESUMO FINAL")
    print("="*70)

    print(f"\n📊 Estatísticas:")
    print(f"  • Imagens processadas: {len(all_results)}")
    print(f"  • Tipo de ruído: {args.noise}")
    print(f"  • Filtros testados: {len(all_results[0])}")

    # Melhor filtro
    filter_names = list(all_results[0].keys())
    avg_mse_per_filter = {}

    for filter_name in filter_names:
        avg_mse = np.mean([r[filter_name]['mse'] for r in all_results])
        avg_mse_per_filter[filter_name] = avg_mse

    best_filter = min(avg_mse_per_filter.items(), key=lambda x: x[1])
    best_psnr = np.mean([r[best_filter[0]]['psnr'] for r in all_results])

    print(f"\n🏆 Melhor filtro (média):")
    print(f"  • {best_filter[0]}")
    print(f"  • MSE médio: {best_filter[1]:.4f}")
    print(f"  • PSNR médio: {best_psnr:.4f} dB")

    print(f"\n📁 Resultados salvos em: {args.output}/")

    print("\n" + "="*70)
    print(" "*15 + "✓ PROCESSAMENTO CONCLUÍDO!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
