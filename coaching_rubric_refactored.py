"""
Coaching Rubric Tool - Player skill assessment and ranking system.

This module provides a comprehensive coaching interface for evaluating player
performance across different skill categories. Features animated backgrounds,
interactive rank selectors, and detailed note-taking capabilities.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGroupBox,
    QFrame, QGridLayout, QTextEdit
)


# ============================================================================
# CONFIGURATION AND DATA
# ============================================================================

class RankConfig:
    """Configuration constants for rank system."""
    
    # Available ranks in ascending order
    RANKS = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Celestial", "Eternity+"]
    
    # Skill score mapping for each rank tier
    TIER_SCORES = {
        "Bronze": 1, "Silver": 2, "Gold": 3, "Platinum": 3,
        "Diamond": 4, "Master": 4, "Celestial": 5, "Eternity+": 5
    }
    
    # Color scheme for each rank
    RANK_COLORS = {
        "Bronze": "#cd7f32", "Silver": "#c0c0c0", "Gold": "#ffd700",
        "Platinum": "#e5e4e2", "Diamond": "#b9f2ff", "Master": "#ffcc00",
        "Celestial": "#87ceeb", "Eternity+": "#9370db"
    }
    
    # Skill categories with associated colors
    CATEGORIES = {
        "Mechanics": {"color": "#ff80ab"},
        "Role Effectiveness": {"color": "#8c9eff"},
        "Game Sense": {"color": "#b388ff"},
        "Decision-Making": {"color": "#ffab91"}
    }
    
    # UI dimensions
    RANK_SIZE = (53, 55)  # Width, height of rank display
    RANK_CONTAINER_SIZE = (165, 80)  # Container for 3 ranks
    CATEGORY_CARD_SIZE = (300, 170)  # Size of category cards
    ARROW_BUTTON_SIZE = (32, 32)  # Navigation arrows


class AssetManager:
    """Manages loading and caching of rank images."""
    
    def __init__(self):
        """Initialize asset manager with base path."""
        self.base_path = Path(__file__).parent / "assets"
        self._image_cache: Dict[str, str] = {}
    
    def get_rank_image_path(self, rank_name: str) -> Optional[str]:
        """
        Get the file path for a rank's image.
        
        Args:
            rank_name: Name of the rank
            
        Returns:
            Absolute path to the rank image file, or None if not found
        """
        if rank_name in self._image_cache:
            return self._image_cache[rank_name]
        
        # Map rank names to actual filenames
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
        image_path = self.base_path / filename
        
        if image_path.exists():
            self._image_cache[rank_name] = str(image_path)
            return str(image_path)
        
        return None


# ============================================================================
# RANK SELECTOR COMPONENT
# ============================================================================

class RankSelector(QWidget):
    """
    Interactive rank selection widget with navigation.
    
    Provides a horizontal scrollable interface for selecting player ranks
    with smooth navigation and visual feedback. Supports empty containers
    for centering ranks at the extremes of the rank list.
    """
    
    def __init__(self, parent_widget: QWidget, category: Optional[str] = None, 
                 initial_rank: str = "Gold"):
        """
        Initialize rank selector.
        
        Args:
            parent_widget: Parent coaching rubric widget
            category: Skill category (None for player rank)
            initial_rank: Default rank to display
        """
        super().__init__()
        self.rubric = parent_widget
        self.category = category
        self.asset_manager = AssetManager()
        
        # Navigation state
        self.start_index = max(0, RankConfig.RANKS.index(initial_rank) - 1)
        self.selected_index = 1  # Middle position is selected by default
        
        # UI components
        self.rank_squares: List[Dict] = []
        
        self._setup_ui()
        self.update_display()
    
    def _setup_ui(self) -> None:
        """Create and arrange all UI components."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)
        
        # Left navigation arrow
        self._create_navigation_arrow(main_layout, "◄", self.prev_ranks)
        
        # Rank display container
        ranks_container = self._create_ranks_container()
        main_layout.addWidget(ranks_container, 0, Qt.AlignVCenter)
        
        # Right navigation arrow
        self._create_navigation_arrow(main_layout, "►", self.next_ranks)
    
    def _create_navigation_arrow(self, layout: QHBoxLayout, arrow_text: str, 
                               callback) -> None:
        """Create a navigation arrow button."""
        arrow_btn = QPushButton(arrow_text)
        arrow_btn.setFixedSize(*RankConfig.ARROW_BUTTON_SIZE)
        arrow_btn.setStyleSheet("""
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
        arrow_btn.clicked.connect(callback)
        layout.addWidget(arrow_btn, 0, Qt.AlignVCenter)
    
    def _create_ranks_container(self) -> QFrame:
        """Create the container that holds the rank displays."""
        container = QFrame()
        container.setFixedSize(*RankConfig.RANK_CONTAINER_SIZE)
        container.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create 3 rank display slots
        for i in range(3):
            rank_widget = self._create_rank_widget()
            self.rank_squares.append(rank_widget)
            layout.addWidget(rank_widget['widget'])
        
        return container
    
    def _create_rank_widget(self) -> Dict:
        """Create a single rank display widget."""
        widget = QWidget()
        widget.setFixedSize(*RankConfig.RANK_CONTAINER_SIZE)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Rank image display
        image_label = QLabel()
        image_label.setFixedSize(*RankConfig.RANK_SIZE)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setCursor(Qt.ArrowCursor)  # No clicking functionality
        
        # Rank name label
        name_label = QLabel("")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setFont(QFont("Arial", 9, QFont.Bold))
        name_label.setStyleSheet("color: #4a148c;")
        
        # Arrange components with vertical centering
        layout.addStretch()
        layout.addWidget(image_label, 0, Qt.AlignCenter)
        layout.addWidget(name_label, 0, Qt.AlignCenter)
        layout.addStretch()
        
        return {
            'widget': widget,
            'image': image_label,
            'label': name_label
        }
    
    def prev_ranks(self) -> None:
        """Navigate to previous set of ranks."""
        if self.start_index > -1:  # Allow empty container before Bronze
            self.start_index -= 1
            self.update_display()
    
    def next_ranks(self) -> None:
        """Navigate to next set of ranks."""
        if self.start_index + 3 < len(RankConfig.RANKS) + 1:  # Allow empty after Eternity+
            self.start_index += 1
            self.update_display()
    
    def update_display(self) -> None:
        """Update the visual display of ranks based on current position."""
        for i in range(3):
            index = self.start_index + i
            
            if 0 <= index < len(RankConfig.RANKS):
                self._display_rank(i, RankConfig.RANKS[index])
            else:
                self._display_empty_slot(i)
        
        self.update_score()
    
    def _display_rank(self, position: int, rank_name: str) -> None:
        """Display a specific rank in the given position."""
        # Handle special case for Eternity+ display name
        display_name = "Eternity" if rank_name == "Eternity+" else rank_name
        self.rank_squares[position]['label'].setText(display_name)
        
        # Try to load and display rank image
        image_path = self.asset_manager.get_rank_image_path(rank_name)
        
        if image_path:
            self._display_rank_image(position, image_path)
        else:
            self._display_fallback_rank(position, rank_name)
    
    def _display_rank_image(self, position: int, image_path: str) -> None:
        """Display the actual rank image."""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                *RankConfig.RANK_SIZE, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.rank_squares[position]['image'].setPixmap(scaled_pixmap)
            self.rank_squares[position]['image'].setStyleSheet("border: none;")
        else:
            # Fallback if image fails to load
            rank_name = RankConfig.RANKS[self.start_index + position]
            self._display_fallback_rank(position, rank_name)
    
    def _display_fallback_rank(self, position: int, rank_name: str) -> None:
        """Display colored circle with first letter as fallback."""
        self.rank_squares[position]['image'].setText(rank_name[0])
        self.rank_squares[position]['image'].setStyleSheet(f"""
            background-color: {RankConfig.RANK_COLORS[rank_name]};
            border-radius: 25px;
            color: white;
            border: none;
            font-size: 18px;
            font-weight: bold;
        """)
    
    def _display_empty_slot(self, position: int) -> None:
        """Display an empty slot (transparent)."""
        self.rank_squares[position]['image'].clear()
        self.rank_squares[position]['image'].setStyleSheet("background-color: transparent; border: none;")
        self.rank_squares[position]['label'].setText("")
    
    def select_rank(self, index: int) -> None:
        """
        Select a rank at the given position.
        
        Args:
            index: Position index (0, 1, or 2)
        """
        # Remove previous selection highlight
        self.rank_squares[self.selected_index]['widget'].setStyleSheet(
            "background: transparent; border: none;"
        )
        
        # Highlight new selection
        self.selected_index = index
        self.rank_squares[self.selected_index]['widget'].setStyleSheet(
            "background: rgba(186, 104, 200, 0.2); border: none; border-radius: 10px;"
        )
        
        self.update_score()
    
    def update_score(self) -> None:
        """Update the score based on currently selected rank."""
        index = self.start_index + self.selected_index
        
        if 0 <= index < len(RankConfig.RANKS):
            rank = RankConfig.RANKS[index]
            score = RankConfig.TIER_SCORES[rank]
            
            if self.category:
                # Update category score
                self.rubric.scores[self.category] = score
            else:
                # Update player rank
                self.rubric.player_rank = rank
    
    def reset(self) -> None:
        """Reset to default state (Gold rank centered)."""
        self.start_index = max(0, RankConfig.RANKS.index("Gold") - 1)
        self.selected_index = 1
        self.update_display()
        
        # Highlight the middle (Gold) rank
        self.rank_squares[1]['widget'].setStyleSheet(
            "background: rgba(186, 104, 200, 0.2); border: none; border-radius: 10px;"
        )


# ============================================================================
# MAIN COACHING RUBRIC INTERFACE
# ============================================================================

class CoachingRubric(QWidget):
    """
    Main coaching rubric interface with animated background.
    
    Provides a comprehensive interface for evaluating player skills across
    multiple categories with visual feedback and note-taking capabilities.
    Features an animated diagonal stripe background and responsive UI elements.
    """
    
    def __init__(self, stack_widget: Optional[QWidget] = None, 
                 sound_player: Optional[object] = None):
        """
        Initialize coaching rubric interface.
        
        Args:
            stack_widget: Page stack for navigation
            sound_player: Sound effect manager
        """
        super().__init__()
        self.stack = stack_widget
        self.sound_player = sound_player
        
        # Initialize data
        self.scores = {cat: RankConfig.TIER_SCORES["Gold"] 
                      for cat in RankConfig.CATEGORIES}
        self.player_rank = "Gold"
        
        # Animation state
        self.bg_offset = 0.0
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self.update)
        self.bg_timer.start(16)  # ~60 FPS animation
        
        # UI components
        self.selectors: Dict[str, RankSelector] = {}
        
        self._setup_ui()
        self._initialize_scores()
    
    def _setup_ui(self) -> None:
        """Create and arrange all UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(10)
        
        # Navigation and title section
        self._create_header_section(main_layout)
        
        # Player rank selector
        self._create_player_rank_section(main_layout)
        
        # Category cards grid
        self._create_category_cards(main_layout)
        
        # Notes section
        self._create_notes_section(main_layout)
        
        # Footer spacing
        main_layout.addStretch()
    
    def _create_header_section(self, layout: QVBoxLayout) -> None:
        """Create back button and title."""
        # Back button row
        back_row = QHBoxLayout()
        back_row.addStretch()
        
        back_btn = self._create_back_button()
        back_row.addWidget(back_btn)
        back_row.addStretch()
        
        layout.addLayout(back_row)
        
        # Title
        title = QLabel("Coaching")
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #9c27b0;")
        layout.addWidget(title)
        
        layout.addSpacing(10)
    
    def _create_back_button(self) -> QPushButton:
        """Create the navigation back button."""
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
        
        # Navigation and sound effects
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        if self.sound_player:
            back_btn.clicked.connect(self.sound_player.play_click)
        
        # Hover effects
        def enter_event(e):
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
        
        def leave_event(e):
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
        
        back_btn.enterEvent = enter_event
        back_btn.leaveEvent = leave_event
        
        return back_btn
    
    def _create_player_rank_section(self, layout: QVBoxLayout) -> None:
        """Create the player rank selection section."""
        player_label = QLabel("Player Rank")
        player_label.setFont(QFont("Arial", 16, QFont.Bold))
        player_label.setAlignment(Qt.AlignCenter)
        player_label.setStyleSheet("color: #9c27b0;")
        layout.addWidget(player_label)
        
        self.player_selector = RankSelector(self, None)
        layout.addWidget(self.player_selector, alignment=Qt.AlignCenter)
        
        layout.addSpacing(25)
    
    def _create_category_cards(self, layout: QVBoxLayout) -> None:
        """Create the 2x2 grid of category cards."""
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(20)
        
        # Create a card for each category
        for i, (category, config) in enumerate(RankConfig.CATEGORIES.items()):
            card = self._create_category_card(category, config['color'])
            self.selectors[category] = card['selector']
            grid.addWidget(card['frame'], i // 2, i % 2, alignment=Qt.AlignCenter)
        
        # Center the grid
        grid_row = QHBoxLayout()
        grid_row.setContentsMargins(0, 0, 0, 0)
        grid_row.addStretch()
        grid_row.addLayout(grid)
        grid_row.addStretch()
        
        layout.addLayout(grid_row)
        layout.addSpacing(30)
    
    def _create_category_card(self, category: str, color: str) -> Dict:
        """Create a single category card with rank selector."""
        # Card frame
        card_frame = QFrame()
        card_frame.setFixedSize(*RankConfig.CATEGORY_CARD_SIZE)
        card_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border: 4px solid #d8b4ff;
                border-radius: 25px;
            }
        """)
        
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(8)
        
        # Category title
        category_label = QLabel(category)
        category_label.setFont(QFont("Arial", 16, QFont.Bold))
        category_label.setAlignment(Qt.AlignCenter)
        category_label.setStyleSheet(f"color: {color}; border: transparent")
        card_layout.addWidget(category_label)
        
        # Rank selector for this category
        selector = RankSelector(self, category)
        card_layout.addWidget(selector, alignment=Qt.AlignCenter)
        
        return {
            'frame': card_frame,
            'selector': selector
        }
    
    def _create_notes_section(self, layout: QVBoxLayout) -> None:
        """Create the notes input section."""
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
        layout.addWidget(notes_group)
    
    def _initialize_scores(self) -> None:
        """Initialize all rank selectors with default scores."""
        self.player_selector.update_score()
        for selector in self.selectors.values():
            selector.update_score()
    
    def paintEvent(self, event) -> None:
        """
        Paint animated diagonal stripe background.
        
        Creates a smooth animated background with alternating diagonal stripes
        that move continuously for visual appeal.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # Animation parameters
        w, h = self.width(), self.height()
        light_color = QColor("#f3e8ff")
        dark_color = QColor("#e6d4ff")
        stripe_width = 60
        angle = 45
        
        # Calculate stripe positions
        offset = self.bg_offset
        
        # Draw dark stripes
        painter.save()
        painter.translate(w // 2, h // 2)
        painter.rotate(angle)
        painter.translate(-w // 2, -h // 2)
        
        x = -h * 3 - offset
        while x < w + h * 3:
            painter.fillRect(int(x), -h * 3, stripe_width, h * 6, dark_color)
            x += stripe_width * 2
        
        painter.restore()
        
        # Draw light stripes (offset by one stripe width)
        painter.save()
        painter.translate(w // 2, h // 2)
        painter.rotate(angle)
        painter.translate(-w // 2, -h // 2)
        
        x = -h * 3 - offset + stripe_width
        while x < w + h * 3:
            painter.fillRect(int(x), -h * 3, stripe_width, h * 6, light_color)
            x += stripe_width * 2
        
        painter.restore()
        
        # Update animation offset
        self.bg_offset = (self.bg_offset - 0.5) % 10000
        
        super().paintEvent(event)
