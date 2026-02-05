# bingo.py
import random
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTextEdit
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QResizeEvent

# Initial phrases
default_bingo_phrases = [
    "Pulse cannon airball", "Keyboard warrior", "Magneto performs a gravitational L", "4 DPS", "Strategist asks for a swap",
    "Triple support", "Support ultimate is canceled", "Unfunny username", "5+ minute queue time", "Voice chat yapper",
    "Lord flexing", "'gg ez'", "Mechanically ungifted", "Klyntar domination", "Certified gooner skin", "Misinformation",
    "High testosterone hitscan", "Hero mirroring", "EOMM agent detected", "Voice changer", "TTV player", "Spidey main",
    "XLEK jr.", "Mid-ultimate voiceline death", "Pointless ultimate", "'No peel'", "Leaver/Disconnected", "Mystery heroes",
    "Less frames than OPM S3", "Payload princess", "Grey carpet (5+ losses)", "One trick pony", "Ban contrarian",
    "Surrender vote", "C9", "Terrible strange portal", "Quickplay demon", "Composition complaint", "'Report'", "'Avoid X'", "Blames the game",
    "Xbox 360 microphone"
]

# Bingo card class
class BingoCard(QWidget):

    # Constants
    cell_size = 120
    border_width = 2
    margin = 10

    # Constructor
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_page = parent
        self.marked = [[False for _ in range(5)] for _ in range(5)]
        self.marked[2][2] = True
        self.phrases = [["" for _ in range(5)] for _ in range(5)]
        self.phrases[2][2] = "FREE"

        total = 5 * self.cell_size + 2 * self.margin
        self.setFixedSize(total, total)
        self.setCursor(Qt.PointingHandCursor)

    # Set phrases
    def set_phrases(self, phrases_1d):
        idx = 0
        for r in range(5):
            for c in range(5):
                if r == 2 and c == 2:
                    continue
                self.phrases[r][c] = phrases_1d[idx]
                self.marked[r][c] = False
                idx += 1
        self.update()

    # Toggles a cell on the bingo card
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.x() - self.margin
            y = event.y() - self.margin
            if x >= 0 and y >= 0:
                col = x // self.cell_size
                row = y // self.cell_size
                if 0 <= row < 5 and 0 <= col < 5 and not (row == 2 and col == 2):
                    self.parent_page.sound_player.play_click()
                    self.marked[row][col] = not self.marked[row][col]
                    self.update()

    # Draws the bingo card
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        for r in range(5):
            for c in range(5):
                x = self.margin + c * self.cell_size
                y = self.margin + r * self.cell_size
                rect = (x, y, self.cell_size, self.cell_size)

                bg_color = "#e1bee7" if self.marked[r][c] else "white"
                painter.fillRect(*rect, QColor(bg_color))

                painter.setPen(QPen(QColor("#d8b4ff"), self.border_width))
                painter.drawRect(*rect)

                text = self.phrases[r][c]
                if not text:
                    continue

                painter.setPen(QColor("#ba68c8" if (r == 2 and c == 2) else "#4a148c"))
                font = painter.font()
                font.setBold(True)
                font.setPixelSize(18 if r == 2 and c == 2 else 14)
                painter.setFont(font)

                painter.drawText(
                    x + 8, y + 8, self.cell_size - 16, self.cell_size - 16,
                    Qt.AlignCenter | Qt.TextWordWrap,
                    text
                )

# Bingo page class
class BingoPage(QWidget):
    def __init__(self, stack, sound_player):
        super().__init__()
        self.stack = stack
        self.sound_player = sound_player

        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        # Background offset
        self.bg_offset = 0.0
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self.update)
        self.bg_timer.start(50)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 18, 20, 20)
        main_layout.setSpacing(12)

        # Back button
        back_row = QHBoxLayout()
        back_row.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(100, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #f3e8ff;
                color: #4a148c;
                font-size: 16px;
                font-weight: bold;
                border-radius: 20px;
                border: 3px solid #d8b4ff;
            }
        """)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        back_btn.clicked.connect(self.sound_player.play_click)

        # Back button hover events
        def back_enter(e):
            back_btn.setStyleSheet("""
                QPushButton {
                    background: #ce93d8;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 20px;
                    border: 3px solid #d8b4ff;
                }
            """)
            self.sound_player.play_hover()


        def back_leave(e):
            back_btn.setStyleSheet("""
                QPushButton {
                    background: #f3e8ff;
                    color: #4a148c;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 20px;
                    border: 3px solid #d8b4ff;
                }
            """)

        back_btn.enterEvent = back_enter
        back_btn.leaveEvent = back_leave

        back_row.addWidget(back_btn)
        main_layout.addLayout(back_row)

        # Title with extra space above
        title = QLabel("<h1 style='color: #9c27b0; font-weight: 900; margin: 0;'>Marvel Rivals Bingo</h1>")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Bingo card
        self.bingo_card = BingoCard(self)
        card_wrapper = QHBoxLayout()
        card_wrapper.addStretch(1)
        card_wrapper.addWidget(self.bingo_card)
        card_wrapper.addStretch(1)
        main_layout.addLayout(card_wrapper)

        # Generate button
        gen_row = QHBoxLayout()
        gen_row.setAlignment(Qt.AlignCenter)
        self.generate_btn = QPushButton("Generate New Card")
        self.generate_btn.setFixedSize(320, 56)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background: #f3e8ff;
                color: #4a148c;
                font-size: 18px;
                font-weight: bold;
                border-radius: 18px;
                border: 4px solid #d8b4ff;
            }
        """)
        self.generate_btn.setCursor(Qt.PointingHandCursor)
        self.generate_btn.clicked.connect(self.generate_card)
        self.generate_btn.clicked.connect(self.sound_player.play_click)

        # Generate button hover events
        def gen_enter(e):
            self.generate_btn.setStyleSheet("""
                QPushButton {
                    background: #ce93d8;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 18px;
                    border: 4px solid #d8b4ff;
                }
            """)
            self.sound_player.play_hover()

        # Generate button leave events
        def gen_leave(e):
            self.generate_btn.setStyleSheet("""
                QPushButton {
                    background: #f3e8ff;
                    color: #4a148c;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 18px;
                    border: 4px solid #d8b4ff;
                }
            """)
        
        self.generate_btn.enterEvent = gen_enter
        self.generate_btn.leaveEvent = gen_leave

        gen_row.addWidget(self.generate_btn)
        main_layout.addLayout(gen_row)

        main_layout.addSpacing(30)

        phrases_wrapper = QHBoxLayout()
        phrases_wrapper.addStretch(1)

        self.phrases_container = QWidget()
        self.phrases_container.setFixedSize(600, 130)
        self.phrases_container.setMouseTracking(True)

        container_layout = QVBoxLayout(self.phrases_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.phrases_edit = QTextEdit()
        self.phrases_edit.setPlaceholderText("Enter phrases separated by commas...")
        self.phrases_edit.setPlainText(", ".join(default_bingo_phrases))
        self.phrases_edit.setStyleSheet("""
            QTextEdit {
                background: #f9f1ff;
                border: 4px solid #d8b4ff;
                border-radius: 24px;
                padding: 12px;
                font-size: 14px;
                color: #4a148c;
            }
        """)
        self.phrases_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        container_layout.addWidget(self.phrases_edit)

        # Clean, elegant cover
        self.phrases_cover = QLabel(self.phrases_container)
        self.phrases_cover.setAlignment(Qt.AlignCenter)
        self.phrases_cover.setText("Custom Phrases")
        self.phrases_cover.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ce93d8, stop:1 #ba68c8);
                color: white;
                font-size: 22px;
                font-weight: bold;
                border: 4px solid #d8b4ff;
                border-radius: 24px;
            }
        """)
        self.phrases_cover.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.phrases_cover.show()
        self.phrases_cover.raise_()

        def enter_event(e):
            self.phrases_cover.hide()
            self.sound_player.play_hover()

        def leave_event(e):
            self.phrases_cover.show()

        self.phrases_container.enterEvent = enter_event
        self.phrases_container.leaveEvent = leave_event

        phrases_wrapper.addWidget(self.phrases_container)
        phrases_wrapper.addStretch(1)

        main_layout.addLayout(phrases_wrapper)

        main_layout.addStretch(1)

        self.generate_card()

    # Resizes the phrases cover
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if hasattr(self, 'phrases_cover'):
            self.phrases_cover.setGeometry(0, 0, 600, 130)

    # Paints the background
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w, h = self.width(), self.height()
        light = QColor("#f3e8ff")
        dark = QColor("#e6d4ff")
        stripe_width = 60
        angle = 45

        painter.save()
        painter.translate(w / 2, h / 2)
        painter.rotate(angle)
        painter.translate(-w / 2, -h / 2)

        offset = self.bg_offset
        x = -h * 3 - offset
        while x < w + h * 3:
            painter.fillRect(int(x), -h * 3, stripe_width, h * 6, dark)
            x += stripe_width
            painter.fillRect(int(x), -h * 3, stripe_width, h * 6, light)
            x += stripe_width

        painter.restore()

        self.bg_offset = (self.bg_offset - 1) % (stripe_width * 2)

        super().paintEvent(event)

    # Generates a new bingo card
    def generate_card(self):
        text = self.phrases_edit.toPlainText().strip()
        all_phrases = [p.strip() for p in text.replace("\n", ",").split(",") if p.strip()]

        source_phrases = all_phrases if len(all_phrases) >= 24 else default_bingo_phrases
        selected = random.sample(source_phrases, 24)

        self.bingo_card.set_phrases(selected)