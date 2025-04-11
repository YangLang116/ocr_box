"""
OCR盒子应用程序主模块
"""
import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def run_app():
    """运行OCR盒子应用程序"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(run_app()) 