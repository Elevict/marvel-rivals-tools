# main.py
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QLabel, QPushButton
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtGui import QPixmap

# Import pages
from homepage import HomePage
from team_randomizer import TeamRandomizerPage, HERO_PIXMAPS
from transition import SlideCurtainTransition
from bingo import BingoPage
from coaching_rubric import CoachingRubric

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        # Get the directory where the script is located
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to reach the project root
        base_path = os.path.dirname(base_path)
    return os.path.join(base_path, relative_path)

# Paths
ASSET_BASE = Path(resource_path(""))
SOUND_PATH = resource_path("sounds/slot_loop.wav")
# And in SoundPlayer:
loop_path = resource_path("sounds/slot_loop.wav")
hover_path = resource_path("sounds/hover.wav")
click_path = resource_path("sounds/click.wav")

# Load all hero images once at startup
def load_hero_images():
    assets_dir = ASSET_BASE / "assets"
    hero_names = [
        "doctorstrange", "hulk", "ironman", "spiderman", "lunasnow", "namor",
        "loki", "blackpanther", "magik", "rocket", "groot", "peniparker",
        "storm", "magneto", "starlord", "mantis", "punisher", "scarletwitch",
        "hela", "venom", "adamwarlock", "thor", "jeff", "wintersoldier",
        "captainamerica", "psylocke", "moonknight", "hawkeye", "squirrelgirl",
        "ironfist", "blackwidow", "cloak&dagger", "wolverine", "mrfantastic",
        "invisiblewoman", "humantorch", "thething", "emmafrost", "ultron",
        "phoenix", "blade", "angela", "daredevil", "gambit", "rogue"
    ]
    for name in hero_names:
        path = assets_dir / f"{name}.webp"
        if path.exists():
            HERO_PIXMAPS[name] = QPixmap(str(path))


# Global sound player
class SoundPlayer:
    def __init__(self):
        base = ASSET_BASE / "sounds"

        # Slot loop (for randomizer)
        self.loop = QSoundEffect()
        loop_path = base / "slot_loop.wav"
        if loop_path.exists():
            self.loop.setSource(QUrl.fromLocalFile(str(loop_path)))
            self.loop.setLoopCount(QSoundEffect.Infinite)
            self.loop.setVolume(0.02)

        # UI hover sound
        self.hover = QSoundEffect()
        hover_path = base / "hover.wav"
        if hover_path.exists():
            self.hover.setSource(QUrl.fromLocalFile(str(hover_path)))
            self.hover.setVolume(0.02)

        # UI click sound
        self.click = QSoundEffect()
        click_path = base / "click.wav"
        if click_path.exists():
            self.click.setSource(QUrl.fromLocalFile(str(click_path)))
            self.click.setVolume(0.02)

    def play_loop(self):
        if self.loop.isLoaded() and not self.loop.isPlaying():
            self.loop.play()

    def stop_loop(self):
        if self.loop.isLoaded():
            self.loop.stop()

    def play_hover(self):
        if self.hover.isLoaded():
            self.hover.play()

    def play_click(self):
        if self.click.isLoaded():
            self.click.play()


# Main application window
class MainApp(QWidget):
    def __init__(self):
        super().__init__()

        # Frameless window (no OS borders/shadows)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # Window setup
        self.setWindowTitle("Kikyuu's Marvel Rivals Tools")
        self.setFixedSize(730, 1020)
        self.setStyleSheet("background: transparent;")

        # Load assets
        load_hero_images()
        self.sound_player = SoundPlayer()

        # Central navigation
        self.stack = QStackedWidget()
        self.stack.addWidget(HomePage(self.stack, self.sound_player))            # Index 0
        self.stack.addWidget(TeamRandomizerPage(self.stack, self.sound_player))  # Index 1
        self.stack.addWidget(BingoPage(self.stack, self.sound_player))           # Index 2
        self.stack.addWidget(CoachingRubric(self.stack, self.sound_player))      # Index 3

        # Screen transitions
        self.page_transition = SlideCurtainTransition(self)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        title_bar = QWidget(self)
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QWidget {
                background: #e1bee7;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        # Title label
        title_label = QLabel("Kikyuu's Marvel Rivals Tools")
        title_label.setStyleSheet("color: #4a148c; font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # Minimize button with hover highlight
        min_btn = QPushButton("—")
        min_btn.setFixedSize(30, 30)
        min_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #4a148c;
                font-weight: bold;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background: #ba68c8;
                color: white;
            }
        """)
        min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(min_btn)

        # Close button with hover highlight
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #4a148c;
                font-weight: bold;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background: #ba68c8;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

        # Make title bar draggable
        def move_window(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()
                event.accept()

        title_bar.mousePressEvent = lambda event: setattr(self, "drag_pos", event.globalPos()) if event.button() == Qt.LeftButton else None
        title_bar.mouseMoveEvent = move_window

        # Add title bar first
        layout.addWidget(title_bar)

        # Then add the stack
        layout.addWidget(self.stack)

        self.setLayout(layout)

    def go_to_page(self, index):
        self.page_transition.go_to(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())