"""
Установочный скрипт для 3D QR Code Generator.
"""

from setuptools import setup, find_packages
import os

# Чтение README файла
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Чтение requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="3dqr-generator",
    version="1.0.0",
    author="Denis Silantev",
    author_email="denissilantev64@example.com",
    description="Генератор трёхмерных QR-кодов с выпуклой структурой и внутренним свечением",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/denissilantev64/3Dqr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "docs": [
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "3dqr=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["settings/*.json", "settings/examples/*.json"],
    },
    keywords="qr-code 3d visualization mesh rendering plotly matplotlib",
    project_urls={
        "Bug Reports": "https://github.com/denissilantev64/3Dqr/issues",
        "Source": "https://github.com/denissilantev64/3Dqr",
        "Documentation": "https://github.com/denissilantev64/3Dqr#readme",
    },
)