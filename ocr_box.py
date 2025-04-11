#!/usr/bin/env python
"""
OCR盒子启动脚本

这是OCR盒子程序的主入口点, 运行此脚本启动应用
"""
import sys
from src.app import run_app

if __name__ == "__main__":
    sys.exit(run_app()) 