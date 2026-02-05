# homepage.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint
from PyQt5.QtGui import QPixmap, QPainter
from pathlib import Path
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl

# Paths
asset_base = Path(__file__).parent.parent
assets_dir = asset_base / "assets"
sounds_dir = asset_base / "sounds"
bg_image = assets_dir / "homepage.png"
title_image = assets_dir / "Title.png"
chibi_image = assets_dir / "catgirl_chibi.png"


class ParallaxBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.offset = 0
        self.direction = 1

        if bg_image.exists():
            self.original_pixmap = QPixmap(str(bg_image))
        else:
            self.original_pixmap = QPixmap(1920, 1080)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()

        speed = 0.4
        travel_distance = 500

        self.offset += speed * self.direction

        if self.offset >= travel_distance:
            self.offset = travel_distance
            self.direction = -1
        elif self.offset <= 0:
            self.offset = 0
            self.direction = 1

        parallax_x = -400 + (self.offset * 0.7)
        parallax_y = -400 + (self.offset * 0.5)

        scaled = self.original_pixmap.scaled(
            w + 800, h + 800,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        painter.drawPixmap(int(parallax_x), int(parallax_y), scaled)


class HomePage(QWidget):
    def __init__(self, stack, sound_player):
        super().__init__()
        self.stack = stack
        self.sounds = sound_player

        # Background
        self.bg = ParallaxBackground(self)
        self.bg.setGeometry(self.rect())
        self.bg.lower()

        # Main layout with more top/bottom space to prevent cropping
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 120, 80, 120)  # Increased top/bottom to avoid crop


        # === FLOATING TITLE IMAGE ===
        self.title_label = QLabel()
        if title_image.exists():
            pix = QPixmap(str(title_image)).scaled(
                700, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.title_label.setPixmap(pix)
        else:
            self.title_label.setText("Kikyuu's\nMarvel Rivals Tools")
            self.title_label.setStyleSheet("color: #d896ff; font-size: 52px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        # Slower, gentler floating animation (8 seconds, 30px up/down)
        self.title_float = QPropertyAnimation(self.title_label, b"pos")
        self.title_float.setDuration(8000)  # Much slower
        self.title_float.setLoopCount(-1)
        self.title_float.setEasingCurve(QEasingCurve.InOutSine)

        # Buttons
        options = [
            ("Hero Team Randomizer", lambda: self.parent().parent().go_to_page(1)),
            ("Rivals Bingo", lambda: self.parent().parent().go_to_page(2)),
            ("Coaching", lambda: self.parent().parent().go_to_page(3))
        ]

        for text, func in options:
            btn = QPushButton(text)
            btn.setFixedHeight(100)
            btn.setCursor(Qt.PointingHandCursor)
            btn.play_hover_sound = True
            btn.installEventFilter(self)

            def make_click_handler(f=func):
                def handler():
                    self.sounds.play_click()
                    f()
                return handler

            btn.clicked.connect(make_click_handler())

            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #e1bee7, stop:0.5 #ce93d8, stop:1 #ba68c8);
                    color: #4a148c;
                    font-size: 34px;
                    font-weight: bold;
                    font-family: "Segoe UI", 'Segoe UI', sans-serif;
                    border: 3px solid #fff0ff;
                    border-radius: 28px;
                    padding: 15px;
                    margin: 8px 60px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #f3e5f5, stop:1 #e1bee7);
                    border: 4px solid #ffebff;
                    box-shadow: 0 15px 35px rgba(186, 104, 200, 0.4);
                    transform: translateY(-8px);
                }
                QPushButton:pressed {
                    background: #ce93d8;
                    transform: translateY(4px);
                }
            """)
            layout.addWidget(btn)

        layout.addStretch()

        # Chibi
        self.chibi = QLabel(self)
        if chibi_image.exists():
            chibi_pix = QPixmap(str(chibi_image)).scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.chibi.setPixmap(chibi_pix)
        self.chibi.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        self.chibi.raise_()

        self.chibi_float = QPropertyAnimation(self.chibi, b"pos")
        self.chibi_float.setDuration(4000)
        self.chibi_float.setLoopCount(-1)
        self.chibi_float.setEasingCurve(QEasingCurve.SineCurve)

        QTimer.singleShot(200, self.start_animations)

    def eventFilter(self, obj, event):
        if event.type() == event.Enter and hasattr(obj, "play_hover_sound"):
            self.sounds.play_hover()
        return super().eventFilter(obj, event)

    def start_animations(self):
        # Title: slow float up/down, shifted right for balance
        base_pos = self.title_label.pos()
        offset_x = -20  # Move title slightly right
        self.title_label.move(base_pos.x() + offset_x, base_pos.y())

        self.title_float.setKeyValues([
            (0.0, QPoint(base_pos.x() + offset_x, base_pos.y())),
            (0.5, QPoint(base_pos.x() + offset_x, base_pos.y() - 30)),
            (1.0, QPoint(base_pos.x() + offset_x, base_pos.y()))
        ])
        self.title_float.start()

        # Chibi float
        margin = 30
        base_x = self.width() - 100 - margin
        base_y = self.height() - 100 - margin
        self.chibi.move(base_x, base_y)

        self.chibi_float.setKeyValues([
            (0.0, QPoint(base_x, base_y)),
            (0.25, QPoint(base_x + 5, base_y - 10)),
            (0.5, QPoint(base_x, base_y - 15)),
            (0.75, QPoint(base_x - 5, base_y - 10)),
            (1.0, QPoint(base_x, base_y))
        ])
        self.chibi_float.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.setGeometry(self.rect())

        # Re-center title with right offset on resize
        if hasattr(self, 'title_label'):
            title_w = self.title_label.width()
            new_x = (self.width() - title_w) // 2 + 40  # +40px shift right
            current_y = self.title_label.y()
            self.title_label.move(new_x, current_y)

        # Chibi pinned
        if self.chibi.pixmap():
            self.chibi.resize(180, 180)
            margin = 30
            self.chibi.move(
                self.width() - 100 - margin,
                self.height() - 100 - margin
            )

        for child in self.findChildren(QWidget):
            if child != self.bg:
                child.raise_()