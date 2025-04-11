import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap

class TransparentWindow(QWidget):
    """
    一个透明的、可拖动和调整大小的窗口, 用于选择OCR区域
    """
    def __init__(self, icon_dir="icon"):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 初始窗口大小和位置
        self.setGeometry(400, 300, 400, 300)
        
        # 调整窗口相关变量
        self.dragging = False
        self.resizing = False
        self.offset = QPoint()
        self.resize_start = QPoint()
        self.original_size = self.size()
        
        # 热区图标大小
        self.handle_size = 24
        
        # 鼠标悬停状态
        self.hover_drag = False
        self.hover_resize = False
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        
        # 图标目录
        self.icon_dir = icon_dir
        
        # 加载图标
        self.load_icons()
        
    def load_icons(self):
        """加载拖动和调整大小的图标"""
        drag_path = os.path.join(self.icon_dir, "drag_icon.png")
        resize_path = os.path.join(self.icon_dir, "resize_icon.png")
        
        self.drag_icon = QPixmap(drag_path)
        self.resize_icon = QPixmap(resize_path)
        
        # 如果图标文件不存在, 创建默认图标
        if self.drag_icon.isNull():
            self.drag_icon = self.create_drag_icon()
        
        if self.resize_icon.isNull():
            self.resize_icon = self.create_resize_icon()
        
    def create_drag_icon(self):
        """创建默认拖动图标"""
        pixmap = QPixmap(self.handle_size, self.handle_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(0, 120, 215), 2))
        painter.setBrush(QColor(0, 120, 215, 180))
        painter.drawRect(0, 0, self.handle_size, self.handle_size)
        painter.drawLine(4, 12, 20, 12)
        painter.drawLine(12, 4, 12, 20)
        painter.end()
        return pixmap
    
    def create_resize_icon(self):
        """创建默认调整大小图标"""
        pixmap = QPixmap(self.handle_size, self.handle_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(0, 120, 215), 2))
        painter.setBrush(QColor(0, 120, 215, 180))
        painter.drawRect(0, 0, self.handle_size, self.handle_size)
        # 绘制调整大小图标
        painter.drawLine(8, 16, 16, 16)
        painter.drawLine(16, 8, 16, 16)
        painter.end()
        return pixmap
        
    def paintEvent(self, event):
        """绘制窗口边框"""
        painter = QPainter(self)
        
        # 设置绘制属性
        pen = QPen(QColor(0, 120, 215), 2, Qt.SolidLine)
        painter.setPen(pen)
        
        # 绘制窗口主体(半透明背景, 方便用户看到边界)
        painter.setBrush(QColor(200, 200, 255, 30))  # 非常淡的蓝色, 几乎透明
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
        
        # 绘制左上角拖动图标(添加背景使其更明显)
        drag_bg_color = QColor(0, 120, 215, 150 if self.hover_drag else 80)  # 鼠标悬停时更亮
        drag_rect = QRect(0, 0, self.handle_size, self.handle_size)
        painter.fillRect(drag_rect, drag_bg_color)
        painter.drawPixmap(0, 0, self.drag_icon)
        
        # 绘制右下角调整大小图标(添加背景使其更明显)
        resize_bg_color = QColor(0, 120, 215, 150 if self.hover_resize else 80)  # 鼠标悬停时更亮
        resize_rect = QRect(self.width() - self.handle_size, self.height() - self.handle_size, 
                            self.handle_size, self.handle_size)
        painter.fillRect(resize_rect, resize_bg_color)
        painter.drawPixmap(self.width() - self.handle_size, self.height() - self.handle_size, self.resize_icon)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            
            # 检查是否在右下角调整大小的区域
            if self.is_on_resize_area(pos):
                self.resizing = True
                self.resize_start = event.globalPos()
                self.original_size = self.size()
            # 检查是否在左上角拖动区域
            elif self.is_on_drag_area(pos):
                self.dragging = True
                self.offset = event.pos()
            # 如果点击在窗口其他区域, 也允许拖动
            else:
                self.dragging = True
                self.offset = event.pos()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        pos = event.pos()
        
        # 更新鼠标悬停状态
        old_hover_drag = self.hover_drag
        old_hover_resize = self.hover_resize
        
        self.hover_drag = self.is_on_drag_area(pos)
        self.hover_resize = self.is_on_resize_area(pos)
        
        # 如果悬停状态改变, 重绘窗口
        if old_hover_drag != self.hover_drag or old_hover_resize != self.hover_resize:
            self.update()
        
        # 处理拖动和调整大小
        if self.resizing and event.buttons() & Qt.LeftButton:
            # 计算鼠标移动的差值
            delta = event.globalPos() - self.resize_start
            
            # 调整窗口大小
            new_width = max(100, self.original_size.width() + delta.x())
            new_height = max(100, self.original_size.height() + delta.y())
            
            self.resize(new_width, new_height)
        
        elif self.dragging and event.buttons() & Qt.LeftButton:
            # 移动窗口位置
            self.move(event.globalPos() - self.offset)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.resizing = False
    
    def is_on_resize_area(self, pos):
        """判断是否在右下角调整大小的区域"""
        # 增大判断区域以便于操作
        return (self.width() - self.handle_size - 5 <= pos.x() <= self.width() and 
                self.height() - self.handle_size - 5 <= pos.y() <= self.height())
    
    def is_on_drag_area(self, pos):
        """判断是否在左上角拖动区域"""
        # 增大判断区域以便于操作
        return (0 <= pos.x() <= self.handle_size + 5 and 
                0 <= pos.y() <= self.handle_size + 5)

    def enterEvent(self, event):
        """鼠标进入窗口事件"""
        # 设置光标为箭头形状
        self.setCursor(Qt.ArrowCursor)
        
    def leaveEvent(self, event):
        """鼠标离开窗口事件"""
        # 重置悬停状态
        self.hover_drag = False
        self.hover_resize = False
        self.update() 