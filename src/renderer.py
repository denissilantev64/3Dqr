"""
Модуль для рендеринга и визуализации 3D QR-кодов.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.offline as pyo
from PIL import Image
import trimesh
import os
from typing import Optional, Tuple, List, Dict, Any

from .config import Config
from .qr_generator import QRGenerator
from .mesh_builder import MeshBuilder


class Renderer:
    """Класс для рендеринга 3D QR-кодов."""
    
    def __init__(self, config: Config, qr_generator: QRGenerator, mesh_builder: MeshBuilder):
        """
        Инициализация рендерера.
        
        Args:
            config: Конфигурация проекта
            qr_generator: Генератор QR-кодов
            mesh_builder: Строитель мешей
        """
        self.config = config
        self.qr_generator = qr_generator
        self.mesh_builder = mesh_builder
    
    def render_matplotlib(self, output_path: str, show_plot: bool = False) -> None:
        """
        Рендеринг с использованием Matplotlib.
        
        Args:
            output_path: Путь для сохранения изображения
            show_plot: Показать ли график
        """
        # Получение данных
        matrix = self.qr_generator.get_qr_matrix()
        height_map = self.qr_generator.create_height_map()
        glow_map = self.qr_generator.create_glow_map()
        
        # Создание фигуры
        fig = plt.figure(figsize=(
            self.config.output.width / self.config.output.dpi,
            self.config.output.height / self.config.output.dpi
        ), dpi=self.config.output.dpi)
        
        ax = fig.add_subplot(111, projection='3d')
        
        # Создание координатных сеток
        height, width = matrix.shape
        x = np.arange(width)
        y = np.arange(height)
        X, Y = np.meshgrid(x, y)
        
        # Создание цветовой карты
        colors = self._create_color_map(matrix, glow_map)
        
        # Рендеринг поверхности
        surf = ax.plot_surface(
            X, Y, height_map,
            facecolors=colors,
            alpha=0.9,
            linewidth=0,
            antialiased=True,
            shade=True
        )
        
        # Настройка освещения и внешнего вида
        self._setup_matplotlib_lighting(ax)
        self._setup_matplotlib_appearance(ax, matrix.shape)
        
        # Сохранение
        plt.savefig(
            output_path,
            dpi=self.config.output.dpi,
            bbox_inches='tight',
            facecolor='black',
            edgecolor='none'
        )
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def render_plotly(self, output_path: str, interactive: bool = True) -> None:
        """
        Рендеринг с использованием Plotly.
        
        Args:
            output_path: Путь для сохранения
            interactive: Создать интерактивную версию
        """
        # Получение данных
        matrix = self.qr_generator.get_qr_matrix()
        height_map = self.qr_generator.create_height_map()
        glow_map = self.qr_generator.create_glow_map()
        
        # Создание координатных сеток
        height, width = matrix.shape
        x = np.arange(width)
        y = np.arange(height)
        X, Y = np.meshgrid(x, y)
        
        # Создание цветов для Plotly
        colors_plotly = self._create_plotly_colors(matrix, glow_map)
        
        # Создание поверхности
        surface = go.Surface(
            x=X,
            y=Y,
            z=height_map,
            surfacecolor=colors_plotly,
            colorscale=self._create_custom_colorscale(),
            showscale=False,
            lighting=dict(
                ambient=self.config.lighting.ambient,
                diffuse=self.config.lighting.diffuse,
                specular=self.config.lighting.specular,
                roughness=0.1,
                fresnel=0.2
            ),
            lightposition=dict(
                x=self.config.lighting.position[0],
                y=self.config.lighting.position[1],
                z=self.config.lighting.position[2]
            )
        )
        
        # Создание фигуры
        fig = go.Figure(data=[surface])
        
        # Настройка макета
        fig.update_layout(
            title=dict(
                text="3D QR Code",
                x=0.5,
                font=dict(color='white', size=16)
            ),
            scene=dict(
                xaxis=dict(
                    title="X",
                    backgroundcolor="black",
                    gridcolor="gray",
                    showbackground=True,
                    zerolinecolor="gray"
                ),
                yaxis=dict(
                    title="Y",
                    backgroundcolor="black",
                    gridcolor="gray",
                    showbackground=True,
                    zerolinecolor="gray"
                ),
                zaxis=dict(
                    title="Height",
                    backgroundcolor="black",
                    gridcolor="gray",
                    showbackground=True,
                    zerolinecolor="gray"
                ),
                bgcolor="black",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            paper_bgcolor="black",
            plot_bgcolor="black",
            width=self.config.output.width,
            height=self.config.output.height
        )
        
        if interactive:
            # Сохранение как HTML
            pyo.plot(fig, filename=output_path, auto_open=False)
        else:
            # Сохранение как статичное изображение
            fig.write_image(output_path, width=self.config.output.width, height=self.config.output.height)
    
    def render_mesh_visualization(self, output_path: str) -> None:
        """
        Рендеринг меша с использованием trimesh.
        
        Args:
            output_path: Путь для сохранения
        """
        mesh = self.mesh_builder.get_mesh()
        if mesh is None:
            raise ValueError("Меш не создан. Вызовите mesh_builder.create_mesh() сначала.")
        
        # Создание сцены
        scene = trimesh.Scene([mesh])
        
        # Настройка освещения
        scene.lights = self._create_trimesh_lights()
        
        # Рендеринг
        try:
            # Попытка использовать pyrender для качественного рендеринга
            image = scene.save_image(
                resolution=(self.config.output.width, self.config.output.height),
                visible=True
            )
            
            # Сохранение изображения
            if isinstance(image, bytes):
                with open(output_path, 'wb') as f:
                    f.write(image)
            else:
                image.save(output_path)
                
        except Exception as e:
            print(f"Ошибка при рендеринге с pyrender: {e}")
            # Fallback к matplotlib
            self.render_matplotlib(output_path)
    
    def create_animation(self, output_dir: str, frames: int = 36) -> List[str]:
        """
        Создать анимацию вращения 3D QR-кода.
        
        Args:
            output_dir: Директория для сохранения кадров
            frames: Количество кадров
            
        Returns:
            Список путей к созданным кадрам
        """
        os.makedirs(output_dir, exist_ok=True)
        frame_paths = []
        
        # Получение данных
        matrix = self.qr_generator.get_qr_matrix()
        height_map = self.qr_generator.create_height_map()
        glow_map = self.qr_generator.create_glow_map()
        
        # Создание координатных сеток
        height, width = matrix.shape
        x = np.arange(width)
        y = np.arange(height)
        X, Y = np.meshgrid(x, y)
        
        colors = self._create_color_map(matrix, glow_map)
        
        for frame in range(frames):
            angle = 2 * np.pi * frame / frames
            
            # Создание фигуры для каждого кадра
            fig = plt.figure(figsize=(
                self.config.output.width / self.config.output.dpi,
                self.config.output.height / self.config.output.dpi
            ), dpi=self.config.output.dpi)
            
            ax = fig.add_subplot(111, projection='3d')
            
            # Рендеринг поверхности
            surf = ax.plot_surface(
                X, Y, height_map,
                facecolors=colors,
                alpha=0.9,
                linewidth=0,
                antialiased=True,
                shade=True
            )
            
            # Настройка вида
            ax.view_init(elev=30, azim=np.degrees(angle))
            self._setup_matplotlib_appearance(ax, matrix.shape)
            
            # Сохранение кадра
            frame_path = os.path.join(output_dir, f"frame_{frame:03d}.png")
            plt.savefig(
                frame_path,
                dpi=self.config.output.dpi,
                bbox_inches='tight',
                facecolor='black',
                edgecolor='none'
            )
            plt.close()
            
            frame_paths.append(frame_path)
        
        return frame_paths
    
    def _create_color_map(self, matrix: np.ndarray, glow_map: np.ndarray) -> np.ndarray:
        """
        Создать цветовую карту для matplotlib.
        
        Args:
            matrix: Матрица QR-кода
            glow_map: Карта свечения
            
        Returns:
            Массив цветов RGBA
        """
        height, width = matrix.shape
        colors = np.zeros((height, width, 4))
        
        primary_rgb = self.config.get_primary_color_rgb()
        inner_rgb = self.config.get_inner_color_rgb()
        
        for i in range(height):
            for j in range(width):
                if matrix[i, j]:
                    # Активный пиксель
                    glow_intensity = glow_map[i, j]
                    
                    # Смешивание цветов
                    color = self._blend_colors(primary_rgb, inner_rgb, glow_intensity)
                    colors[i, j] = [*color, 1.0]
                else:
                    # Неактивный пиксель
                    colors[i, j] = [0.1, 0.1, 0.1, 0.3]
        
        return colors
    
    def _create_plotly_colors(self, matrix: np.ndarray, glow_map: np.ndarray) -> np.ndarray:
        """
        Создать цветовую карту для Plotly.
        
        Args:
            matrix: Матрица QR-кода
            glow_map: Карта свечения
            
        Returns:
            Массив значений для цветовой карты
        """
        height, width = matrix.shape
        colors = np.zeros((height, width))
        
        for i in range(height):
            for j in range(width):
                if matrix[i, j]:
                    colors[i, j] = glow_map[i, j]
                else:
                    colors[i, j] = 0
        
        return colors
    
    def _create_custom_colorscale(self) -> List[List]:
        """
        Создать пользовательскую цветовую шкалу для Plotly.
        
        Returns:
            Цветовая шкала в формате Plotly
        """
        primary_hex = self.config.primary_color
        inner_hex = self.config.inner_color
        
        return [
            [0, 'rgb(20, 20, 20)'],      # Тёмный для неактивных пикселей
            [0.3, primary_hex],           # Основной цвет
            [0.7, inner_hex],            # Внутренний цвет
            [1, inner_hex]               # Максимальное свечение
        ]
    
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
    
    def _setup_matplotlib_lighting(self, ax: Axes3D) -> None:
        """
        Настроить освещение для matplotlib.
        
        Args:
            ax: 3D оси matplotlib
        """
        # Настройка источников света
        ax.computed_zorder = False
        
        # Установка цвета фона
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        
        ax.xaxis.pane.set_edgecolor('gray')
        ax.yaxis.pane.set_edgecolor('gray')
        ax.zaxis.pane.set_edgecolor('gray')
        
        ax.xaxis.pane.set_alpha(0.1)
        ax.yaxis.pane.set_alpha(0.1)
        ax.zaxis.pane.set_alpha(0.1)
    
    def _setup_matplotlib_appearance(self, ax: Axes3D, matrix_shape: Tuple[int, int]) -> None:
        """
        Настроить внешний вид matplotlib графика.
        
        Args:
            ax: 3D оси matplotlib
            matrix_shape: Размеры матрицы QR-кода
        """
        height, width = matrix_shape
        
        # Настройка осей
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.set_zlim(0, self.config.settings_3d.height * 1.2)
        
        # Настройка меток
        ax.set_xlabel('X', color='white')
        ax.set_ylabel('Y', color='white')
        ax.set_zlabel('Height', color='white')
        
        # Настройка цветов осей
        ax.tick_params(colors='white')
        
        # Настройка вида
        ax.view_init(elev=30, azim=45)
        
        # Скрытие сетки
        ax.grid(False)
        
        # Настройка фона
        ax.xaxis.set_pane_color((0, 0, 0, 1))
        ax.yaxis.set_pane_color((0, 0, 0, 1))
        ax.zaxis.set_pane_color((0, 0, 0, 1))
    
    def _create_trimesh_lights(self) -> List:
        """
        Создать источники света для trimesh.
        
        Returns:
            Список источников света
        """
        lights = []
        
        # Основной направленный свет
        main_light = trimesh.scene.lighting.DirectionalLight(
            color=[255, 255, 255, 255],
            intensity=self.config.lighting.diffuse
        )
        lights.append(main_light)
        
        # Заполняющий свет
        fill_light = trimesh.scene.lighting.DirectionalLight(
            color=[100, 100, 150, 255],
            intensity=self.config.lighting.ambient
        )
        lights.append(fill_light)
        
        return lights
    
    def render_all_formats(self, base_path: str) -> Dict[str, str]:
        """
        Рендеринг во всех указанных форматах.
        
        Args:
            base_path: Базовый путь без расширения
            
        Returns:
            Словарь с путями к созданным файлам
        """
        output_files = {}
        
        for fmt in self.config.output.format:
            if fmt == 'png':
                output_path = f"{base_path}.png"
                self.render_matplotlib(output_path)
                output_files['png'] = output_path
                
            elif fmt == 'html':
                output_path = f"{base_path}.html"
                self.render_plotly(output_path, interactive=True)
                output_files['html'] = output_path
                
            elif fmt in ['obj', 'ply', 'stl']:
                output_path = f"{base_path}.{fmt}"
                self.mesh_builder.save_mesh(output_path, fmt)
                output_files[fmt] = output_path
        
        return output_files
    
    def get_render_info(self) -> Dict[str, Any]:
        """
        Получить информацию о рендеринге.
        
        Returns:
            Словарь с информацией
        """
        return {
            'output_formats': self.config.output.format,
            'resolution': (self.config.output.width, self.config.output.height),
            'dpi': self.config.output.dpi,
            'lighting': {
                'ambient': self.config.lighting.ambient,
                'diffuse': self.config.lighting.diffuse,
                'specular': self.config.lighting.specular,
                'position': self.config.lighting.position
            },
            '3d_settings': {
                'height': self.config.settings_3d.height,
                'glow_intensity': self.config.settings_3d.glow_intensity,
                'resolution': self.config.settings_3d.resolution
            }
        }
    
    def __str__(self) -> str:
        """Строковое представление рендерера."""
        return f"Renderer(formats={self.config.output.format})"
    
    def __repr__(self) -> str:
        """Подробное строковое представление."""
        return f"Renderer(config={self.config})"