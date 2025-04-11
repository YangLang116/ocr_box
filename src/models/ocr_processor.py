import time
import threading
import pytesseract
from PIL import ImageGrab, ImageEnhance, ImageFilter, Image
import cv2
import numpy as np
from src.models.action_handler import ActionHandler

class OCRProcessor:
    """
    OCR处理器, 负责截取屏幕区域并执行OCR识别, 根据识别结果执行自动操作
    """
    
    def __init__(self, signals, interval=1):
        """
        初始化OCR处理器
        
        Args:
            signals: OCRSignals实例, 用于线程间通信
            interval: OCR识别间隔(秒), 默认为2秒
        """
        self.signals = signals
        self.interval = interval
        self.enabled = False
        self.transparent_window = None
        self.stop_thread = False
        self.ocr_thread = None
        self.tesseract_path = None
        
        # OCR识别配置参数
        self.config = {
            "lang": "chi_sim",  # 语言设置
            "psm": 11,  # 页面分割模式: 6 - 假设为单一文本块
            "oem": 3,  # OCR引擎模式: 3 - 默认, 使用LSTM
            "image_preprocessing": {
                "enabled": True,  # 是否启用图像预处理
                "contrast": 1.5,  # 对比度增强倍数
                "sharpen": False,  # 是否锐化图像
                "denoise": False,  # 是否降噪
                "threshold": True,  # 是否进行二值化处理
                "scale_factor": 1.2,  # 放大倍数以提高识别准确率
            }
        }
    
    def set_tesseract_path(self, path):
        """设置Tesseract路径"""
        self.tesseract_path = path
        pytesseract.pytesseract.tesseract_cmd = path
    
    def set_language(self, lang):
        """
        设置OCR识别语言
        
        Args:
            lang: 语言代码，例如'chi_sim+eng'
        """
        self.config["lang"] = lang
    
    def set_config(self, config_dict):
        """
        更新OCR配置参数
        
        Args:
            config_dict: 包含OCR配置参数的字典
        """
        # 合并配置参数
        for key, value in config_dict.items():
            if key in self.config:
                if isinstance(value, dict) and isinstance(self.config[key], dict):
                    self.config[key].update(value)
                else:
                    self.config[key] = value
    
    def preprocess_image(self, image):
        """
        对图像进行预处理以提高OCR识别准确率
        
        Args:
            image: PIL.Image对象
            
        Returns:
            PIL.Image: 预处理后的图像
        """
        if not self.config["image_preprocessing"]["enabled"]:
            return image
        
        # 转换为OpenCV格式以便进行更复杂的图像处理
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 放大图像
        scale = self.config["image_preprocessing"]["scale_factor"]
        if scale > 1.0:
            img_cv = cv2.resize(img_cv, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # 降噪
        if self.config["image_preprocessing"]["denoise"]:
            img_cv = cv2.fastNlMeansDenoisingColored(img_cv, None, 10, 10, 7, 21)
        
        # 锐化
        if self.config["image_preprocessing"]["sharpen"]:
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            img_cv = cv2.filter2D(img_cv, -1, kernel)
        
        # 转回PIL格式
        image = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        
        # 增强对比度
        contrast = self.config["image_preprocessing"]["contrast"]
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        # 二值化处理
        if self.config["image_preprocessing"]["threshold"]:
            image = image.convert('L')  # 转换为灰度图
            image = image.point(lambda x: 0 if x < 128 else 255, '1')
        
        return image
    
    def start(self, transparent_window):
        """
        启动OCR识别
        
        Args:
            transparent_window: 透明窗口实例, 用于获取OCR区域
        """
        if not self.tesseract_path:
            self.signals.error_message.emit("未设置Tesseract路径, 无法启动OCR")
            return False
        
        self.transparent_window = transparent_window
        self.enabled = True
        self.stop_thread = False
        
        # 启动OCR线程
        self.ocr_thread = threading.Thread(target=self.ocr_job, daemon=True)
        self.ocr_thread.start()
        return True
    
    def stop(self):
        """停止OCR识别"""
        self.enabled = False
        self.stop_thread = True
        self.transparent_window = None
    
    def set_interval(self, interval):
        """设置OCR识别间隔"""
        self.interval = interval
    
    def ocr_job(self):
        """OCR识别线程"""
        while not self.stop_thread:
            if self.enabled and self.transparent_window:
                try:
                    # 获取透明窗口的位置和大小
                    rect = self.transparent_window.geometry()
                    
                    # 截取屏幕区域
                    screenshot = ImageGrab.grab(bbox=(rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height()))
                    
                    # 预处理图像
                    processed_image = self.preprocess_image(screenshot)
                    
                    # 构建Tesseract配置
                    custom_config = f'-l {self.config["lang"]} --psm {self.config["psm"]} --oem {self.config["oem"]}'
                    
                    # 执行OCR识别
                    try:
                        text = pytesseract.image_to_string(processed_image, config=custom_config)
                        self.signals.text_detected.emit(text)
                    except Exception as e:
                        self.signals.error_message.emit(f"OCR识别错误: {str(e)}")

                except Exception as e:
                    self.signals.error_message.emit(f"OCR处理错误: {str(e)}")
            
            # 等待指定间隔
            time.sleep(self.interval)