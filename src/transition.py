# transition.py — Fade-to-Black with Bottom-Left Image + Animated "Loading ♡..." in Center
from PyQt5.QtWidgets import QWidget, QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QFont

from pathlib import Path

# Paths
ASSET_BASE = Path(__file__).parent.parent
TRANSITION_IMAGE_PATH = ASSET_BASE / "assets" / "transitionimage.jpg"


class SlideCurtainTransition:
    """
    Fast fade transition:
    - Fade in black overlay (blocks input)
    - Bottom-left silhouette image
    - Large "Loading ♡..." in center with smooth animated dots
    - Fade out together
    """

    def __init__(self, main_app_window):
        self.main_app = main_app_window

        # Full-screen black overlay — blocks all mouse events
        self.overlay = QWidget(main_app_window)
        self.overlay.setStyleSheet("background: black;")

        # Opacity for main fade
        self.opacity_effect = QGraphicsOpacityEffect(self.overlay)
        self.opacity_effect.setOpacity(0.0)
        self.overlay.setGraphicsEffect(self.opacity_effect)

        # Bottom-left silhouette
        self.transition_image = QLabel(self.overlay)
        self.transition_image.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        if TRANSITION_IMAGE_PATH.exists():
            pix = QPixmap(str(TRANSITION_IMAGE_PATH)).scaled(
                300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.transition_image.setPixmap(pix)

        # Large centered "Loading ♡..." text with animated dots
        self.loading_text = QLabel("Loading ♡", self.overlay)
        self.loading_text.setAlignment(Qt.AlignCenter)
        self.loading_text.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.loading_text.setStyleSheet("color: white; background: transparent;")
        self.loading_text.setFont(QFont("Segoe UI", 60, QFont.Bold))  # Clean, crisp font

        # Timer for dots animation
        self.dots_timer = QTimer(self.overlay)
        self.dots_timer.timeout.connect(self.update_dots)
        self.dot_count = 0

        # Main fade animations
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")

        self.setup_animations()

    def setup_animations(self):
        self.fade_in.setDuration(400)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutQuart)

        self.fade_out.setDuration(400)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InOutCubic)

    def update_dots(self):
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        self.loading_text.setText(f"Loading ♡{dots}")

    def go_to(self, target_index):
        win_w = self.main_app.width()
        win_h = self.main_app.height()

        self.overlay.setGeometry(0, 0, win_w, win_h)

        # Bottom-left image
        img_w = self.transition_image.pixmap().width() if self.transition_image.pixmap() else 300
        img_h = self.transition_image.pixmap().height() if self.transition_image.pixmap() else 300
        self.transition_image.setGeometry(0, win_h - img_h, img_w, img_h)

        # Center loading text
        self.loading_text.setGeometry(0, 0, win_w, win_h)

        # Show everything
        self.overlay.show()
        self.overlay.raise_()
        self.transition_image.show()
        self.transition_image.raise_()
        self.loading_text.show()
        self.loading_text.raise_()

        self.target_index = target_index
        self.fade_in.finished.connect(self.on_fade_in_complete)
        self.fade_in.start()

    def on_fade_in_complete(self):
        QTimer.singleShot(400, self.start_fade_out)

    def start_fade_out(self):
        self.dots_timer.stop()
        self.loading_text.setText("Loading ♡")  # Clean finish

        self.main_app.stack.setCurrentIndex(self.target_index)
        self.fade_out.finished.connect(self.cleanup)
        self.fade_out.start()

    def cleanup(self):
        self.overlay.hide()
        self.transition_image.hide()
        self.loading_text.hide()
        self.opacity_effect.setOpacity(0.0)
        try:
            self.fade_in.finished.disconnect()
            self.fade_out.finished.disconnect()
        except TypeError:
            pass