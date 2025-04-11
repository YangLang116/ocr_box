from PyQt5.QtCore import QObject, pyqtSignal

class OCRSignals(QObject):
    """
    用于OCR线程和主线程之间的信号通信
    
    Signals:
        text_detected: OCR识别到文本时发出的信号
        log_message: 记录日志消息的信号
        error_message: 记录错误消息的信号
    """
    text_detected = pyqtSignal(str)
    log_message = pyqtSignal(str)
    error_message = pyqtSignal(str)