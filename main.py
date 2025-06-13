import ctypes
import os
import sys
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient


class GaoKaoCountdownWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口无边框和透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # 避免使用WindowStaysOnBottomHint,防止争夺底层
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        if os.name == 'nt':
            def set_window_pos():
                hwnd = self.winId().__int__()
                # 稍高于最底层的值
                ctypes.windll.user32.SetWindowPos(hwnd, 2, 0, 0, 0, 0, 0x0214)

            QTimer.singleShot(100, set_window_pos)
        else:
            QTimer.singleShot(100, self.lower)

        if sys.platform == 'darwin':
            self.setWindowFlag(Qt.WindowType.Widget, True)
        else:
            self.setWindowFlag(Qt.WindowType.Tool, True)

        self.setFixedSize(640, 50)

        # 设置高考日期（6月7日）
        self.gaokao_date = datetime(datetime.now().year, 6, 7)
        if datetime.now() > self.gaokao_date:
            self.gaokao_date = datetime(datetime.now().year + 1, 6, 7)

        # 创建UI
        self.init_ui()

        # 设置定时器每秒更新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000 * 60)

        # 初始位置（右下角）
        screen_geo = QApplication.primaryScreen().geometry()
        self.move((screen_geo.width() - self.width()) // 2, 0)

    def init_ui(self):
        # 主标签
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 640, 50)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: white")

        # 设置字体
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setBold(True)
        font.setPointSize(20)
        self.label.setFont(font)

        self.update_countdown()

    def update_countdown(self):
        now = datetime.now()
        delta = self.gaokao_date - now
        days = delta.days + 1

        if days < 0:
            text = "高考已结束!"
        else:
            text = f"距离{self.gaokao_date.year}年高考还有{days}天"

        self.label.setText(text)

    def paintEvent(self, event):
        """绘制半透明圆角矩形背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 创建渐变背景
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(68, 64, 60, 220))  # 钢蓝色
        gradient.setColorAt(1, QColor(28, 25, 23, 220))  # 午夜蓝

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(0, 0, 0, 0)))

        # 绘制圆角矩形
        painter.drawRoundedRect(self.rect(), 15, 15)

    # def mousePressEvent(self, event):
    #     """实现窗口拖动功能"""
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    #         event.accept()
    #
    # def mouseMoveEvent(self, event):
    #     """处理窗口拖动"""
    #     if event.buttons() == Qt.MouseButton.LeftButton:
    #         self.move(event.globalPosition().toPoint() - self.drag_position)
    #         event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = GaoKaoCountdownWidget()
    widget.show()
    sys.exit(app.exec())
