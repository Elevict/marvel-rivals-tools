# team_randomizer.py
import random
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QGroupBox,
    QVBoxLayout, QHBoxLayout, QFrame,
    QRadioButton, QCheckBox, QGridLayout, QButtonGroup
)

# Global assets (loaded in main.py)
hero_pixmaps = {}

# Hero list & roles
heroes = [
    "Doctor Strange", "Hulk", "Iron Man", "Spiderman", "Luna Snow", "Namor",
    "Loki", "Black Panther", "Magik", "Rocket", "Groot", "Peni Parker",
    "Storm", "Magneto", "Star Lord", "Mantis", "Punisher", "Scarlet Witch",
    "Hela", "Venom", "Adam Warlock", "Thor", "Jeff", "Winter Soldier",
    "Captain America", "Psylocke", "Moon Knight", "Hawkeye", "Squirrel Girl",
    "Iron Fist", "Black Widow", "Cloak & Dagger", "Wolverine", "Mr Fantastic",
    "Invisible Woman", "Human Torch", "The Thing", "Emma Frost", "Ultron",
    "Phoenix", "Blade", "Angela", "Daredevil", "Gambit", "Rogue"
]

role_map = {
    "Duelist": [
        "Iron Man", "Spiderman", "Black Panther", "Storm", "Namor", "Magik",
        "Star Lord", "Punisher", "Scarlet Witch", "Hela", "Winter Soldier",
        "Psylocke", "Moon Knight", "Hawkeye", "Squirrel Girl", "Iron Fist",
        "Black Widow", "Wolverine", "Mr Fantastic", "Human Torch", "Phoenix",
        "Blade", "Daredevil"
    ],
    "Strategist": [
        "Loki", "Rocket", "Luna Snow", "Mantis", "Adam Warlock",
        "Jeff", "Cloak & Dagger", "Invisible Woman", "Ultron", "Gambit"
    ],
    "Vanguard": [
        "Hulk", "Doctor Strange", "Groot", "Peni Parker", "Magneto", "Venom",
        "Thor", "Captain America", "The Thing", "Emma Frost", "Angela", "Rogue"
    ]
}

role_colors = {"Strategist": "#b388ff", "Duelist": "#ff80ab", "Vanguard": "#8c9eff"}


class HeroSlot(QFrame):
    def __init__(self, reroll_callback=None):
        super().__init__()
        self.setFixedSize(136, 236)
        self.reroll_callback = reroll_callback

        self.setStyleSheet("""
            HeroSlot {
                background: rgba(255, 255, 255, 0.92);
                border: 3px solid #d8b4ff;
                border-radius: 18px;
                box-shadow: 0 8px 20px rgba(180, 120, 255, 0.15);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(10)

        self.image = QLabel()
        self.image.setFixedSize(112, 112)
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setStyleSheet("background: #f5f0ff; border-radius: 12px;")

        self.name = QLabel("Hero")
        self.name.setAlignment(Qt.AlignCenter)
        self.name.setStyleSheet("font-weight: bold; font-size: 13px; color: #4a148c;")

        self.role = QLabel("")
        self.role.setAlignment(Qt.AlignCenter)
        self.role.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.username = QLineEdit("Player")
        self.username.setAlignment(Qt.AlignCenter)
        self.username.setFixedHeight(32)
        self.username.setStyleSheet("background: #f3e8ff; border: none; border-radius: 10px; padding: 6px; font-size: 13px; color: #6a1b9a;")
        self.username.returnPressed.connect(self.username.clearFocus)

        layout.addWidget(self.image, alignment=Qt.AlignCenter)
        layout.addWidget(self.name, alignment=Qt.AlignCenter)
        layout.addWidget(self.role, alignment=Qt.AlignCenter)
        layout.addWidget(self.username, alignment=Qt.AlignCenter)

        self.setMouseTracking(True)

    def enterEvent(self, event):
        from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint

        # Store original position if not already stored
        if not hasattr(self, "original_pos"):
            self.original_pos = self.pos()

        # Lift up animation
        self.anim_lift = QPropertyAnimation(self, b"pos")
        self.anim_lift.setDuration(300)
        self.anim_lift.setStartValue(self.pos())
        self.anim_lift.setEndValue(QPoint(self.original_pos.x(), self.original_pos.y() - 20))
        self.anim_lift.setEasingCurve(QEasingCurve.OutCubic)
        self.anim_lift.start()

    def leaveEvent(self, event):
        from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint

        # Return to exact original position
        if not hasattr(self, "original_pos"):
            self.original_pos = self.pos()  # Fallback

        self.anim_return = QPropertyAnimation(self, b"pos")
        self.anim_return.setDuration(400)
        self.anim_return.setStartValue(self.pos())
        self.anim_return.setEndValue(self.original_pos)
        self.anim_return.setEasingCurve(QEasingCurve.OutBack)  # Nice bouncy settle
        self.anim_return.start()

    def set_hero(self, hero):
        key = hero.lower().replace(" ", "")
        pix = hero_pixmaps.get(key)
        if pix:
            self.image.setPixmap(pix.scaled(112, 112, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.image.setText("")
        else:
            self.image.setText(hero[:9])

        self.name.setText(hero)
        for role, heroes in role_map.items():
            if hero in heroes:
                self.role.setText(role)
                self.role.setStyleSheet(f"color: {role_colors[role]}; font-weight: bold;")
                break

    def pulse(self):
        from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
        anim = QPropertyAnimation(self, b"windowOpacity", self)
        anim.setDuration(800)
        anim.setKeyValues([(0, 1.0), (0.4, 0.6), (1.0, 1.0)])
        anim.setEasingCurve(QEasingCurve.OutBack)
        anim.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.reroll_callback:
            self.reroll_callback(self)


class TeamRandomizerPage(QWidget):
    def __init__(self, stack, sound_player):
        super().__init__()
        self.stack = stack
        self.sound_player = sound_player
        self.animation_running = False
        self.button_cooldown = False
        self.timers = []

        self.all_slots = []

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 18, 20, 20)
        main_layout.setSpacing(20)

        # Animation offset
        self.bg_offset = 0.0  # Use float for smoother increments
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self.update_background)
        self.bg_timer.start(16)  # High frequency for smoothness

        # Back Button
        back_row = QHBoxLayout()
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
        back_btn.clicked.connect(lambda: stack.setCurrentIndex(0))

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

        back_btn.clicked.connect(self.sound_player.play_click)

        back_row.addWidget(back_btn)
        main_layout.addLayout(back_row)

        # Teams
        teams_row = QHBoxLayout()
        teams_row.setSpacing(90)
        for team_name in ["Team A", "Team B"]:
            col = QVBoxLayout()
            col.setSpacing(18)
            title = QLabel(f"<h1 style='color: #9c27b0; font-weight: 900;'>{team_name}</h1>")
            title.setAlignment(Qt.AlignCenter)
            col.addWidget(title)
            grid = QGridLayout()
            grid.setHorizontalSpacing(20)
            grid.setVerticalSpacing(18)
            player_num = 1
            for r in range(3):
                for c in range(2):
                    slot = HeroSlot(self.reroll_single)
                    slot.username.setText(f"Player {player_num}")
                    grid.addWidget(slot, r, c)
                    self.all_slots.append(slot)
                    player_num += 1
            col.addLayout(grid)
            teams_row.addLayout(col)
        main_layout.addLayout(teams_row)

        # Bottom: Settings + Button
        bottom = QHBoxLayout()

        bottom.setSpacing(90)  # Adjust gap between buttons if needed
        settings = QGroupBox("Settings")
        settings.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #6a1b9a;
                background: rgba(255, 245, 255, 0.94);
                border: 3px solid #d8b4ff;
                border-radius: 10px;
                padding: 6px;
                margin-top: 6px;
            }
            QGroupBox::title {
                background: rgba(255, 245, 255, 0);
                padding: 4px 12px;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 0px;
                top: 7.5px;
            }
        """)
        settings.setFixedSize(290, 110)
        grid = QGridLayout()
        grid.setSpacing(1)
        grid.setContentsMargins(8, 6, 8, 6)

        self.mode_group = QButtonGroup()
        self.rb_instant = QRadioButton("Instant")
        self.rb_animated = QRadioButton("Animated")
        self.rb_instant.setChecked(True)
        self.mode_group.addButton(self.rb_instant)
        self.mode_group.addButton(self.rb_animated)
        grid.addWidget(QLabel("Mode:"), 0, 0)
        grid.addWidget(self.rb_instant, 0, 1)
        grid.addWidget(self.rb_animated, 0, 2)

        self.rules_group = QButtonGroup()
        self.rb_free = QRadioButton("Free")
        self.rb_unique = QRadioButton("Unique")
        self.rb_free.setChecked(True)
        self.rules_group.addButton(self.rb_free)
        self.rules_group.addButton(self.rb_unique)
        grid.addWidget(QLabel("Heroes:"), 1, 0)
        grid.addWidget(self.rb_free, 1, 1)
        grid.addWidget(self.rb_unique, 1, 2)

        row = QHBoxLayout()
        self.cb_222 = QCheckBox("2-2-2 Team Format")
        self.cb_shuffle = QCheckBox("Shuffle Players")
        self.cb_shuffle.setChecked(False)
        row.addWidget(self.cb_222)
        row.addWidget(self.cb_shuffle)
        grid.addLayout(row, 2, 0, 1, 3)
        settings.setLayout(grid)
        bottom.addWidget(settings)

        self.randomize_btn = QPushButton("Randomize Teams")
        self.randomize_btn.setFixedSize(290, 52)
        self.randomize_btn.setStyleSheet("""
            QPushButton {
                background: #f3e8ff;
                color: #4a148c;
                font-size: 16px;
                font-weight: bold;
                border-radius: 26px;
                border: 3px solid #d8b4ff;
            }
        """)
        self.randomize_btn.setCursor(Qt.PointingHandCursor)
        self.randomize_btn.clicked.connect(self.randomize_teams)

        def randomize_enter(e):
            self.randomize_btn.setStyleSheet("""
                QPushButton {
                    background: #ce93d8;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 26px;
                    border: 3px solid #d8b4ff;
                }
            """)
            self.sound_player.play_hover()

        # Hover leave: revert visual
        def randomize_leave(e):
            # Only revert to normal style if not in "STOP" mode
            if not self.animation_running:
                self.randomize_btn.setStyleSheet("""
                    QPushButton {
                        background: #f3e8ff;
                        color: #4a148c;
                        font-size: 16px;
                        font-weight: bold;
                        border-radius: 26px;
                        border: 3px solid #d8b4ff;
                    }
                """)

        self.randomize_btn.enterEvent = randomize_enter
        self.randomize_btn.leaveEvent = randomize_leave

        # Click sound on press
        self.randomize_btn.clicked.connect(self.sound_player.play_click)

        def mouse_release(event):
            QPushButton.mouseReleaseEvent(self.randomize_btn, event)
            if self.randomize_btn.underMouse():
                self.randomize_btn.enterEvent(None)

        self.randomize_btn.mouseReleaseEvent = mouse_release
        self.randomize_btn.setMouseTracking(True)

        bottom.addWidget(self.randomize_btn)
        main_layout.addLayout(bottom)

        self._randomize_instant()

    def update_background(self):
        self.bg_offset = (self.bg_offset - 0.5) % 10000  # Reverse direction, very long cycle
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w = self.width()
        h = self.height()

        # Colors
        color_light = QColor("#f3e8ff")
        color_dark = QColor("#e6d4ff")

        stripe_width = 60
        angle = 45

        # Draw animated diagonal stripes
        offset = self.bg_offset

        painter.save()
        painter.translate(w / 2, h / 2)
        painter.rotate(angle)
        painter.translate(-w / 2, -h / 2)

        x = -h * 3 - offset  # Extended coverage for no black patches
        while x < w + h * 3:  # Draw extra to cover all corners
            painter.fillRect(int(x), -h * 3, stripe_width, h * 6, color_dark)
            x += stripe_width * 2

        painter.restore()

        # Draw light stripes on top
        painter.save()
        painter.translate(w / 2, h / 2)
        painter.rotate(angle)
        painter.translate(-w / 2, -h / 2)

        x = -h * 3 - offset + stripe_width
        while x < w + h * 3:
            painter.fillRect(int(x), -h * 3, stripe_width, h * 6, color_light)
            x += stripe_width * 2

        painter.restore()

        super().paintEvent(event)

    # === All your existing methods below (unchanged) ===
    def get_role(self, hero):
        for role, heroes in role_map.items():
            if hero in heroes:
                return role
        return None

    def generate_heroes(self):
        if self.cb_222.isChecked():
            team_a = []
            team_b = []
            for role in role_map:
                pool = role_map[role][:]
                if self.rb_unique.isChecked():
                    random.shuffle(pool)
                    team_a.extend(pool[:2])
                    team_b.extend(pool[2:4])
                else:
                    team_a.extend(random.sample(pool, 2))
                    team_b.extend(random.sample(pool, 2))
            random.shuffle(team_a)
            random.shuffle(team_b)
            return team_a + team_b
        else:
            available_heroes = heroes[:]
            if self.rb_unique.isChecked():
                random.shuffle(available_heroes)
                return available_heroes
            else:
                team_a = random.sample(available_heroes, 6)
                team_b = random.sample(available_heroes, 6)
                return team_a + team_b

    def get_available_heroes(self, used_heroes, clicked_slot):
        global_used = set(used_heroes)
        is_team_a = clicked_slot in self.all_slots[:6]
        team_slots = self.all_slots[:6] if is_team_a else self.all_slots[6:]
        current_hero = clicked_slot.name.text()
        team_used = {s.name.text() for s in team_slots if s.name.text() != "Hero"}
        if current_hero != "Hero":
            team_used.discard(current_hero)

        if self.cb_222.isChecked():
            counts = {"Duelist": 0, "Strategist": 0, "Vanguard": 0}
            for h in team_used:
                role = self.get_role(h)
                if role:
                    counts[role] += 1
            avail = []
            for role, pool in role_map.items():
                if counts[role] < 2:
                    for h in pool:
                        if self.rb_unique.isChecked():
                            if h not in global_used:
                                avail.append(h)
                        else:
                            if h not in team_used:
                                avail.append(h)
            return avail if avail else []
        else:
            available_heroes = heroes[:]
            if self.rb_unique.isChecked():
                return [h for h in available_heroes if h not in global_used]
            else:
                return [h for h in available_heroes if h not in team_used]

    def reroll_single(self, slot):
        used_heroes = {s.name.text() for s in self.all_slots if s.name.text() != "Hero"}
        current_hero = slot.name.text()
        if current_hero != "Hero":
            used_heroes.discard(current_hero)
        avail = self.get_available_heroes(used_heroes, slot)
        if not avail:
            return
        new = random.choice(avail)
        if self.rb_animated.isChecked():
            self.sound_player.play_loop()

            QTimer.singleShot(2200, self.sound_player.stop_loop)

            self.spin_slot(slot, new)
        else:
            slot.set_hero(new)
            slot.pulse()

    def spin_slot(self, slot, final_hero):
        timer = QTimer(self)
        timer.slot = slot
        timer.final = final_hero
        timer.step = 0
        def spin():
            timer.step += 1
            h = random.choice(heroes)
            slot.set_hero(h)
            if timer.step > 18:
                timer.setInterval(timer.interval() + 14)
        timer.timeout.connect(spin)
        timer.start(45)
        self.timers.append(timer)
        QTimer.singleShot(random.randint(1600, 2600), lambda: self.land(timer, slot, final_hero))

    def land(self, timer, slot, hero):
        if timer in self.timers:
            timer.stop()
            self.timers.remove(timer)
        slot.set_hero(hero)
        slot.pulse()

    def randomize_teams(self):
        if self.rb_animated.isChecked():
            if self.animation_running:
                self.stop_all()
            else:
                self.start_full_spin()
        else:
            self._randomize_instant()

    def _randomize_instant(self):
        self.stop_all()
        names = [s.username.text().strip() or f"Player {i+1}" for i, s in enumerate(self.all_slots)]
        if self.cb_shuffle.isChecked():
            random.shuffle(names)
        heroes = self.generate_heroes()
        for slot, hero, name in zip(self.all_slots, heroes, names):
            slot.set_hero(hero)
            slot.username.setText(name)

    def start_full_spin(self):
        self.randomize_btn.setEnabled(False)
        if self.button_cooldown:  # Prevent starting if in cooldown
            return

        self.animation_running = True
        self.randomize_btn.setText("Randomization in Progress...")
        self.randomize_btn.setStyleSheet("""
            QPushButton {
                background: #ff5252;
                color: white;
                font-weight: bold;
                border-radius: 26px;
                border: none;
            }
        """)
        self.sound_player.play_loop()
        self.timers.clear()

        names = [s.username.text().strip() or f"Player {i + 1}" for i, s in enumerate(self.all_slots)]
        if self.cb_shuffle.isChecked():
            random.shuffle(names)
        final = self.generate_heroes()

        for i, (slot, hero, name) in enumerate(zip(self.all_slots, final, names)):
            delay = i * 200
            QTimer.singleShot(delay, lambda s=slot, h=hero: self.spin_slot(s, h))
            QTimer.singleShot(delay + 2200, lambda s=slot, n=name: s.username.setText(n))

        QTimer.singleShot(4500, self.finish_spin)

    def finish_spin(self):
        if self.animation_running:
            self.animation_running = False
            self.randomize_btn.setText("Randomize Teams")
            # ← FIXED: Use the exact same normal style as initial and stop_all
            self.randomize_btn.setStyleSheet("""
                QPushButton {
                    background: #f3e8ff;
                    color: #4a148c;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 26px;
                    border: 3px solid #d8b4ff;
                }
            """)
            self.sound_player.stop_loop()
            self.randomize_btn.setEnabled(True)

    def stop_all(self):
        for t in self.timers[:]:
            if t.isActive():
                t.stop()
            self.timers.remove(t)

        self.animation_running = False
        self.randomize_btn.setText("Randomize Teams")
        self.randomize_btn.setStyleSheet("""
            QPushButton {
                background: #f3e8ff;
                color: #4a148c;
                font-size: 16px;
                font-weight: bold;
                border-radius: 26px;
                border: 3px solid #d8b4ff;
            }
        """)
        self.sound_player.stop_loop()

        self.button_cooldown = True
        self.randomize_btn.setEnabled(False)
        QTimer.singleShot(800, lambda: (
            setattr(self, "button_cooldown", False),
            self.randomize_btn.setEnabled(True)
        ))
        self.randomize_btn.setEnabled(True)