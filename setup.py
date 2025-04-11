#!/usr/bin/env python
"""
OCR盒子安装脚本

用于安装OCR盒子应用程序
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ocr_box",
    version="1.0.0",
    author="OCR盒子开发团队",
    description="桌面OCR识别工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ocr_box",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyQt5>=5.15.0",
        "pyautogui>=0.9.52",
        "pytesseract>=0.3.8",
        "pillow>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ocr_box=src.app:run_app",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["icon/*.png"],
    },
) 