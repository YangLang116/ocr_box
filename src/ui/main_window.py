import os
import time
from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QSpinBox,
    QTextEdit,
    QGroupBox,
    QFileDialog,
    QLineEdit,
    QCheckBox,
    QDoubleSpinBox,
    QComboBox,
)
from PyQt5.QtCore import Qt

from src.models.transparent_window import TransparentWindow
from src.models.ocr_signals import OCRSignals
from src.models.ocr_processor import OCRProcessor
from src.utils.tesseract_finder import TesseractFinder
from src.models.action_handler import ActionHandler


class MainWindow(QMainWindow):
    """OCR盒子主窗口"""

    def __init__(self):
        super().__init__()

        # 初始化组件
        self.transparent_window = None
        self.has_chinese_support = False
        
        # 初始化UI控件
        self.tesseract_path_edit = None
        self.language_combo = None
        self.preprocess_checkbox = None
        self.scale_spin = None
        self.contrast_spin = None
        self.sharpen_checkbox = None
        self.denoise_checkbox = None
        self.threshold_checkbox = None
        self.psm_combo = None
        self.toggle_button = None
        self.interval_spin = None
        self.result_text = None
        self.log_text = None

        # 查找Tesseract路径
        self.tesseract_path = TesseractFinder.find_tesseract_path()

        # 初始化信号
        self.signals = OCRSignals()
        self.signals.log_message.connect(self.log)
        self.signals.error_message.connect(self.log_error)
        self.signals.text_detected.connect(self.update_result_text)

        # 关键字处理器
        self.action_handler = ActionHandler(self.signals)

        # 初始化OCR处理器
        self.ocr_processor = OCRProcessor(self.signals)

        # 初始化UI
        self.init_ui()

        # 应用创建后检查Tesseract状态并记录日志
        self.init_tesseract()

    def init_tesseract(self):
        """初始化Tesseract设置"""
        if self.tesseract_path:
            self.ocr_processor.set_tesseract_path(self.tesseract_path)
            self.log(f"已自动检测到Tesseract: {self.tesseract_path}")
            # 检查中文支持
            self.update_language_support()
        else:
            self.log("未在系统路径中找到Tesseract, 请手动指定路径")

    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("OCR盒子")
        self.setGeometry(100, 100, 750, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # 创建各部分UI
        tesseract_group = self.create_tesseract_ui()
        ocr_settings_group = self.create_ocr_settings_ui()
        control_group = self.create_control_ui()
        action_config_ui = self.action_handler.create_config_ui()
        result_group = self.create_result_ui()
        log_group = self.create_log_ui()

        # 添加所有组件到主布局
        main_layout.addWidget(tesseract_group)
        main_layout.addWidget(ocr_settings_group)
        main_layout.addWidget(control_group)
        main_layout.addWidget(action_config_ui)
        main_layout.addWidget(result_group)
        main_layout.addWidget(log_group)

        central_widget.setLayout(main_layout)

    def create_tesseract_ui(self):
        """创建Tesseract路径设置UI"""
        tesseract_group = QGroupBox("Tesseract路径设置")
        tesseract_layout = QHBoxLayout()

        self.tesseract_path_edit = QLineEdit(self.tesseract_path)
        self.tesseract_path_edit.setReadOnly(True)

        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_tesseract)

        tesseract_layout.addWidget(QLabel("Tesseract路径:"))
        tesseract_layout.addWidget(self.tesseract_path_edit)
        tesseract_layout.addWidget(browse_button)
        tesseract_group.setLayout(tesseract_layout)
        
        return tesseract_group

    def log(self, message):
        """添加日志到日志窗口"""
        try:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            log_entry = f"[{current_time}] {message}"
            self.log_text.append(log_entry)
            # 自动滚动到底部
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except Exception:
            pass

    def log_error(self, message):
        """添加错误日志到日志窗口"""
        try:
            self.log(f"错误: {message}")
        except Exception:
            pass

    def update_result_text(self, text):
        """更新OCR结果显示(在主线程中调用)"""
        try:
            self.result_text.setText(text)
        except Exception as e:
            self.log_error(f"更新UI出错: {str(e)}")
        # 执行匹配逻辑
        self.action_handler.process_text(text)

    def browse_tesseract(self):
        """打开文件对话框选择Tesseract路径"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Tesseract可执行文件", "", "可执行文件 (*.exe);;所有文件 (*.*)"
        )

        if file_path:
            self.tesseract_path = file_path
            self.tesseract_path_edit.setText(file_path)
            self.ocr_processor.set_tesseract_path(file_path)
            self.log(f"Tesseract路径已更新: {file_path}")

            # 检查中文支持
            self.update_language_support()

    def update_interval(self, value):
        """更新OCR检测间隔"""
        self.ocr_processor.set_interval(value)
        self.log(f"OCR检测间隔已更新为 {value} 秒")

    def toggle_ocr(self):
        """切换OCR状态"""
        if self.toggle_button.isChecked():
            # 检查Tesseract路径
            if not self.tesseract_path or not os.path.exists(self.tesseract_path):
                self.log_error("无法找到Tesseract可执行文件, 请先设置正确的路径")
                self.toggle_button.setChecked(False)
                return

            self.toggle_button.setText("关闭OCR")
            self.start_ocr()
            self.log("OCR服务已启动")
        else:
            self.toggle_button.setText("开启OCR")
            self.stop_ocr()
            self.log("OCR服务已停止")

    def start_ocr(self):
        """启动OCR服务"""
        # 创建透明窗口
        if not self.transparent_window:
            self.transparent_window = TransparentWindow()
        self.transparent_window.show()

        # 启动OCR处理器
        self.ocr_processor.start(self.transparent_window)

    def stop_ocr(self):
        """停止OCR服务"""
        # 停止OCR处理器
        self.ocr_processor.stop()

        # 关闭透明窗口
        if self.transparent_window:
            self.transparent_window.hide()

    def update_language_support(self):
        """更新语言支持状态"""
        if not self.tesseract_path:
            return

        # 检测中文支持
        self.has_chinese_support = TesseractFinder.has_chinese_support(
            self.tesseract_path
        )

        # 更新UI
        if self.has_chinese_support:
            self.log("已检测到中文语言包支持")
        else:
            self.log_error("未检测到中文语言包，OCR识别将仅支持英文")

            # 获取所有支持的语言
            langs = TesseractFinder.check_tesseract_languages(self.tesseract_path)
            if langs:
                self.log(f"可用语言: {', '.join(langs)}")

            # 提供语言包安装建议
            self.log("如已安装中文语言包但未检测到, 可尝试手动选择中文语言")
            
        # 根据实际支持的语言启用/禁用语言选项
        for i in range(self.language_combo.count()):
            lang_code = self.language_combo.itemData(i)
            if not self.has_chinese_support and "chi" in lang_code:
                # 如果不支持中文但选项中包含中文，显示灰色提示
                self.language_combo.setItemText(i, self.language_combo.itemText(i) + " (未安装)")
            
        # 如果当前选择的语言不可用，自动切换到英文
        current_lang = self.language_combo.itemData(self.language_combo.currentIndex())
        if not self.has_chinese_support and "chi" in current_lang:
            # 找到"仅英文"选项
            for i in range(self.language_combo.count()):
                if self.language_combo.itemData(i) == "eng":
                    self.language_combo.setCurrentIndex(i)
                    self.update_language()
                    break

    def closeEvent(self, event):
        """窗口关闭时的处理"""
        try:
            self.stop_ocr()
            event.accept()
        except Exception:
            event.accept()

    def update_ocr_settings(self):
        """更新OCR设置"""
        try:
            # 获取PSM值
            psm_map = {0: 6, 1: 3, 2: 7, 3: 8, 4: 10, 5: 11}
            psm_value = psm_map.get(self.psm_combo.currentIndex(), 6)
            
            # 获取语言设置
            lang = self.language_combo.itemData(self.language_combo.currentIndex())
            
            # 获取当前设置
            config = {
                "lang": lang,
                "psm": psm_value,
                "oem": 3,  # 默认使用最佳引擎模式
                "image_preprocessing": {
                    "enabled": self.preprocess_checkbox.isChecked(),
                    "contrast": self.contrast_spin.value(),
                    "sharpen": self.sharpen_checkbox.isChecked(),
                    "denoise": self.denoise_checkbox.isChecked(),
                    "threshold": self.threshold_checkbox.isChecked(),
                    "scale_factor": self.scale_spin.value()
                }
            }
            
            # 更新OCR处理器配置
            self.ocr_processor.set_config(config)
            self.log("OCR设置已更新")
        except Exception as e:
            self.log_error(f"更新OCR设置出错: {str(e)}")
    
    def reset_ocr_settings(self):
        """重置OCR设置为默认值"""
        try:
            # 设置默认值
            self.preprocess_checkbox.setChecked(True)
            self.contrast_spin.setValue(1.5)
            self.sharpen_checkbox.setChecked(True)
            self.denoise_checkbox.setChecked(True)
            self.threshold_checkbox.setChecked(False)
            self.scale_spin.setValue(2.0)
            self.psm_combo.setCurrentIndex(0)  # 选择单一文本块模式
            
            # 重置语言设置（如果支持中文则设为中文+英文，否则只设为英文）
            if self.has_chinese_support:
                # 查找"中文+英文"选项
                for i in range(self.language_combo.count()):
                    if self.language_combo.itemData(i) == "chi_sim+eng":
                        self.language_combo.setCurrentIndex(i)
                        break
            else:
                # 查找"仅英文"选项
                for i in range(self.language_combo.count()):
                    if self.language_combo.itemData(i) == "eng":
                        self.language_combo.setCurrentIndex(i)
                        break
            
            # 更新设置
            self.update_ocr_settings()
            self.log("OCR设置已重置为默认值")
        except Exception as e:
            self.log_error(f"重置OCR设置出错: {str(e)}")

    def refresh_language_list(self):
        """刷新语言列表"""
        try:
            if not self.tesseract_path:
                self.log_error("请先设置Tesseract路径")
                return
            
            # 获取所有支持的语言
            langs = TesseractFinder.check_tesseract_languages(self.tesseract_path)
            if not langs:
                self.log_error("未检测到任何语言包，请检查Tesseract安装")
                return
            
            # 清空当前语言列表
            current_lang = self.language_combo.itemData(self.language_combo.currentIndex())
            self.language_combo.clear()
            
            # 基本选项
            self.language_combo.addItem("仅英文 (eng)", "eng")
            
            # 检查是否支持中文
            has_chi_sim = 'chi_sim' in langs
            has_chi_tra = 'chi_tra' in langs
            
            # 添加中文相关选项
            if has_chi_sim:
                self.language_combo.addItem("仅简体中文 (chi_sim)", "chi_sim")
                self.language_combo.addItem("简体中文+英文 (chi_sim+eng)", "chi_sim+eng")
            
            if has_chi_tra:
                self.language_combo.addItem("仅繁体中文 (chi_tra)", "chi_tra")
                self.language_combo.addItem("繁体中文+英文 (chi_tra+eng)", "chi_tra+eng")
            
            if has_chi_sim and has_chi_tra:
                self.language_combo.addItem("简繁中文+英文 (chi_sim+chi_tra+eng)", "chi_sim+chi_tra+eng")
            
            # 添加其他特殊语言
            other_langs = [lang for lang in langs if lang not in ['eng', 'chi_sim', 'chi_tra']]
            for lang in other_langs:
                self.language_combo.addItem(f"{lang}", lang)
                self.language_combo.addItem(f"{lang}+英文 ({lang}+eng)", f"{lang}+eng")
            
            # 尝试恢复之前的选择
            found = False
            for i in range(self.language_combo.count()):
                if self.language_combo.itemData(i) == current_lang:
                    self.language_combo.setCurrentIndex(i)
                    found = True
                    break
            
            # 如果没找到之前的语言，则使用默认值
            if not found:
                if has_chi_sim:
                    for i in range(self.language_combo.count()):
                        if self.language_combo.itemData(i) == "chi_sim+eng":
                            self.language_combo.setCurrentIndex(i)
                            break
                else:
                    self.language_combo.setCurrentIndex(0)  # 默认为英文
            
            self.update_language_support()
            self.log(f"已刷新语言列表，检测到{len(langs)}种语言")
        except Exception as e:
            self.log_error(f"刷新语言列表出错: {str(e)}")

    def update_language(self):
        """更新OCR语言"""
        selected_lang = self.language_combo.itemData(self.language_combo.currentIndex())
        self.ocr_processor.set_language(selected_lang)
        self.log(f"已更新OCR语言为: {selected_lang}")

    def create_ocr_settings_ui(self):
        """创建OCR设置面板UI"""
        ocr_settings_group = QGroupBox("OCR设置")
        ocr_settings_layout = QVBoxLayout()
        
        # 添加语言设置
        language_layout = self.create_language_settings_ui()
        ocr_settings_layout.addLayout(language_layout)
        
        # 添加图像预处理设置
        preprocess_layout = self.create_preprocessing_ui()
        ocr_settings_layout.addLayout(preprocess_layout)
        
        ocr_settings_group.setLayout(ocr_settings_layout)
        return ocr_settings_group

    def create_language_settings_ui(self):
        """创建语言设置UI"""
        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel("识别语言:"))
        
        # 创建下拉选择框
        self.language_combo = QComboBox()
        self.language_combo.addItem("仅英文 (eng)", "eng")
        self.language_combo.addItem("中文+英文 (chi_sim+eng)", "chi_sim+eng")
        self.language_combo.addItem("仅中文 (chi_sim)", "chi_sim")
        self.language_combo.addItem("繁体中文 (chi_tra)", "chi_tra")
        self.language_combo.addItem("简繁中文+英文 (chi_sim+chi_tra+eng)", "chi_sim+chi_tra+eng")
        
        # 根据当前语言设置选择下拉框选项
        current_lang = self.ocr_processor.config["lang"]
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_lang:
                self.language_combo.setCurrentIndex(i)
                break
        
        # 连接信号
        self.language_combo.currentIndexChanged.connect(self.update_language)
        
        language_layout.addWidget(self.language_combo)
        
        # 添加刷新语言按钮
        refresh_lang_btn = QPushButton("刷新语言列表")
        refresh_lang_btn.clicked.connect(self.refresh_language_list)
        language_layout.addWidget(refresh_lang_btn)
        
        return language_layout

    def create_preprocessing_ui(self):
        """创建图像预处理UI"""
        preprocess_layout = QVBoxLayout()
        
        # 启用预处理
        enable_layout = QHBoxLayout()
        self.preprocess_checkbox = QCheckBox("启用图像预处理")
        self.preprocess_checkbox.setChecked(self.ocr_processor.config["image_preprocessing"]["enabled"])
        self.preprocess_checkbox.toggled.connect(self.update_ocr_settings)
        enable_layout.addWidget(self.preprocess_checkbox)
        
        # 图像放大
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("图像放大倍数:"))
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(1.0, 4.0)
        self.scale_spin.setSingleStep(0.5)
        self.scale_spin.setValue(self.ocr_processor.config["image_preprocessing"]["scale_factor"])
        self.scale_spin.valueChanged.connect(self.update_ocr_settings)
        scale_layout.addWidget(self.scale_spin)
        
        # 对比度设置
        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(QLabel("对比度增强:"))
        self.contrast_spin = QDoubleSpinBox()
        self.contrast_spin.setRange(0.5, 3.0)
        self.contrast_spin.setSingleStep(0.1)
        self.contrast_spin.setValue(self.ocr_processor.config["image_preprocessing"]["contrast"])
        self.contrast_spin.valueChanged.connect(self.update_ocr_settings)
        contrast_layout.addWidget(self.contrast_spin)
        
        # 预处理选项
        options_layout = QHBoxLayout()
        
        # 锐化
        self.sharpen_checkbox = QCheckBox("图像锐化")
        self.sharpen_checkbox.setChecked(self.ocr_processor.config["image_preprocessing"]["sharpen"])
        self.sharpen_checkbox.toggled.connect(self.update_ocr_settings)
        options_layout.addWidget(self.sharpen_checkbox)
        
        # 降噪
        self.denoise_checkbox = QCheckBox("降噪")
        self.denoise_checkbox.setChecked(self.ocr_processor.config["image_preprocessing"]["denoise"])
        self.denoise_checkbox.toggled.connect(self.update_ocr_settings)
        options_layout.addWidget(self.denoise_checkbox)
        
        # 二值化
        self.threshold_checkbox = QCheckBox("二值化")
        self.threshold_checkbox.setChecked(self.ocr_processor.config["image_preprocessing"]["threshold"])
        self.threshold_checkbox.toggled.connect(self.update_ocr_settings)
        options_layout.addWidget(self.threshold_checkbox)
        
        # 引擎设置
        engine_layout = QHBoxLayout()
        
        # PSM设置
        engine_layout.addWidget(QLabel("页面分割模式:"))
        self.psm_combo = QComboBox()
        psm_options = [
            "6 - 单一文本块",
            "3 - 自动分割",
            "7 - 单行文本",
            "8 - 单词",
            "10 - 单字符",
            "11 - 稀疏文本"
        ]
        self.psm_combo.addItems(psm_options)
        
        # 设置当前PSM值
        psm_index_map = {6: 0, 3: 1, 7: 2, 8: 3, 10: 4, 11: 5}
        current_psm = self.ocr_processor.config["psm"]
        if current_psm in psm_index_map:
            self.psm_combo.setCurrentIndex(psm_index_map[current_psm])
        else:
            self.psm_combo.setCurrentIndex(0)  # 默认为单一文本块
            
        self.psm_combo.currentIndexChanged.connect(self.update_ocr_settings)
        engine_layout.addWidget(self.psm_combo)
        
        # 按钮行
        buttons_layout = QHBoxLayout()
        
        # 重置按钮
        reset_button = QPushButton("重置为默认设置")
        reset_button.clicked.connect(self.reset_ocr_settings)
        buttons_layout.addWidget(reset_button)
        
        # 添加所有布局到预处理布局
        preprocess_layout.addLayout(enable_layout)
        preprocess_layout.addLayout(scale_layout)
        preprocess_layout.addLayout(contrast_layout)
        preprocess_layout.addLayout(options_layout)
        preprocess_layout.addLayout(engine_layout)
        preprocess_layout.addLayout(buttons_layout)
        
        return preprocess_layout

    def create_control_ui(self):
        """创建控制面板UI"""
        control_group = QGroupBox("控制面板")
        control_layout = QHBoxLayout()

        self.toggle_button = QPushButton("开启OCR")
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_ocr)

        interval_label = QLabel("检测间隔(秒):")

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(self.ocr_processor.interval)
        self.interval_spin.valueChanged.connect(self.update_interval)

        control_layout.addWidget(self.toggle_button)
        control_layout.addWidget(interval_label)
        control_layout.addWidget(self.interval_spin)
        control_group.setLayout(control_layout)
        
        return control_group

    def create_result_ui(self):
        """创建OCR结果显示UI"""
        result_group = QGroupBox("OCR识别结果")
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        
        return result_group

    def create_log_ui(self):
        """创建操作日志UI"""
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        
        return log_group