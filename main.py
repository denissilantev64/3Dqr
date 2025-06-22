#!/usr/bin/env python3
"""
Главный модуль для генерации 3D QR-кодов.

Использование:
    python main.py [опции]

Примеры:
    python main.py
    python main.py --config settings/custom.json
    python main.py --text "Мой QR-код" --primary-color "#ff0000"
    python main.py --help
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Добавление src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.qr_generator import QRGenerator
from src.mesh_builder import MeshBuilder
from src.renderer import Renderer


def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Генератор 3D QR-кодов с выпуклой структурой и внутренним свечением",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s
  %(prog)s --config settings/blue_glow.json
  %(prog)s --text "https://example.com" --primary-color "#0066cc"
  %(prog)s --text "Hello World" --output-dir custom_output
  %(prog)s --formats png html obj --resolution 150
        """
    )
    
    # Основные параметры
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='settings/default.json',
        help='Путь к файлу конфигурации (по умолчанию: settings/default.json)'
    )
    
    parser.add_argument(
        '--text', '-t',
        type=str,
        help='Текст для QR-кода (переопределяет значение из конфигурации)'
    )
    
    parser.add_argument(
        '--primary-color',
        type=str,
        help='Основной цвет в формате HEX (например, #0066cc)'
    )
    
    parser.add_argument(
        '--inner-color',
        type=str,
        help='Внутренний цвет свечения в формате HEX (например, #ff3366)'
    )
    
    # Параметры вывода
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='output',
        help='Директория для сохранения результатов (по умолчанию: output)'
    )
    
    parser.add_argument(
        '--filename', '-f',
        type=str,
        help='Имя выходного файла без расширения'
    )
    
    parser.add_argument(
        '--formats',
        nargs='+',
        choices=['png', 'html', 'obj', 'ply', 'stl'],
        help='Форматы для экспорта (по умолчанию из конфигурации)'
    )
    
    # 3D параметры
    parser.add_argument(
        '--height',
        type=float,
        help='Высота выпуклых элементов'
    )
    
    parser.add_argument(
        '--glow-intensity',
        type=float,
        help='Интенсивность внутреннего свечения (0.0-2.0)'
    )
    
    parser.add_argument(
        '--resolution',
        type=int,
        help='Разрешение 3D меша'
    )
    
    # Дополнительные опции
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Подробный вывод'
    )
    
    parser.add_argument(
        '--no-mesh',
        action='store_true',
        help='Не создавать 3D меш (только 2D рендеринг)'
    )
    
    parser.add_argument(
        '--animation',
        action='store_true',
        help='Создать анимацию вращения'
    )
    
    parser.add_argument(
        '--frames',
        type=int,
        default=36,
        help='Количество кадров для анимации (по умолчанию: 36)'
    )
    
    return parser.parse_args()


def load_config(args):
    """Загрузка и настройка конфигурации."""
    try:
        config = Config.load(args.config)
        if args.verbose:
            print(f"✓ Конфигурация загружена из: {args.config}")
    except FileNotFoundError:
        print(f"⚠ Файл конфигурации не найден: {args.config}")
        print("Использование настроек по умолчанию...")
        config = Config()
    
    # Переопределение параметров из командной строки
    if args.text:
        config.text = args.text
    
    if args.primary_color:
        config.primary_color = args.primary_color
    
    if args.inner_color:
        config.inner_color = args.inner_color
    
    if args.filename:
        config.output.filename = args.filename
    
    if args.formats:
        config.output.format = args.formats
    
    if args.height:
        config.settings_3d.height = args.height
    
    if args.glow_intensity:
        config.settings_3d.glow_intensity = args.glow_intensity
    
    if args.resolution:
        config.settings_3d.resolution = args.resolution
    
    return config


def validate_config(config, verbose=False):
    """Валидация конфигурации."""
    errors = config.validate()
    
    if errors:
        print("❌ Ошибки в конфигурации:")
        for error in errors:
            print(f"   • {error}")
        return False
    
    if verbose:
        print("✓ Конфигурация валидна")
    
    return True


def create_output_directory(output_dir, verbose=False):
    """Создание выходной директории."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    if verbose:
        print(f"✓ Выходная директория: {output_dir}")


def generate_qr_code(config, verbose=False):
    """Генерация QR-кода."""
    if verbose:
        print("🔄 Генерация QR-кода...")
    
    qr_generator = QRGenerator(config)
    qr_generator.generate_qr_matrix()
    
    if verbose:
        info = qr_generator.get_info()
        print(f"✓ QR-код сгенерирован:")
        print(f"   • Размер матрицы: {info['matrix_size']}")
        print(f"   • Активных модулей: {info['active_modules']}")
        print(f"   • Коэффициент заполнения: {info['fill_ratio']:.2%}")
        print(f"   • Версия: {info['version']}")
        print(f"   • Уровень коррекции: {info['error_correction']}")
    
    return qr_generator


def create_3d_mesh(config, qr_generator, verbose=False):
    """Создание 3D меша."""
    if verbose:
        print("🔄 Создание 3D меша...")
    
    mesh_builder = MeshBuilder(config, qr_generator)
    mesh_builder.create_mesh()
    
    if verbose:
        info = mesh_builder.get_mesh_info()
        print(f"✓ 3D меш создан:")
        print(f"   • Вершин: {info.get('vertex_count', 0)}")
        print(f"   • Граней: {info.get('face_count', 0)}")
        print(f"   • Объём: {info.get('volume', 0):.3f}")
        print(f"   • Площадь поверхности: {info.get('surface_area', 0):.3f}")
        print(f"   • Водонепроницаемый: {info.get('is_watertight', False)}")
    
    return mesh_builder


def render_outputs(config, qr_generator, mesh_builder, output_dir, verbose=False):
    """Рендеринг выходных файлов."""
    if verbose:
        print("🔄 Рендеринг выходных файлов...")
    
    renderer = Renderer(config, qr_generator, mesh_builder)
    
    base_path = os.path.join(output_dir, config.output.filename)
    output_files = renderer.render_all_formats(base_path)
    
    if verbose:
        print("✓ Файлы созданы:")
        for fmt, path in output_files.items():
            file_size = os.path.getsize(path) / 1024  # KB
            print(f"   • {fmt.upper()}: {path} ({file_size:.1f} KB)")
    
    return output_files


def create_animation(config, qr_generator, output_dir, frames, verbose=False):
    """Создание анимации."""
    if verbose:
        print(f"🔄 Создание анимации ({frames} кадров)...")
    
    # Создание временного mesh_builder для анимации
    mesh_builder = MeshBuilder(config, qr_generator)
    renderer = Renderer(config, qr_generator, mesh_builder)
    
    animation_dir = os.path.join(output_dir, 'animation')
    frame_paths = renderer.create_animation(animation_dir, frames)
    
    if verbose:
        print(f"✓ Анимация создана: {len(frame_paths)} кадров в {animation_dir}")
    
    return frame_paths


def print_summary(config, output_files, execution_time, verbose=False):
    """Вывод итоговой информации."""
    print("\n" + "="*60)
    print("🎉 ГЕНЕРАЦИЯ ЗАВЕРШЕНА")
    print("="*60)
    
    print(f"📝 Текст QR-кода: {config.text}")
    print(f"🎨 Основной цвет: {config.primary_color}")
    print(f"✨ Внутренний цвет: {config.inner_color}")
    print(f"⏱️  Время выполнения: {execution_time:.2f} сек")
    
    print(f"\n📁 Созданные файлы:")
    for fmt, path in output_files.items():
        print(f"   • {fmt.upper()}: {path}")
    
    if verbose:
        print(f"\n⚙️  Параметры:")
        print(f"   • Высота 3D: {config.settings_3d.height}")
        print(f"   • Интенсивность свечения: {config.settings_3d.glow_intensity}")
        print(f"   • Разрешение: {config.settings_3d.resolution}")
        print(f"   • Сглаживание: {config.settings_3d.smooth_edges}")


def main():
    """Главная функция."""
    start_time = time.time()
    
    # Парсинг аргументов
    args = parse_arguments()
    
    try:
        # Загрузка конфигурации
        config = load_config(args)
        
        # Валидация
        if not validate_config(config, args.verbose):
            sys.exit(1)
        
        # Создание выходной директории
        create_output_directory(args.output_dir, args.verbose)
        
        # Генерация QR-кода
        qr_generator = generate_qr_code(config, args.verbose)
        
        # Создание 3D меша (если не отключено)
        if not args.no_mesh:
            mesh_builder = create_3d_mesh(config, qr_generator, args.verbose)
        else:
            mesh_builder = MeshBuilder(config, qr_generator)
            if args.verbose:
                print("⚠ Создание 3D меша пропущено")
        
        # Рендеринг
        output_files = render_outputs(
            config, qr_generator, mesh_builder, 
            args.output_dir, args.verbose
        )
        
        # Создание анимации (если запрошено)
        if args.animation:
            create_animation(
                config, qr_generator, args.output_dir, 
                args.frames, args.verbose
            )
        
        # Итоговая информация
        execution_time = time.time() - start_time
        print_summary(config, output_files, execution_time, args.verbose)
        
    except KeyboardInterrupt:
        print("\n❌ Операция прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()