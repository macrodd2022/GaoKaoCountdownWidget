import ctypes
import os
import sys
import json
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient


class GaoKaoCountdownWidget(QWidget):
    def __init__(self, target: str, date: datetime):
        super().__init__()

        self.target = target
        self.date = date

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
        delta = self.date - now
        days = delta.days + 1

        if days < 0:
            text = f"{self.target}已结束!"
        else:
            text = f"距离{self.date.year}{self.target}还有{days}天"

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

    if not os.path.exists("./config.json"):
        target = "高考"
        date = datetime(datetime.now().year, 6, 7)
        if datetime.now() - date > timedelta(days=5):
            date = datetime(date.year + 1, 6, 7)

        target_text, ok = QInputDialog.getText(None, "输入目标", "目标（默认高考）")
        if ok and target_text:
            target = target_text[:8]

        date_text, ok = QInputDialog.getText(None, "输入时间", "时间（默认0607）")
        if ok and date_text:
            try:
                if not date_text.isdigit() or len(date_text) != 4:
                    raise ValueError
                date = datetime(datetime.now().year, int(date_text[:2]), int(date_text[2:]))
                if datetime.now() - date > timedelta(days=5):
                    date = datetime(date.year + 1, date.month, date.day)
            except ValueError:
                QMessageBox.critical(None, "错误", "时间格式无效", QMessageBox.StandardButton.Yes)
                sys.exit(0)

        config = {
            "target": target,
            "date": f"{date.month:02}{date.day:02}",
        }

        json.dump(config, open("./config.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)
        QMessageBox.information(None, "配置保存成功", "请不要移除本程序同目录下的config.json，除非你要重新修改配置。",
                                QMessageBox.StandardButton.Yes)

    else:
        try:
            config = json.load(open("./config.json", "r", encoding="utf-8"))
            target = config["target"]
            date = datetime(datetime.now().year, int(config["date"][:2]), int(config["date"][2:]))
            if datetime.now() - date > timedelta(days=5):
                date = datetime(date.year + 1, date.month, date.day)
        except (json.decoder.JSONDecodeError, KeyError, ValueError):
            QMessageBox.critical(None, "配置文件有误", "请移除本程序同目录下的config.json，再重新运行。",
                                 QMessageBox.StandardButton.Yes)
            sys.exit(0)
        QMessageBox.information(None, "正在使用配置文件", "如果你要重新修改配置，请移除本程序同目录下的config.json。",
                                QMessageBox.StandardButton.Yes)

    widget = GaoKaoCountdownWidget(target, date)
    widget.show()
    sys.exit(app.exec())
