"""
Main application entry point for Marvel Rivals Tools.

This module contains the primary application window, sound management,
and asset loading functionality. It serves as the central hub for all
tool pages and manages the overall application lifecycle.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QLabel, QPushButton
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtGui import QPixmap

# Import all tool pages
from homepage import HomePage
from team_randomizer import TeamRandomizerPage, HERO_PIXMAPS
from transition import SlideCurtainTransition
from bingo import BingoPage
from coaching_rubric import CoachingRubric


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

class AppConfig:
    """Central configuration for the application."""
    
    WINDOW_TITLE = "Kikyuu's Marvel Rivals Tools"
    WINDOW_SIZE = (730, 1020)
    SOUND_VOLUME = 0.02  # Low volume for better user experience
    
    # Hero roster for team randomizer
    HERO_ROSTER = [
        "doctorstrange", "hulk", "ironman", "spiderman", "lunasnow", "namor",
        "loki", "blackpanther", "magik", "rocket", "groot", "peniparker",
        "storm", "magneto", "starlord", "mantis", "punisher", "scarletwitch",
        "hela", "venom", "adamwarlock", "thor", "jeff", "wintersoldier",
        "captainamerica", "psylocke", "moonknight", "hawkeye", "squirrelgirl",
        "ironfist", "blackwidow", "cloak&dagger", "wolverine", "mrfantastic",
        "invisiblewoman", "humantorch", "thething", "emmafrost", "ultron",
        "phoenix", "blade", "angela", "daredevil", "gambit", "rogue"
    ]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for development and PyInstaller.
    
    Args:
        relative_path: Relative path from the application root
        
    Returns:
        Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # In development, use current directory
        base_path = os.path.abspath("")
    return os.path.join(base_path, relative_path)


def load_hero_images() -> None:
    """
    Preload all hero images into memory for instant access.
    
    This function loads all hero images at startup to prevent loading delays
    during runtime. Images are stored in the global HERO_PIXMAPS dictionary.
    """
    assets_dir = Path(resource_path("assets"))
    
    for hero_name in AppConfig.HERO_ROSTER:
        image_path = assets_dir / f"{hero_name}.webp"
        if image_path.exists():
            HERO_PIXMAPS[hero_name] = QPixmap(str(image_path))


# ============================================================================
# SOUND MANAGEMENT
# ============================================================================

class SoundManager:
    """
    Centralized sound management for all UI interactions.
    
    Provides optimized sound playback with proper error handling and
    resource management. All sounds are preloaded and ready for instant playback.
    """
    
    def __init__(self):
        """Initialize sound manager and preload all sound effects."""
        self.sounds_dir = Path(resource_path("sounds"))
        self._sounds: Dict[str, QSoundEffect] = {}
        self._load_sounds()
    
    def _load_sounds(self) -> None:
        """Load and configure all sound effects."""
        sound_files = {
            'loop': 'slot_loop.wav',
            'hover': 'hover.wav', 
            'click': 'click.wav'
        }
        
        for sound_name, filename in sound_files.items():
            sound_effect = QSoundEffect()
            sound_path = self.sounds_dir / filename
            
            if sound_path.exists():
                sound_effect.setSource(QUrl.fromLocalFile(str(sound_path)))
                sound_effect.setVolume(AppConfig.SOUND_VOLUME)
                
                # Configure loop sound for infinite playback
                if sound_name == 'loop':
                    sound_effect.setLoopCount(QSoundEffect.Infinite)
                
                self._sounds[sound_name] = sound_effect
                print(f"Loaded sound: {sound_path}")
    
    def play_loop(self) -> None:
        """Start playing the background loop sound."""
        if sound := self._sounds.get('loop'):
            if sound.isLoaded() and not sound.isPlaying():
                sound.play()
    
    def stop_loop(self) -> None:
        """Stop the background loop sound."""
        if sound := self._sounds.get('loop'):
            if sound.isLoaded():
                sound.stop()
    
    def play_hover(self) -> None:
        """Play hover interaction sound."""
        if sound := self._sounds.get('hover'):
            if sound.isLoaded():
                sound.play()
    
    def play_click(self) -> None:
        """Play click interaction sound."""
        if sound := self._sounds.get('click'):
            if sound.isLoaded():
                sound.play()


# ============================================================================
# CUSTOM WIDGETS
# ============================================================================

class TitleBar(QWidget):
    """
    Custom title bar with window controls and drag functionality.
    
    Provides a modern, frameless window experience with minimize/close buttons
    and mouse drag support for window movement.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize custom title bar."""
        super().__init__(parent)
        self.setFixedHeight(40)
        self._drag_position = None
        self._setup_ui()
        self._setup_drag_functionality()
    
    def _setup_ui(self) -> None:
        """Create and configure title bar UI elements."""
        self.setStyleSheet("""
            QWidget {
                background: #e1bee7;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        # Application title
        title = QLabel(AppConfig.WINDOW_TITLE)
        title.setStyleSheet("color: #4a148c; font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        layout.addStretch()
        
        # Window control buttons
        self._create_control_button(layout, "—", self.parent().showMinimized)
        self._create_control_button(layout, "✕", self.parent().close)
    
    def _create_control_button(self, layout: QHBoxLayout, text: str, 
                             callback) -> None:
        """Create a window control button with hover effects."""
        button = QPushButton(text)
        button.setFixedSize(30, 30)
        button.setStyleSheet("""
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
        button.clicked.connect(callback)
        layout.addWidget(button)
    
    def _setup_drag_functionality(self) -> None:
        """Enable window dragging via mouse events."""
        def mouse_press(event):
            if event.button() == Qt.LeftButton:
                self._drag_position = event.globalPos()
                event.accept()
        
        def mouse_move(event):
            if event.buttons() == Qt.LeftButton and self._drag_position:
                delta = event.globalPos() - self._drag_position
                self.parent().move(self.parent().pos() + delta)
                self._drag_position = event.globalPos()
                event.accept()
        
        def mouse_release(event):
            self._drag_position = None
            event.accept()
        
        self.mousePressEvent = mouse_press
        self.mouseMoveEvent = mouse_move
        self.mouseReleaseEvent = mouse_release


# ============================================================================
# MAIN APPLICATION WINDOW
# ============================================================================

class MarvelRivalsToolsApp(QWidget):
    """
    Main application window for Marvel Rivals Tools.
    
    This is the central hub that manages all tool pages, sound effects,
    and user interactions. Features a modern frameless design with smooth
    transitions and responsive UI elements.
    """
    
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        self._setup_window()
        self._initialize_components()
        self._setup_ui()
        self._load_assets()
    
    def _setup_window(self) -> None:
        """Configure window properties and appearance."""
        # Frameless window for modern appearance
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Window properties
        self.setWindowTitle(AppConfig.WINDOW_TITLE)
        self.setFixedSize(*AppConfig.WINDOW_SIZE)
        self.setStyleSheet("background: transparent;")
    
    def _initialize_components(self) -> None:
        """Initialize core application components."""
        # Sound management
        self.sound_manager = SoundManager()
        
        # Page navigation stack
        self.page_stack = QStackedWidget()
        
        # Page transition system
        self.page_transition = SlideCurtainTransition(self)
    
    def _setup_ui(self) -> None:
        """Create and arrange all UI elements."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Custom title bar
        title_bar = TitleBar(self)
        main_layout.addWidget(title_bar)
        
        # Main content area
        main_layout.addWidget(self.page_stack)
        
        self.setLayout(main_layout)
    
    def _load_assets(self) -> None:
        """Load all required assets and initialize pages."""
        # Preload hero images for instant access
        load_hero_images()
        
        # Initialize all tool pages
        self._initialize_pages()
    
    def _initialize_pages(self) -> None:
        """Create and add all tool pages to the stack."""
        pages = [
            (HomePage, "Home"),
            (TeamRandomizerPage, "Team Randomizer"),
            (BingoPage, "Bingo"),
            (CoachingRubric, "Coaching Rubric")
        ]
        
        for page_class, page_name in pages:
            page = page_class(self.page_stack, self.sound_manager)
            self.page_stack.addWidget(page)
            print(f"Initialized page: {page_name}")
    
    def navigate_to_page(self, page_index: int) -> None:
        """
        Navigate to a specific page with transition effect.
        
        Args:
            page_index: Index of the target page in the stack
        """
        if 0 <= page_index < self.page_stack.count():
            self.page_transition.go_to(page_index)


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main() -> None:
    """Main application entry point."""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName(AppConfig.WINDOW_TITLE)
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    main_window = MarvelRivalsToolsApp()
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
