"""
Модуль для работы с конфигурацией проекта.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional, Dict, Any


@dataclass
class QRSettings:
    """Настройки генерации QR-кода."""
    version: int = 1
    error_correction: str = "M"
    box_size: int = 10
    border: int = 4


@dataclass
class Settings3D:
    """Настройки 3D модели."""
    height: float = 0.5
    base_thickness: float = 0.1
    glow_intensity: float = 0.8
    resolution: int = 100
    smooth_edges: bool = True
    bevel_depth: float = 0.05


@dataclass
class OutputSettings:
    """Настройки вывода."""
    format: List[str] = None
    filename: str = "qr_3d"
    width: int = 800
    height: int = 600
    dpi: int = 150

    def __post_init__(self):
        if self.format is None:
            self.format = ["png", "html"]


@dataclass
class LightingSettings:
    """Настройки освещения."""
    ambient: float = 0.3
    diffuse: float = 0.7
    specular: float = 0.5
    position: List[float] = None

    def __post_init__(self):
        if self.position is None:
            self.position = [1, 1, 1]


class Config:
    """Класс для управления конфигурацией проекта."""
    
    def __init__(self, 
                 primary_color: str = "#0066cc",
                 inner_color: str = "#ff3366", 
                 text: str = "Hello, 3D QR World!",
                 qr_settings: Optional[QRSettings] = None,
                 settings_3d: Optional[Settings3D] = None,
                 output: Optional[OutputSettings] = None,
                 lighting: Optional[LightingSettings] = None):
        
        self.primary_color = primary_color
        self.inner_color = inner_color
        self.text = text
        self.qr_settings = qr_settings or QRSettings()
        self.settings_3d = settings_3d or Settings3D()
        self.output = output or OutputSettings()
        self.lighting = lighting or LightingSettings()

    @classmethod
    def load(cls, config_path: str) -> 'Config':
        """Загрузить конфигурацию из JSON файла."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Создать конфигурацию из словаря."""
        qr_settings = QRSettings(**data.get('qr_settings', {}))
        settings_3d = Settings3D(**data.get('3d_settings', {}))
        output = OutputSettings(**data.get('output', {}))
        lighting = LightingSettings(**data.get('lighting', {}))
        
        return cls(
            primary_color=data.get('primary_color', "#0066cc"),
            inner_color=data.get('inner_color', "#ff3366"),
            text=data.get('text', "Hello, 3D QR World!"),
            qr_settings=qr_settings,
            settings_3d=settings_3d,
            output=output,
            lighting=lighting
        )

    def save(self, config_path: str) -> None:
        """Сохранить конфигурацию в JSON файл."""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        data = {
            'primary_color': self.primary_color,
            'inner_color': self.inner_color,
            'text': self.text,
            'qr_settings': asdict(self.qr_settings),
            '3d_settings': asdict(self.settings_3d),
            'output': asdict(self.output),
            'lighting': asdict(self.lighting)
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать конфигурацию в словарь."""
        return {
            'primary_color': self.primary_color,
            'inner_color': self.inner_color,
            'text': self.text,
            'qr_settings': asdict(self.qr_settings),
            '3d_settings': asdict(self.settings_3d),
            'output': asdict(self.output),
            'lighting': asdict(self.lighting)
        }

    def get_primary_color_rgb(self) -> Tuple[float, float, float]:
        """Получить основной цвет в формате RGB (0-1)."""
        return self._hex_to_rgb(self.primary_color)

    def get_inner_color_rgb(self) -> Tuple[float, float, float]:
        """Получить внутренний цвет в формате RGB (0-1)."""
        return self._hex_to_rgb(self.inner_color)

    def get_primary_color_rgba(self, alpha: float = 1.0) -> Tuple[float, float, float, float]:
        """Получить основной цвет в формате RGBA (0-1)."""
        rgb = self.get_primary_color_rgb()
        return (*rgb, alpha)

    def get_inner_color_rgba(self, alpha: float = 1.0) -> Tuple[float, float, float, float]:
        """Получить внутренний цвет в формате RGBA (0-1)."""
        rgb = self.get_inner_color_rgb()
        return (*rgb, alpha)

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
        """Преобразовать HEX цвет в RGB (0-1)."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError(f"Неверный формат цвета: {hex_color}")
        
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        
        return (r, g, b)

    def validate(self) -> List[str]:
        """Проверить корректность конфигурации."""
        errors = []
        
        # Проверка цветов
        try:
            self.get_primary_color_rgb()
        except ValueError as e:
            errors.append(f"Ошибка в primary_color: {e}")
        
        try:
            self.get_inner_color_rgb()
        except ValueError as e:
            errors.append(f"Ошибка в inner_color: {e}")
        
        # Проверка текста
        if not self.text or not self.text.strip():
            errors.append("Текст для QR-кода не может быть пустым")
        
        # Проверка 3D настроек
        if self.settings_3d.height <= 0:
            errors.append("Высота 3D модели должна быть больше 0")
        
        if self.settings_3d.resolution <= 0:
            errors.append("Разрешение должно быть больше 0")
        
        # Проверка форматов вывода
        valid_formats = {"png", "html", "obj", "ply", "stl"}
        for fmt in self.output.format:
            if fmt not in valid_formats:
                errors.append(f"Неподдерживаемый формат: {fmt}")
        
        return errors

    def __str__(self) -> str:
        """Строковое представление конфигурации."""
        return f"Config(text='{self.text[:30]}...', primary='{self.primary_color}', inner='{self.inner_color}')"

    def __repr__(self) -> str:
        """Подробное строковое представление."""
        return (f"Config(primary_color='{self.primary_color}', "
                f"inner_color='{self.inner_color}', "
                f"text='{self.text}', "
                f"qr_settings={self.qr_settings}, "
                f"settings_3d={self.settings_3d})")