import pyautogui
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
)
from PyQt5.QtCore import Qt


class ActionHandler:
    """
    处理OCR识别文本的动作处理器
    负责根据识别的文本执行相应的自动化操作
    """

    def __init__(self, signals):
        self.signals = signals
        # 默认关键字和动作配置
        self.keyword = "测试"
        self.action_x = 1000
        self.action_y = 500
        self.action_text = "哈哈"

    def process_text(self, text):
        # 根据配置的关键字匹配文本
        if self.keyword in text:
            self.signals.log_message.emit(f"检测到关键词'{self.keyword}', 执行模拟操作")
            self.__perform_action()

    def __perform_action(self):
        """执行自动化操作(在主线程中调用)"""
        try:
            # 使用配置的坐标执行点击
            pyautogui.click(self.action_x, self.action_y)
            # 添加短暂延迟，确保点击后窗口已获得焦点
            import time

            time.sleep(0.5)
            # 对于中文等非ASCII文本，使用pyperclip+热键组合
            import pyperclip

            original_clipboard = pyperclip.paste()
            pyperclip.copy(self.action_text)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.2)
            pyperclip.copy(original_clipboard)
            # 按回车键
            time.sleep(0.2)
            pyautogui.press("enter")
            return True
        except Exception as e:
            self.signals.error_message.emit(f"执行操作出错: {str(e)}")
            return False

    def create_config_ui(self):
        """创建关键字和自动操作配置的UI视图"""
        # 创建配置分组
        config_group = QGroupBox("动作配置")
        config_layout = QVBoxLayout()

        # 关键字设置
        keyword_layout = QHBoxLayout()
        keyword_layout.addWidget(QLabel("关键字:"))
        self.keyword_edit = QLineEdit(self.keyword)
        self.keyword_edit.setPlaceholderText("输入要匹配的关键字")
        self.keyword_edit.textChanged.connect(self.update_keyword)
        keyword_layout.addWidget(self.keyword_edit)

        # 点击坐标设置
        coord_layout = QHBoxLayout()
        coord_layout.addWidget(QLabel("点击位置:"))

        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 3000)
        self.x_spin.setValue(self.action_x)
        self.x_spin.valueChanged.connect(self.update_action_x)

        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 3000)
        self.y_spin.setValue(self.action_y)
        self.y_spin.valueChanged.connect(self.update_action_y)

        coord_layout.addWidget(QLabel("X:"))
        coord_layout.addWidget(self.x_spin)
        coord_layout.addWidget(QLabel("Y:"))
        coord_layout.addWidget(self.y_spin)

        # 获取当前位置按钮
        self.get_pos_btn = QPushButton("获取当前位置")
        self.get_pos_btn.clicked.connect(self.get_current_position)
        coord_layout.addWidget(self.get_pos_btn)

        # 自动输入文本设置
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("自动输入:"))
        self.action_text_edit = QLineEdit(self.action_text)
        self.action_text_edit.setPlaceholderText("输入要自动填写的文本")
        self.action_text_edit.textChanged.connect(self.update_action_text)
        text_layout.addWidget(self.action_text_edit)

        # 测试按钮
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("测试动作")
        self.test_btn.clicked.connect(self.__perform_action)
        test_layout.addWidget(self.test_btn)

        # 添加所有布局到配置组
        config_layout.addLayout(keyword_layout)
        config_layout.addLayout(coord_layout)
        config_layout.addLayout(text_layout)
        config_layout.addLayout(test_layout)

        config_group.setLayout(config_layout)
        return config_group

    def update_keyword(self, text):
        """更新关键字配置"""
        self.keyword = text
        self.signals.log_message.emit(f"关键字已更新为: {text}")

    def update_action_x(self, value):
        """更新X坐标"""
        self.action_x = value

    def update_action_y(self, value):
        """更新Y坐标"""
        self.action_y = value

    def update_action_text(self, text):
        """更新自动输入的文本"""
        self.action_text = text

    def get_current_position(self):
        """获取当前鼠标位置"""
        try:
            # 延迟执行，让用户有时间将鼠标移动到目标位置
            self.signals.log_message.emit("3秒后获取鼠标位置, 请将鼠标移至目标位置...")
            import time

            time.sleep(3)

            # 获取当前鼠标位置
            x, y = pyautogui.position()

            # 更新UI控件
            self.x_spin.setValue(x)
            self.y_spin.setValue(y)

            self.signals.log_message.emit(f"已获取鼠标位置: X={x}, Y={y}")
        except Exception as e:
            self.signals.error_message.emit(f"获取鼠标位置失败: {str(e)}")
