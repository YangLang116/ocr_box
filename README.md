# OCR盒子

OCR盒子是一个桌面应用程序, 可以在屏幕上选定区域进行实时OCR文字识别, 并根据识别结果执行自动化操作。

## 功能特点

1. **OCR区域设置**：通过透明悬浮窗口设置屏幕上的OCR识别区域
2. **定时文字提取**：定时对选定区域进行OCR识别, 时间间隔可配置
3. **自动化操作**：根据识别的文字内容执行自定义的键盘和鼠标操作
4. **Tesseract路径配置**：优先从系统PATH中自动检测Tesseract路径, 也可手动指定

## 项目结构

```
ocr_box/
├── icon/                   # 图标文件目录
│   ├── drag_icon.png       # 拖动图标
│   └── resize_icon.png     # 调整大小图标
├── src/                    # 源代码目录
│   ├── models/             # 模型模块(核心功能)
│   │   ├── __init__.py
│   │   ├── action_handler.py  # 动作处理器
│   │   ├── ocr_processor.py   # OCR处理器
│   │   ├── ocr_signals.py     # 信号类
│   │   └── transparent_window.py  # 透明窗口
│   ├── ui/                 # 用户界面模块
│   │   ├── __init__.py
│   │   └── main_window.py  # 主窗口
│   ├── utils/              # 工具模块
│   │   ├── __init__.py
│   │   ├── icon_creator.py # 图标创建工具
│   │   └── tesseract_finder.py  # Tesseract查找工具
│   ├── __init__.py
│   └── app.py              # 应用程序主模块
├── ocr_box.py              # 启动脚本
├── setup.py                # 安装脚本
├── requirements.txt        # 依赖项
└── README.md               # 项目说明
```

## 安装说明

### 依赖项

- Python 3.7+
- PyQt5
- pyautogui
- pytesseract
- Pillow

### 安装步骤

1. 克隆或下载本项目到本地

2. 安装所需依赖项
   ```
   pip install -r requirements.txt
   ```

3. 安装Tesseract OCR引擎
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - 请安装时勾选中文语言包支持
   - 建议将Tesseract添加到系统PATH环境变量中, 程序会自动检测

## 使用方法

1. 运行程序
   ```
   python ocr_box.py
   ```

2. Tesseract设置
   - 程序会自动尝试从系统PATH中查找Tesseract
   - 如果找到, 会显示已检测到的Tesseract路径
   - 如果未找到, 或需要使用其他版本, 可点击"浏览..."按钮手动指定

3. 使用界面
   - 点击"开启OCR"按钮启动OCR服务
   - 调整透明窗口位置和大小以选择OCR区域
   - 在间隔设置中调整OCR识别的时间间隔
   - OCR结果会实时显示在应用界面中

4. 自动化操作
   - 通过动作配置界面设置匹配关键字和自动操作参数
   - 可以设置要匹配的关键字、鼠标点击位置和自动输入的文本
   - 支持"获取当前位置"功能，可以直接获取鼠标当前位置作为点击坐标
   - 点击"测试动作"按钮可以立即测试配置的动作

## 自定义

OCR盒子提供了两种自定义方式：

1. **通过界面配置**：使用应用程序中的"动作配置"面板，可以直接设置关键字匹配和自动操作行为。
2. **通过代码修改**：高级用户可以修改 `src/models/action_handler.py` 文件，实现更复杂的匹配逻辑和操作行为。

## 开发说明

### 构建项目

可以使用以下命令将项目打包为安装包：

```
python setup.py sdist bdist_wheel
```

### 目录结构说明

- **models**: 包含核心功能模块, 如OCR处理、透明窗口等
- **ui**: 包含用户界面相关模块
- **utils**: 包含辅助工具, 如Tesseract查找等
