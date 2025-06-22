"""
Модуль для генерации QR-кодов и их преобразования в 3D структуры.
"""

import qrcode
import numpy as np
from PIL import Image
from typing import Tuple, Optional
import qrcode.constants

from .config import Config


class QRGenerator:
    """Класс для генерации QR-кодов."""
    
    ERROR_CORRECTION_MAP = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    
    def __init__(self, config: Config):
        """
        Инициализация генератора QR-кодов.
        
        Args:
            config: Конфигурация проекта
        """
        self.config = config
        self._qr_matrix = None
        self._qr_image = None
    
    def generate_qr_matrix(self) -> np.ndarray:
        """
        Генерировать матрицу QR-кода.
        
        Returns:
            Двумерный массив numpy с QR-кодом (True/False)
        """
        # Создание QR-кода
        qr = qrcode.QRCode(
            version=self.config.qr_settings.version,
            error_correction=self.ERROR_CORRECTION_MAP.get(
                self.config.qr_settings.error_correction, 
                qrcode.constants.ERROR_CORRECT_M
            ),
            box_size=self.config.qr_settings.box_size,
            border=self.config.qr_settings.border,
        )
        
        qr.add_data(self.config.text)
        qr.make(fit=True)
        
        # Получение матрицы
        matrix = qr.get_matrix()
        self._qr_matrix = np.array(matrix, dtype=bool)
        
        return self._qr_matrix
    
    def generate_qr_image(self, 
                         fill_color: Optional[str] = None,
                         back_color: str = 'white') -> Image.Image:
        """
        Генерировать изображение QR-кода.
        
        Args:
            fill_color: Цвет заливки (по умолчанию из конфигурации)
            back_color: Цвет фона
            
        Returns:
            PIL изображение QR-кода
        """
        if fill_color is None:
            fill_color = self.config.primary_color
        
        qr = qrcode.QRCode(
            version=self.config.qr_settings.version,
            error_correction=self.ERROR_CORRECTION_MAP.get(
                self.config.qr_settings.error_correction,
                qrcode.constants.ERROR_CORRECT_M
            ),
            box_size=self.config.qr_settings.box_size,
            border=self.config.qr_settings.border,
        )
        
        qr.add_data(self.config.text)
        qr.make(fit=True)
        
        self._qr_image = qr.make_image(fill_color=fill_color, back_color=back_color)
        return self._qr_image
    
    def get_qr_matrix(self) -> np.ndarray:
        """
        Получить матрицу QR-кода (генерирует если не существует).
        
        Returns:
            Двумерный массив numpy с QR-кодом
        """
        if self._qr_matrix is None:
            self.generate_qr_matrix()
        return self._qr_matrix
    
    def get_qr_image(self) -> Image.Image:
        """
        Получить изображение QR-кода (генерирует если не существует).
        
        Returns:
            PIL изображение QR-кода
        """
        if self._qr_image is None:
            self.generate_qr_image()
        return self._qr_image
    
    def get_matrix_dimensions(self) -> Tuple[int, int]:
        """
        Получить размеры матрицы QR-кода.
        
        Returns:
            Кортеж (высота, ширина)
        """
        matrix = self.get_qr_matrix()
        return matrix.shape
    
    def create_height_map(self) -> np.ndarray:
        """
        Создать карту высот для 3D модели.
        
        Returns:
            Двумерный массив с высотами для каждого пикселя
        """
        matrix = self.get_qr_matrix()
        height_map = np.zeros_like(matrix, dtype=float)
        
        # Базовая толщина для всех элементов
        height_map.fill(self.config.settings_3d.base_thickness)
        
        # Высота для активных пикселей QR-кода
        height_map[matrix] = self.config.settings_3d.height
        
        # Сглаживание краёв если включено
        if self.config.settings_3d.smooth_edges:
            height_map = self._smooth_edges(height_map, matrix)
        
        return height_map
    
    def _smooth_edges(self, height_map: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        """
        Сгладить края для более плавных переходов.
        
        Args:
            height_map: Карта высот
            matrix: Исходная матрица QR-кода
            
        Returns:
            Сглаженная карта высот
        """
        from scipy import ndimage
        
        # Создание ядра для сглаживания
        kernel_size = max(1, int(self.config.settings_3d.bevel_depth * 10))
        kernel = np.ones((kernel_size, kernel_size)) / (kernel_size * kernel_size)
        
        # Применение фильтра только к краям
        edges = self._find_edges(matrix)
        smoothed = ndimage.convolve(height_map, kernel, mode='constant')
        
        # Применение сглаживания только к краевым областям
        result = height_map.copy()
        result[edges] = smoothed[edges]
        
        return result
    
    def _find_edges(self, matrix: np.ndarray) -> np.ndarray:
        """
        Найти края в матрице QR-кода.
        
        Args:
            matrix: Матрица QR-кода
            
        Returns:
            Булева матрица с краями
        """
        from scipy import ndimage
        
        # Создание ядер для обнаружения краёв
        kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        kernel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        
        # Применение фильтров
        edges_x = ndimage.convolve(matrix.astype(float), kernel_x)
        edges_y = ndimage.convolve(matrix.astype(float), kernel_y)
        
        # Объединение краёв
        edges = np.sqrt(edges_x**2 + edges_y**2) > 0.1
        
        return edges
    
    def create_glow_map(self) -> np.ndarray:
        """
        Создать карту свечения для внутренних областей.
        
        Returns:
            Двумерный массив с интенсивностью свечения
        """
        matrix = self.get_qr_matrix()
        glow_map = np.zeros_like(matrix, dtype=float)
        
        # Базовое свечение для активных пикселей
        glow_map[matrix] = self.config.settings_3d.glow_intensity
        
        # Создание эффекта внутреннего свечения
        if self.config.settings_3d.glow_intensity > 0:
            glow_map = self._create_inner_glow(glow_map, matrix)
        
        return glow_map
    
    def _create_inner_glow(self, glow_map: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        """
        Создать эффект внутреннего свечения.
        
        Args:
            glow_map: Исходная карта свечения
            matrix: Матрица QR-кода
            
        Returns:
            Карта свечения с внутренним эффектом
        """
        from scipy import ndimage
        
        # Размытие для создания эффекта свечения
        sigma = max(1, self.config.settings_3d.glow_intensity * 2)
        blurred = ndimage.gaussian_filter(glow_map.astype(float), sigma=sigma)
        
        # Комбинирование исходного и размытого свечения
        result = np.maximum(glow_map, blurred * 0.5)
        
        # Ограничение интенсивности
        result = np.clip(result, 0, self.config.settings_3d.glow_intensity)
        
        return result
    
    def get_info(self) -> dict:
        """
        Получить информацию о сгенерированном QR-коде.
        
        Returns:
            Словарь с информацией о QR-коде
        """
        matrix = self.get_qr_matrix()
        
        return {
            'text': self.config.text,
            'text_length': len(self.config.text),
            'matrix_size': matrix.shape,
            'total_modules': matrix.size,
            'active_modules': np.sum(matrix),
            'fill_ratio': np.sum(matrix) / matrix.size,
            'version': self.config.qr_settings.version,
            'error_correction': self.config.qr_settings.error_correction,
            'box_size': self.config.qr_settings.box_size,
            'border': self.config.qr_settings.border
        }
    
    def save_2d_image(self, output_path: str) -> None:
        """
        Сохранить 2D изображение QR-кода.
        
        Args:
            output_path: Путь для сохранения
        """
        image = self.get_qr_image()
        image.save(output_path)
    
    def __str__(self) -> str:
        """Строковое представление генератора."""
        info = self.get_info()
        return (f"QRGenerator(text_length={info['text_length']}, "
                f"matrix_size={info['matrix_size']}, "
                f"version={info['version']})")
    
    def __repr__(self) -> str:
        """Подробное строковое представление."""
        return f"QRGenerator(config={self.config})"