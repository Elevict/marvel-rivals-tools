# coaching_rubric.py
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGroupBox,
    QFrame, QGridLayout, QTextEdit
)

# Ranks
RANKS = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Celestial", "Eternity+"]

# Score mapping
TIER_SCORES = {
    "Bronze": 1, "Silver": 2, "Gold": 3, "Platinum": 3,
    "Diamond": 4, "Master": 4, "Celestial": 5, "Eternity+": 5
}

# Colors
RANK_COLORS = {
    "Bronze": "#cd7f32", "Silver": "#c0c0c0", "Gold": "#ffd700",
    "Platinum": "#e5e4e2", "Diamond": "#b9f2ff", "Master": "#ffcc00",
    "Celestial": "#87ceeb", "Eternity+": "#9370db"
}

CATEGORIES = {
    "Mechanics": {"color": "#ff80ab"},
    "Role Effectiveness": {"color": "#8c9eff"},
    "Game Sense": {"color": "#b388ff"},
    "Decision-Making": {"color": "#ffab91"}
}

import os
from pathlib import Path

# Asset loading
ASSET_BASE = Path(__file__).parent.parent / "assets"

def load_rank_image(rank_name):
    """Load rank image from assets folder."""
    # Map rank names to your actual filenames
    filename_map = {
        "Bronze": "bronze.png",
        "Silver": "silver.png", 
        "Gold": "gold.png",
        "Platinum": "plat.png",
        "Diamond": "diamond.png",
        "Master": "grandmaster.webp",
        "Celestial": "celestial.webp",
        "Eternity+": "eternity.png"
    }
    
    filename = filename_map.get(rank_name, f"{rank_name.lower()}.png")
    image_path = ASSET_BASE / filename

    if image_path.exists():
        return str(image_path)
    return None

class RankSelector(QWidget):
    def __init__(self, rubric, category=None, initial_rank="Gold"):
        super().__init__()
        self.rubric = rubric
        self.category = category
        self.start_index = max(0, RANKS.index(initial_rank) - 1)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        self.left_btn = QPushButton("◄")
        self.left_btn.setFixedSize(32, 32)
        self.left_btn.setStyleSheet("""
            QPushButton {
                background: #f3e8ff;
                color: #4a148c;
                font-size: 16px;
                font-weight: bold;
                border-radius: 16px;
                border: 3px solid #d8b4ff;
            }
            QPushButton:hover {
                background: #ce93d8;
                color: white;
            }
        """)
        self.left_btn.clicked.connect(self.prev_ranks)
        main_layout.addWidget(self.left_btn, 0, Qt.AlignVCenter)

        ranks_container = QFrame()
        ranks_container.setFixedSize(165, 80)
        ranks_container.setStyleSheet("background: transparent; border: none;")

        ranks_layout = QHBoxLayout(ranks_container)
        ranks_layout.setContentsMargins(0, 0, 0, 0)
        ranks_layout.setSpacing(0)

        self.rank_squares = []
        for i in range(3):
            rank_widget = QWidget()
            rank_widget.setFixedSize(53, 80)
            
            widget_layout = QVBoxLayout(rank_widget)
            widget_layout.setContentsMargins(0, 0, 0, 0)
            widget_layout.setSpacing(0)
            
            square = QLabel()
            square.setFixedSize(53, 55)
            square.setAlignment(Qt.AlignCenter)
            square.setCursor(Qt.ArrowCursor)
            
            rank_label = QLabel("")
            rank_label.setAlignment(Qt.AlignCenter)
            rank_label.setFont(QFont("Arial", 9, QFont.Bold))
            rank_label.setStyleSheet("color: #4a148c;")

            widget_layout.addStretch()
            widget_layout.addWidget(square, 0, Qt.AlignCenter)
            widget_layout.addWidget(rank_label, 0, Qt.AlignCenter)
            widget_layout.addStretch()
            
            self.rank_squares.append({'widget': rank_widget, 'image': square, 'label': rank_label})
            ranks_layout.addWidget(rank_widget)

        main_layout.addWidget(ranks_container, 0, Qt.AlignVCenter)

        self.right_btn = QPushButton("►")
        self.right_btn.setFixedSize(32, 32)
        self.right_btn.setStyleSheet(self.left_btn.styleSheet())
        self.right_btn.clicked.connect(self.next_ranks)
        main_layout.addWidget(self.right_btn, 0, Qt.AlignVCenter)

        self.selected_index = 1
        self.update_display()

    def prev_ranks(self):
        if self.start_index > -1:  # Allow going to -1 to show empty container before Bronze
            self.start_index -= 1
            self.update_display()

    def next_ranks(self):
        if self.start_index + 3 < len(RANKS) + 1:  # Allow going to len(RANKS)-1 to show empty container after Eternity+
            self.start_index += 1
            self.update_display()

    def update_display(self):
        for i in range(3):
            index = self.start_index + i
            if 0 <= index < len(RANKS):  # Only show ranks for valid indices
                rank = RANKS[index]
                image_path = load_rank_image(rank)
                
                # Update rank name label (handle Eternity+ specially)
                display_name = "Eternity" if rank == "Eternity+" else rank
                self.rank_squares[i]['label'].setText(display_name)
                
                if image_path:
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(53, 55, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.rank_squares[i]['image'].setPixmap(scaled_pixmap)
                        self.rank_squares[i]['image'].setStyleSheet("border: none;")
                    else:
                        # Fallback to colored circle if image fails to load
                        self.rank_squares[i]['image'].setText(rank[0])  # First letter as fallback
                        self.rank_squares[i]['image'].setStyleSheet(f"""
                            background-color: {RANK_COLORS[rank]};
                            border-radius: 25px;
                            color: white;
                            border: none;
                            font-size: 18px;
                            font-weight: bold;
                        """)
                else:
                    # Fallback to colored circle if image doesn't exist
                    self.rank_squares[i]['image'].setText(rank[0])  # First letter as fallback
                    self.rank_squares[i]['image'].setStyleSheet(f"""
                        background-color: {RANK_COLORS[rank]};
                        border-radius: 25px;
                        color: white;
                        border: none;
                        font-size: 18px;
                        font-weight: bold;
                    """)
            else:
                # Show empty container for invalid indices (before Bronze or after Eternity+)
                self.rank_squares[i]['image'].clear()
                self.rank_squares[i]['image'].setStyleSheet("background-color: transparent; border: none;")
                self.rank_squares[i]['label'].setText("")
        self.update_score()

    def select_rank(self, idx):
        # Remove highlight from previous selection (only background)
        self.rank_squares[self.selected_index]['widget'].setStyleSheet("background: transparent; border: none;")
        
        # Add highlight to new selection (only background)
        self.selected_index = idx
        self.rank_squares[self.selected_index]['widget'].setStyleSheet(
            "background: rgba(186, 104, 200, 0.2); border: none; border-radius: 10px;"
        )
        self.update_score()

    def update_score(self):
        index = self.start_index + self.selected_index
        if 0 <= index < len(RANKS):  # Only update score if index is valid
            rank = RANKS[index]
            score = TIER_SCORES[rank]
            if self.category:
                self.rubric.scores[self.category] = score
            else:
                self.rubric.player_rank = rank

    def reset(self):
        self.start_index = max(0, RANKS.index("Gold") - 1)
        self.selected_index = 1
        self.update_display()
        # Highlight the middle (Gold) rank with subtle background
        self.rank_squares[1]['widget'].setStyleSheet(
            "background: rgba(186, 104, 200, 0.2); border: none; border-radius: 10px;"
        )

class CoachingRubric(QWidget):
    def __init__(self, stack=None, sound_player=None):
        super().__init__()
        self.stack = stack
        self.sound_player = sound_player

        # Background animation
        self.bg_offset = 0.0
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self.update)
        self.bg_timer.start(16)

        self.scores = {cat: TIER_SCORES["Gold"] for cat in CATEGORIES}
        self.player_rank = "Gold"

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(10)  # Reduced overall spacing

        # Centered Back button
        back_row = QHBoxLayout()
        back_row.addStretch()
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
        back_btn.clicked.connect(self.sound_player.play_click if self.sound_player else lambda: None)

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
            if self.sound_player:
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
        back_row.addStretch()
        main_layout.addLayout(back_row)

        # Title
        title = QLabel("Coaching")
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #9c27b0;")
        main_layout.addWidget(title)

        main_layout.addSpacing(10)  # Less space between title and Player Rank

        # Small Player Rank section
        player_label = QLabel("Player Rank")
        player_label.setFont(QFont("Arial", 16, QFont.Bold))
        player_label.setAlignment(Qt.AlignCenter)
        player_label.setStyleSheet("color: #9c27b0;")
        main_layout.addWidget(player_label)

        self.player_selector = RankSelector(self, None)
        main_layout.addWidget(self.player_selector, alignment=Qt.AlignCenter)

        main_layout.addSpacing(25)  # Moderate space before cards

        # 2x2 grid with 4 separate large cards
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(20)
        self.selectors = {}
        for i, category in enumerate(CATEGORIES):
            # Large individual card
            card = QFrame()
            card.setFixedSize(300, 170) # Card size
            card.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.95);
                    border: 4px solid #d8b4ff;
                    border-radius: 25px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 12, 14, 12)
            card_layout.setSpacing(8)

            cat_label = QLabel(category)
            cat_label.setFont(QFont("Arial", 16, QFont.Bold))
            cat_label.setAlignment(Qt.AlignCenter)
            cat_label.setStyleSheet(f"color: {CATEGORIES[category]['color']}; border: transparent")
            card_layout.addWidget(cat_label)

            selector = RankSelector(self, category)
            self.selectors[category] = selector
            card_layout.addWidget(selector, alignment=Qt.AlignCenter)

            grid.addWidget(card, i // 2, i % 2, alignment=Qt.AlignCenter)

        grid_row = QHBoxLayout()
        grid_row.setContentsMargins(0, 0, 0, 0)
        grid_row.addStretch()
        grid_row.addLayout(grid)
        grid_row.addStretch()
        main_layout.addLayout(grid_row)

        main_layout.addSpacing(30)

        # Large Notes section
        notes_group = QGroupBox("Notes")
        notes_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #6a1b9a;
                background: rgba(255, 255, 255, 0.94);
                border: 4px solid #d8b4ff;
                border-radius: 20px;
                padding: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 30px;
                padding: 8px 16px;
                background: transparent;
            }
        """)
        notes_layout = QVBoxLayout()
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Write your coaching notes here...")
        self.notes_edit.setStyleSheet("""
            QTextEdit {
                background: #f9f1ff;
                border: none;
                border-radius: 16px;
                padding: 20px;
                font-size: 16px;
                color: #4a148c;
            }
        """)
        notes_layout.addWidget(self.notes_edit)
        notes_group.setLayout(notes_layout)
        main_layout.addWidget(notes_group)

        main_layout.addStretch()

        # Initial score updates
        self.player_selector.update_score()
        for selector in self.selectors.values():
            selector.update_score()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w = self.width()
        h = self.height()

        light = QColor("#f3e8ff")
        dark = QColor("#e6d4ff")
        stripe_width = 60
        angle = 45

        offset = self.bg_offset

        painter.save()
        painter.translate(w / 2, h / 2)
        painter.rotate(angle)
        painter.translate(-w / 2, -h / 2)

        x = -h * 3 - offset
        while x < w + h * 3:
            painter.fillRect(int(x), -h * 3, stripe_width, h * 6, dark)
            x += stripe_width * 2

        painter.restore()

        painter.save()
        painter.translate(w / 2, h / 2)
        painter.rotate(angle)
        painter.translate(-w / 2, -h / 2)

        x = -h * 3 - offset + stripe_width
        while x < w + h * 3:
            painter.fillRect(int(x), -h * 3, stripe_width, h * 6, light)
            x += stripe_width * 2

        painter.restore()

        self.bg_offset = (self.bg_offset - 0.5) % 10000

        super().paintEvent(event)