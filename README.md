# 3D QR Code Generator

Генератор трёхмерных QR-кодов с выпуклой структурой и внутренним свечением.

![3D QR Code Example](https://via.placeholder.com/400x400/0066cc/ffffff?text=3D+QR+Code)

## Описание

Этот проект создаёт объёмные QR-коды на основе входного текста. QR-код формируется как трёхмерный куб с выпуклыми элементами и внутренним свечением, которое можно настроить через файл конфигурации.

## Особенности

- 🎨 Настраиваемые цвета (основной и внутреннее свечение)
- 📐 Выпуклая 3D структура QR-кода
- ✨ Эффект внутреннего свечения
- 🔧 Гибкая конфигурация через JSON
- 📊 Экспорт в различные форматы (PNG, HTML, OBJ, PLY)
- 🖥️ Интерактивная 3D визуализация

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/denissilantev64/3Dqr.git
cd 3Dqr
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

### Быстрый старт

```bash
python main.py
```

Программа использует настройки по умолчанию из файла `settings/default.json`.

### Настройка параметров

Отредактируйте файл `settings/default.json`:

```json
{
    "primary_color": "#0066cc",
    "inner_color": "#ff3366", 
    "text": "https://github.com/denissilantev64/3Dqr",
    "qr_settings": {
        "version": 1,
        "error_correction": "M",
        "box_size": 10,
        "border": 4
    },
    "3d_settings": {
        "height": 0.5,
        "base_thickness": 0.1,
        "glow_intensity": 0.8,
        "resolution": 100
    },
    "output": {
        "format": ["png", "html", "obj"],
        "filename": "qr_3d"
    }
}
```

### Параметры командной строки

```bash
# Использовать другой файл настроек
python main.py --config settings/custom.json

# Задать текст напрямую
python main.py --text "Ваш текст здесь"

# Задать цвета
python main.py --primary-color "#ff0000" --inner-color "#00ff00"

# Показать справку
python main.py --help
```

## Структура проекта

```
3Dqr/
├── src/
│   ├── __init__.py
│   ├── qr_generator.py      # Генерация QR-кода
│   ├── mesh_builder.py      # Создание 3D меша
│   ├── renderer.py          # Рендеринг и визуализация
│   └── config.py            # Работа с конфигурацией
├── settings/
│   ├── default.json         # Настройки по умолчанию
│   └── examples/            # Примеры конфигураций
├── output/                  # Выходные файлы (создаётся автоматически)
├── main.py                  # Точка входа
├── requirements.txt         # Зависимости Python
├── README.md               # Документация
└── .gitignore              # Игнорируемые файлы
```

## Примеры использования

### Создание QR-кода для URL

```python
from src.qr_generator import QRGenerator
from src.config import Config

config = Config.load('settings/default.json')
config.text = "https://example.com"
config.primary_color = "#0066cc"
config.inner_color = "#ff3366"

generator = QRGenerator(config)
generator.generate_and_save()
```

### Настройка 3D параметров

```python
config.settings_3d.height = 1.0  # Высота выпуклых элементов
config.settings_3d.glow_intensity = 0.9  # Интенсивность свечения
config.settings_3d.resolution = 150  # Разрешение меша
```

## Форматы экспорта

- **PNG** - Растровое изображение с рендером
- **HTML** - Интерактивная 3D модель (Plotly)
- **OBJ** - 3D модель для импорта в Blender/Maya
- **PLY** - 3D модель с цветами
- **STL** - Для 3D печати

## Требования

- Python 3.8+
- NumPy
- Matplotlib
- Plotly
- Pillow (PIL)
- QRCode
- Trimesh
- Open3D

## Лицензия

MIT License - см. файл LICENSE для деталей.

## Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## Поддержка

Если у вас есть вопросы или предложения, создайте [Issue](https://github.com/denissilantev64/3Dqr/issues) в репозитории.