"""
3D QR Code Generator

Модуль для создания трёхмерных QR-кодов с выпуклой структурой и внутренним свечением.
"""

__version__ = "1.0.0"
__author__ = "Denis Silantev"
__email__ = "denissilantev64@example.com"

from .qr_generator import QRGenerator
from .config import Config
from .mesh_builder import MeshBuilder
from .renderer import Renderer

__all__ = ['QRGenerator', 'Config', 'MeshBuilder', 'Renderer']