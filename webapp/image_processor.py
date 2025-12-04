import cv2
import numpy as np
from scipy.stats import mode
from typing import Dict, Tuple
import base64
from io import BytesIO
from PIL import Image


class ImageProcessor:

    def __init__(self):
        self.filter_names = [
            'Média 3x3', 'Média 7x7',
            'Gaussiano 3x3', 'Gaussiano 7x7',
            'Mediana 3x3', 'Mediana 7x7',
            'Moda 3x3', 'Moda 7x7'
        ]

    @staticmethod
    def add_salt_pepper_noise(image: np.ndarray, salt_prob: float = 0.02, pepper_prob: float = 0.02) -> np.ndarray:
        noisy = image.copy()
        salt_mask = np.random.random(image.shape) < salt_prob
        noisy[salt_mask] = 255
        pepper_mask = np.random.random(image.shape) < pepper_prob
        noisy[pepper_mask] = 0
        return noisy

    @staticmethod
    def add_gaussian_noise(image: np.ndarray, mean: float = 0, sigma: float = 25) -> np.ndarray:
        gaussian = np.random.normal(mean, sigma, image.shape)
        noisy = image + gaussian
        noisy = np.clip(noisy, 0, 255).astype(np.uint8)
        return noisy

    @staticmethod
    def apply_mean_filter(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        return cv2.blur(image, (kernel_size, kernel_size))

    @staticmethod
    def apply_gaussian_filter(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        sigma = 0.3 * ((kernel_size - 1) * 0.5 - 1) + 0.8
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)

    @staticmethod
    def apply_median_filter(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        return cv2.medianBlur(image, kernel_size)

    @staticmethod
    def apply_mode_filter(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        pad = kernel_size // 2
        padded = np.pad(image, pad, mode='edge')
        output = np.zeros_like(image)
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                window = padded[i:i+kernel_size, j:j+kernel_size]
                output[i, j] = mode(window, axis=None, keepdims=False)[0]
        return output.astype(np.uint8)

    @staticmethod
    def calculate_mse(original: np.ndarray, filtered: np.ndarray) -> float:
        mse = np.mean((original.astype(float) - filtered.astype(float)) ** 2)
        return float(mse)

    @staticmethod
    def calculate_psnr(original: np.ndarray, filtered: np.ndarray) -> float:
        mse = ImageProcessor.calculate_mse(original, filtered)
        if mse == 0:
            return float('inf')
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        return float(psnr)

    def process_image(self, original: np.ndarray, noisy: np.ndarray, progress_callback=None) -> Dict:
        results = {}
        filters = [
            ('Média 3x3', self.apply_mean_filter, 3),
            ('Média 7x7', self.apply_mean_filter, 7),
            ('Gaussiano 3x3', self.apply_gaussian_filter, 3),
            ('Gaussiano 7x7', self.apply_gaussian_filter, 7),
            ('Mediana 3x3', self.apply_median_filter, 3),
            ('Mediana 7x7', self.apply_median_filter, 7),
            ('Moda 3x3', self.apply_mode_filter, 3),
            ('Moda 7x7', self.apply_mode_filter, 7),
        ]

        total = len(filters)
        for idx, (filter_name, filter_func, kernel_size) in enumerate(filters):
            if progress_callback:
                progress_callback(idx, total, filter_name)
            filtered = filter_func(noisy, kernel_size)
            mse = self.calculate_mse(original, filtered)
            psnr = self.calculate_psnr(original, filtered)
            results[filter_name] = {'image': filtered, 'mse': mse, 'psnr': psnr}
        return results

    @staticmethod
    def image_to_base64(image: np.ndarray) -> str:
        pil_img = Image.fromarray(image)
        buffer = BytesIO()
        pil_img.save(buffer, format='PNG')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return gray

    def get_best_filter(self, results: Dict) -> Tuple[str, Dict]:
        best_filter = min(results.items(), key=lambda x: x[1]['mse'])
        return best_filter[0], best_filter[1]

    def get_summary_stats(self, results: Dict) -> Dict:
        mse_values = [r['mse'] for r in results.values()]
        psnr_values = [r['psnr'] for r in results.values()]
        best_filter, best_data = self.get_best_filter(results)
        worst_filter = max(results.items(), key=lambda x: x[1]['mse'])[0]
        return {
            'best_filter': best_filter,
            'best_mse': best_data['mse'],
            'best_psnr': best_data['psnr'],
            'worst_filter': worst_filter,
            'avg_mse': np.mean(mse_values),
            'avg_psnr': np.mean(psnr_values),
            'min_mse': np.min(mse_values),
            'max_mse': np.max(mse_values),
            'min_psnr': np.min(psnr_values),
            'max_psnr': np.max(psnr_values)
        }
