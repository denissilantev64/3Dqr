"""
Модуль для создания 3D мешей на основе QR-кодов.
"""

import numpy as np
import trimesh
from typing import Tuple, List, Optional, Dict, Any
from scipy import ndimage

from .config import Config
from .qr_generator import QRGenerator


class MeshBuilder:
    """Класс для создания 3D мешей QR-кодов."""
    
    def __init__(self, config: Config, qr_generator: QRGenerator):
        """
        Инициализация строителя мешей.
        
        Args:
            config: Конфигурация проекта
            qr_generator: Генератор QR-кодов
        """
        self.config = config
        self.qr_generator = qr_generator
        self._mesh = None
        self._vertices = None
        self._faces = None
        self._colors = None
    
    def create_mesh(self) -> trimesh.Trimesh:
        """
        Создать 3D меш QR-кода.
        
        Returns:
            Trimesh объект с 3D моделью
        """
        # Получение данных QR-кода
        matrix = self.qr_generator.get_qr_matrix()
        height_map = self.qr_generator.create_height_map()
        glow_map = self.qr_generator.create_glow_map()
        
        # Создание вершин и граней
        vertices, faces = self._create_vertices_and_faces(matrix, height_map)
        
        # Создание цветов для вершин
        colors = self._create_vertex_colors(matrix, glow_map, len(vertices))
        
        # Создание меша
        self._mesh = trimesh.Trimesh(
            vertices=vertices,
            faces=faces,
            vertex_colors=colors,
            process=True
        )
        
        # Применение дополнительных эффектов
        if self.config.settings_3d.smooth_edges:
            self._mesh = self._apply_smoothing()
        
        self._vertices = vertices
        self._faces = faces
        self._colors = colors
        
        return self._mesh
    
    def _create_vertices_and_faces(self, 
                                  matrix: np.ndarray, 
                                  height_map: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Создать вершины и грани для 3D меша.
        
        Args:
            matrix: Матрица QR-кода
            height_map: Карта высот
            
        Returns:
            Кортеж (вершины, грани)
        """
        height, width = matrix.shape
        resolution = self.config.settings_3d.resolution
        
        # Создание сетки координат
        x = np.linspace(0, width, resolution)
        y = np.linspace(0, height, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Интерполяция карты высот
        Z = self._interpolate_height_map(height_map, X, Y)
        
        # Создание вершин
        vertices = []
        
        # Верхняя поверхность
        for i in range(resolution):
            for j in range(resolution):
                vertices.append([X[i, j], Y[i, j], Z[i, j]])
        
        # Нижняя поверхность (базовая плоскость)
        for i in range(resolution):
            for j in range(resolution):
                vertices.append([X[i, j], Y[i, j], 0])
        
        # Боковые стенки для краёв
        edge_vertices = self._create_edge_vertices(matrix, height_map)
        vertices.extend(edge_vertices)
        
        vertices = np.array(vertices)
        
        # Создание граней
        faces = self._create_faces(resolution, len(edge_vertices))
        
        return vertices, faces
    
    def _interpolate_height_map(self, 
                               height_map: np.ndarray, 
                               X: np.ndarray, 
                               Y: np.ndarray) -> np.ndarray:
        """
        Интерполировать карту высот для заданной сетки.
        
        Args:
            height_map: Исходная карта высот
            X, Y: Координатные сетки
            
        Returns:
            Интерполированная карта высот
        """
        from scipy.interpolate import RegularGridInterpolator
        
        h, w = height_map.shape
        
        # Создание интерполятора
        y_orig = np.arange(h)
        x_orig = np.arange(w)
        interpolator = RegularGridInterpolator(
            (y_orig, x_orig), 
            height_map, 
            method='linear',
            bounds_error=False,
            fill_value=0
        )
        
        # Интерполяция
        points = np.column_stack([Y.ravel(), X.ravel()])
        Z = interpolator(points).reshape(X.shape)
        
        return Z
    
    def _create_edge_vertices(self, 
                             matrix: np.ndarray, 
                             height_map: np.ndarray) -> List[List[float]]:
        """
        Создать вершины для боковых стенок.
        
        Args:
            matrix: Матрица QR-кода
            height_map: Карта высот
            
        Returns:
            Список вершин для боковых стенок
        """
        vertices = []
        height, width = matrix.shape
        
        # Обход по периметру
        for i in range(height):
            for j in range(width):
                if self._is_edge_pixel(matrix, i, j):
                    h = height_map[i, j]
                    # Добавляем вершины для боковых стенок
                    vertices.extend([
                        [j, i, 0],      # Нижняя вершина
                        [j, i, h],      # Верхняя вершина
                        [j+1, i, 0],    # Нижняя вершина (следующая)
                        [j+1, i, h],    # Верхняя вершина (следующая)
                        [j, i+1, 0],    # Нижняя вершина (следующая строка)
                        [j, i+1, h],    # Верхняя вершина (следующая строка)
                        [j+1, i+1, 0],  # Нижняя вершина (диагональ)
                        [j+1, i+1, h]   # Верхняя вершина (диагональ)
                    ])
        
        return vertices
    
    def _is_edge_pixel(self, matrix: np.ndarray, i: int, j: int) -> bool:
        """
        Проверить, является ли пиксель краевым.
        
        Args:
            matrix: Матрица QR-кода
            i, j: Координаты пикселя
            
        Returns:
            True если пиксель на краю
        """
        height, width = matrix.shape
        
        # Проверка границ
        if i == 0 or i == height-1 or j == 0 or j == width-1:
            return matrix[i, j]
        
        # Проверка соседей
        if matrix[i, j]:
            neighbors = [
                matrix[i-1, j], matrix[i+1, j],
                matrix[i, j-1], matrix[i, j+1]
            ]
            return not all(neighbors)
        
        return False
    
    def _create_faces(self, resolution: int, edge_vertex_count: int) -> np.ndarray:
        """
        Создать грани для меша.
        
        Args:
            resolution: Разрешение сетки
            edge_vertex_count: Количество вершин для краёв
            
        Returns:
            Массив граней
        """
        faces = []
        
        # Грани для верхней поверхности
        for i in range(resolution - 1):
            for j in range(resolution - 1):
                # Индексы вершин для квада
                v1 = i * resolution + j
                v2 = i * resolution + (j + 1)
                v3 = (i + 1) * resolution + j
                v4 = (i + 1) * resolution + (j + 1)
                
                # Два треугольника для квада
                faces.extend([
                    [v1, v2, v3],
                    [v2, v4, v3]
                ])
        
        # Грани для нижней поверхности
        offset = resolution * resolution
        for i in range(resolution - 1):
            for j in range(resolution - 1):
                v1 = offset + i * resolution + j
                v2 = offset + i * resolution + (j + 1)
                v3 = offset + (i + 1) * resolution + j
                v4 = offset + (i + 1) * resolution + (j + 1)
                
                # Обратный порядок для нижней поверхности
                faces.extend([
                    [v1, v3, v2],
                    [v2, v3, v4]
                ])
        
        # Грани для боковых стенок
        edge_offset = 2 * resolution * resolution
        for i in range(0, edge_vertex_count, 8):
            if i + 7 < edge_vertex_count:
                base = edge_offset + i
                # Создание граней для боковых стенок
                faces.extend([
                    [base, base+1, base+2],
                    [base+1, base+3, base+2],
                    [base+2, base+3, base+4],
                    [base+3, base+5, base+4],
                    [base+4, base+5, base+6],
                    [base+5, base+7, base+6]
                ])
        
        return np.array(faces)
    
    def _create_vertex_colors(self, 
                             matrix: np.ndarray, 
                             glow_map: np.ndarray, 
                             vertex_count: int) -> np.ndarray:
        """
        Создать цвета для вершин.
        
        Args:
            matrix: Матрица QR-кода
            glow_map: Карта свечения
            vertex_count: Количество вершин
            
        Returns:
            Массив цветов RGBA
        """
        colors = np.zeros((vertex_count, 4))
        
        primary_rgb = self.config.get_primary_color_rgb()
        inner_rgb = self.config.get_inner_color_rgb()
        
        resolution = self.config.settings_3d.resolution
        height, width = matrix.shape
        
        # Цвета для верхней поверхности
        for i in range(resolution):
            for j in range(resolution):
                # Преобразование координат в индексы матрицы
                matrix_i = int(i * height / resolution)
                matrix_j = int(j * width / resolution)
                
                matrix_i = min(matrix_i, height - 1)
                matrix_j = min(matrix_j, width - 1)
                
                vertex_idx = i * resolution + j
                
                if matrix[matrix_i, matrix_j]:
                    # Активный пиксель - смешивание основного и внутреннего цветов
                    glow_intensity = glow_map[matrix_i, matrix_j]
                    
                    # Интерполяция между основным и внутренним цветом
                    color = self._blend_colors(primary_rgb, inner_rgb, glow_intensity)
                    colors[vertex_idx] = [*color, 1.0]
                else:
                    # Неактивный пиксель - прозрачный или базовый цвет
                    colors[vertex_idx] = [0.2, 0.2, 0.2, 0.3]
        
        # Цвета для нижней поверхности
        offset = resolution * resolution
        for i in range(resolution):
            for j in range(resolution):
                vertex_idx = offset + i * resolution + j
                colors[vertex_idx] = [0.1, 0.1, 0.1, 1.0]  # Тёмный базовый цвет
        
        # Цвета для боковых стенок
        edge_offset = 2 * resolution * resolution
        for i in range(edge_offset, vertex_count):
            colors[i] = [*primary_rgb, 0.8]  # Основной цвет с прозрачностью
        
        return colors
    
    def _blend_colors(self, 
                     color1: Tuple[float, float, float], 
                     color2: Tuple[float, float, float], 
                     factor: float) -> Tuple[float, float, float]:
        """
        Смешать два цвета.
        
        Args:
            color1: Первый цвет (RGB)
            color2: Второй цвет (RGB)
            factor: Фактор смешивания (0-1)
            
        Returns:
            Смешанный цвет (RGB)
        """
        factor = np.clip(factor, 0, 1)
        
        r = color1[0] * (1 - factor) + color2[0] * factor
        g = color1[1] * (1 - factor) + color2[1] * factor
        b = color1[2] * (1 - factor) + color2[2] * factor
        
        return (r, g, b)
    
    def _apply_smoothing(self) -> trimesh.Trimesh:
        """
        Применить сглаживание к мешу.
        
        Returns:
            Сглаженный меш
        """
        if self._mesh is None:
            return None
        
        # Применение Laplacian сглаживания
        smoothed = self._mesh.smoothed()
        
        return smoothed
    
    def get_mesh(self) -> Optional[trimesh.Trimesh]:
        """
        Получить созданный меш.
        
        Returns:
            Trimesh объект или None если не создан
        """
        return self._mesh
    
    def save_mesh(self, output_path: str, file_format: str = 'obj') -> None:
        """
        Сохранить меш в файл.
        
        Args:
            output_path: Путь для сохранения
            file_format: Формат файла (obj, ply, stl)
        """
        if self._mesh is None:
            raise ValueError("Меш не создан. Вызовите create_mesh() сначала.")
        
        if file_format.lower() == 'obj':
            self._mesh.export(output_path)
        elif file_format.lower() == 'ply':
            self._mesh.export(output_path)
        elif file_format.lower() == 'stl':
            # STL не поддерживает цвета
            mesh_copy = self._mesh.copy()
            mesh_copy.visual = None
            mesh_copy.export(output_path)
        else:
            raise ValueError(f"Неподдерживаемый формат: {file_format}")
    
    def get_mesh_info(self) -> Dict[str, Any]:
        """
        Получить информацию о меше.
        
        Returns:
            Словарь с информацией о меше
        """
        if self._mesh is None:
            return {}
        
        return {
            'vertex_count': len(self._mesh.vertices),
            'face_count': len(self._mesh.faces),
            'volume': self._mesh.volume,
            'surface_area': self._mesh.area,
            'bounds': self._mesh.bounds.tolist(),
            'center_mass': self._mesh.center_mass.tolist(),
            'is_watertight': self._mesh.is_watertight,
            'is_winding_consistent': self._mesh.is_winding_consistent
        }
    
    def create_wireframe(self) -> trimesh.path.Path3D:
        """
        Создать каркасную модель.
        
        Returns:
            Каркасная модель
        """
        if self._mesh is None:
            raise ValueError("Меш не создан. Вызовите create_mesh() сначала.")
        
        # Создание каркаса из рёбер
        wireframe = self._mesh.outline()
        
        return wireframe
    
    def __str__(self) -> str:
        """Строковое представление строителя мешей."""
        info = self.get_mesh_info()
        if info:
            return (f"MeshBuilder(vertices={info.get('vertex_count', 0)}, "
                   f"faces={info.get('face_count', 0)})")
        return "MeshBuilder(no mesh created)"
    
    def __repr__(self) -> str:
        """Подробное строковое представление."""
        return f"MeshBuilder(config={self.config})"