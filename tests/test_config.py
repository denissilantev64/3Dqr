"""
Тесты для модуля конфигурации.
"""

import unittest
import tempfile
import os
import json
import sys

# Добавление src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config, QRSettings, Settings3D, OutputSettings, LightingSettings


class TestConfig(unittest.TestCase):
    """Тесты для класса Config."""
    
    def test_default_config(self):
        """Тест создания конфигурации по умолчанию."""
        config = Config()
        
        self.assertEqual(config.primary_color, "#0066cc")
        self.assertEqual(config.inner_color, "#ff3366")
        self.assertEqual(config.text, "Hello, 3D QR World!")
        self.assertIsInstance(config.qr_settings, QRSettings)
        self.assertIsInstance(config.settings_3d, Settings3D)
        self.assertIsInstance(config.output, OutputSettings)
        self.assertIsInstance(config.lighting, LightingSettings)
    
    def test_color_conversion(self):
        """Тест преобразования цветов."""
        config = Config(primary_color="#ff0000", inner_color="#00ff00")
        
        primary_rgb = config.get_primary_color_rgb()
        inner_rgb = config.get_inner_color_rgb()
        
        self.assertEqual(primary_rgb, (1.0, 0.0, 0.0))
        self.assertEqual(inner_rgb, (0.0, 1.0, 0.0))
    
    def test_color_rgba(self):
        """Тест получения RGBA цветов."""
        config = Config(primary_color="#ff0000")
        
        rgba = config.get_primary_color_rgba(0.5)
        self.assertEqual(rgba, (1.0, 0.0, 0.0, 0.5))
    
    def test_invalid_color(self):
        """Тест обработки неверного цвета."""
        config = Config(primary_color="invalid")
        
        with self.assertRaises(ValueError):
            config.get_primary_color_rgb()
    
    def test_validation(self):
        """Тест валидации конфигурации."""
        # Валидная конфигурация
        config = Config()
        errors = config.validate()
        self.assertEqual(len(errors), 0)
        
        # Невалидная конфигурация
        config.text = ""
        config.settings_3d.height = -1
        errors = config.validate()
        self.assertGreater(len(errors), 0)
    
    def test_save_load(self):
        """Тест сохранения и загрузки конфигурации."""
        config = Config(
            primary_color="#123456",
            inner_color="#abcdef",
            text="Test QR Code"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config.save(temp_path)
            loaded_config = Config.load(temp_path)
            
            self.assertEqual(config.primary_color, loaded_config.primary_color)
            self.assertEqual(config.inner_color, loaded_config.inner_color)
            self.assertEqual(config.text, loaded_config.text)
        finally:
            os.unlink(temp_path)
    
    def test_from_dict(self):
        """Тест создания конфигурации из словаря."""
        data = {
            "primary_color": "#ff0000",
            "inner_color": "#00ff00",
            "text": "Test",
            "qr_settings": {"version": 2},
            "3d_settings": {"height": 1.0},
            "output": {"format": ["png"]},
            "lighting": {"ambient": 0.5}
        }
        
        config = Config.from_dict(data)
        
        self.assertEqual(config.primary_color, "#ff0000")
        self.assertEqual(config.qr_settings.version, 2)
        self.assertEqual(config.settings_3d.height, 1.0)


class TestQRSettings(unittest.TestCase):
    """Тесты для класса QRSettings."""
    
    def test_default_settings(self):
        """Тест настроек по умолчанию."""
        settings = QRSettings()
        
        self.assertEqual(settings.version, 1)
        self.assertEqual(settings.error_correction, "M")
        self.assertEqual(settings.box_size, 10)
        self.assertEqual(settings.border, 4)


class TestSettings3D(unittest.TestCase):
    """Тесты для класса Settings3D."""
    
    def test_default_settings(self):
        """Тест настроек по умолчанию."""
        settings = Settings3D()
        
        self.assertEqual(settings.height, 0.5)
        self.assertEqual(settings.base_thickness, 0.1)
        self.assertEqual(settings.glow_intensity, 0.8)
        self.assertEqual(settings.resolution, 100)
        self.assertTrue(settings.smooth_edges)


if __name__ == '__main__':
    unittest.main()