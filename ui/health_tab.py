"""
ui/health_tab.py — Full Health tree UI.

Sections:
  1. XP / Level bar
  2. Gym tracker — monthly calendar + streak
  3. Meditation tracker — type selector, log, recent history
  4. Objectives checklist
"""

import calendar
from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QComboBox, QSpinBox,
    QTextEdit, QSizePolicy, QDialog, QDialogButtonBox,
    QGraphicsDropShadowEffect, QApplication
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QFontDatabase

import models
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

# ── Palette ────────────────────────────────────────────────────────────────
C_BG       = "#050a0f"
C_SURFACE  = "rgba(10, 25, 35, 200)" # Glassmorphism effect
C_SURFACE2 = "rgba(20, 45, 65, 150)"
C_TEXT     = "#ffffff"
C_MUTED    = "#6c7086"
C_ACCENT   = "#00d4ff"       # Electric Blue
C_BORDER   = "#00d4ff"
C_MUTED    = "#507a8a"
C_GREEN    = "#a6e3a1"
C_RED      = "#f38ba8"
C_YELLOW   = "#f9e2af"
C_BLUE     = "#89b4fa"


def card(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setStyleSheet(f"""
        QFrame {{
            background: {C_SURFACE};
            border: 1px solid {C_BORDER};
            border-top: 3px solid {C_ACCENT};
            border-radius: 0px;
            padding: 8px;
        }}
    """)
    # Add the glow effect
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setColor(QColor(0, 212, 255, 100))
    shadow.setOffset(0, 0)
    f.setGraphicsEffect(shadow)
    
    return f


def h_label(text, size=13, bold=False, color=C_TEXT) -> QLabel:
    lbl = QLabel(text)
    font = QFont(["Consolas", "Monospace", "Courier New"], size)
    if bold:
        font.setWeight(QFont.Weight.Bold)
    lbl.setFont(font)
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    return lbl


# ── XP Bar ─────────────────────────────────────────────────────────────────

class XPBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(64)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.level_lbl = h_label("LVL 1", 20, bold=True, color=C_ACCENT)
        self.level_lbl.setFixedWidth(80)

        bar_col = QVBoxLayout()
        self.xp_lbl = h_label("0 / 100 XP", 10, color=C_MUTED)
        self.bar_bg = QFrame()
        self.bar_bg.setFixedHeight(10) # Thinner is more modern/HUD-like
        self.bar_bg.setStyleSheet(f"background: #0d2a35; border: 1px solid {C_ACCENT}; border-radius: 0px;")
        self.bar_fill = QFrame(self.bar_bg)
        self.bar_fill.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #005f73, stop:1 {C_ACCENT});
            border-radius: 0px;
        """)
        bar_col.addWidget(self.xp_lbl)
        bar_col.addWidget(self.bar_bg)

        layout.addWidget(self.level_lbl)
        layout.addLayout(bar_col)

    def refresh(self):
        tree = models.get_tree("health")
        if not tree:
            return
        pct = tree["xp"] / tree["xp_per_lvl"]
        self.level_lbl.setText(f"LVL {tree['level']}")
        self.xp_lbl.setText(f"{tree['xp']} / {tree['xp_per_lvl']} XP")
        self.bar_bg.resizeEvent = lambda e: self._resize_fill(pct)
        self._resize_fill(pct)

    def _resize_fill(self, pct):
        w = int(self.bar_bg.width() * pct)
        self.bar_fill.setFixedWidth(max(w, 0))


# ── Gym Calendar ───────────────────────────────────────────────────────────

class GymCalendar(QWidget):
    def __init__(self):
        super().__init__()
        self._year  = date.today().year
        self._month = date.today().month
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header row
        header = QHBoxLayout()
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedWidth(32)
        self.prev_btn.setStyleSheet(f"color:{C_ACCENT}; background:transparent; border:none; font-size:16px;")
        self.prev_btn.clicked.connect(self._prev_month)

        self.month_lbl = h_label("", 13, bold=True, color=C_TEXT)
        self.month_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedWidth(32)
        self.next_btn.setStyleSheet(f"color:{C_ACCENT}; background:transparent; border:none; font-size:16px;")
        self.next_btn.clicked.connect(self._next_month)

        header.addWidget(self.prev_btn)
        header.addWidget(self.month_lbl, 1)
        header.addWidget(self.next_btn)
        layout.addLayout(header)

        # Day-of-week labels
        dow_row = QHBoxLayout()
        for d in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            lbl = h_label(d, 10, color=C_MUTED)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dow_row.addWidget(lbl)
        layout.addLayout(dow_row)

        # Grid placeholder — rebuilt on refresh
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(4)
        layout.addWidget(self.grid_widget)

        # Streak
        self.streak_lbl = h_label("🔥 Streak: 0 days", 12, color=C_YELLOW)
        self.streak_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.streak_lbl)

        # Today button
        today_btn = QPushButton("✅  Log Today's Session")
        today_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; 
                color: {C_ACCENT};
                border: 1px solid {C_ACCENT};
                padding: 10px;
                font-family: 'Consolas', 'Monospace', monospace;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background: rgba(0, 212, 255, 40);
            }}
        """)
        today_btn.clicked.connect(self._log_today)
        layout.addWidget(today_btn)

        self.refresh()

    def refresh(self):
        # Clear grid
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().deleteLater()

        logged = set(models.get_gym_logs(self._year, self._month))
        today_str = date.today().isoformat()
        cal = calendar.monthcalendar(self._year, self._month)

        self.month_lbl.setText(date(self._year, self._month, 1).strftime("%B %Y"))

        for row, week in enumerate(cal):
            for col, day in enumerate(week):
                if day == 0:
                    self.grid_layout.addWidget(QLabel(""), row, col)
                    continue
                day_str = f"{self._year:04d}-{self._month:02d}-{day:02d}"
                btn = QPushButton(str(day))
                btn.setFixedSize(36, 36)
                is_logged = day_str in logged
                is_today  = day_str == today_str

                if is_logged:
                    style = f"background:{C_GREEN}; color:#1e1e2e; border-radius:18px; font-weight:bold;"
                elif is_today:
                    style = f"background:{C_SURFACE2}; color:{C_ACCENT}; border-radius:18px; border:2px solid {C_ACCENT};"
                else:
                    style = f"background:{C_SURFACE2}; color:{C_MUTED}; border-radius:18px;"

                btn.setStyleSheet(style)
                btn.clicked.connect(lambda _, ds=day_str, il=is_logged: self._toggle(ds, il))
                self.grid_layout.addWidget(btn, row, col)

        self.streak_lbl.setText(f"🔥 Streak: {models.get_gym_streak()} days")

    def _toggle(self, day_str: str, is_logged: bool):
        if is_logged:
            models.remove_gym_log(day_str)
        else:
            models.log_gym(day_str)
        self.refresh()

    def _log_today(self):
        models.log_gym()
        self.refresh()

    def _prev_month(self):
        if self._month == 1:
            self._month, self._year = 12, self._year - 1
        else:
            self._month -= 1
        self.refresh()

    def _next_month(self):
        if self._month == 12:
            self._month, self._year = 1, self._year + 1
        else:
            self._month += 1
        self.refresh()


# ── Meditation Panel ────────────────────────────────────────────────────────

class MeditationInfoDialog(QDialog):
    def __init__(self, med_type: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(med_type["name"])
        self.setMinimumWidth(420)
        self.setStyleSheet(f"background:{C_SURFACE}; color:{C_TEXT};")
        layout = QVBoxLayout(self)

        layout.addWidget(h_label(med_type["name"], 16, bold=True, color=C_ACCENT))
        layout.addWidget(h_label(med_type["description"], 11, color=C_MUTED))
        layout.addSpacing(8)

        summary = QLabel(med_type["summary"])
        summary.setWordWrap(True)
        summary.setStyleSheet(f"color:{C_TEXT}; font-size:12px; line-height:1.5;")
        layout.addWidget(summary)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.setStyleSheet(f"color:{C_TEXT};")
        btns.accepted.connect(self.accept)
        layout.addWidget(btns)


class MeditationPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._types = models.get_meditation_types()
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Type selector row
        type_row = QHBoxLayout()
        type_row.addWidget(h_label("Type:", 12))
        self.type_combo = QComboBox()
        self.type_combo.setStyleSheet(f"""
            QComboBox {{
                background:{C_SURFACE2}; color:{C_TEXT};
                border-radius:6px; padding:4px 8px; min-width:160px;
            }}
            QComboBox QAbstractItemView {{ background:{C_SURFACE2}; color:{C_TEXT}; }}
        """)
        for mt in self._types:
            self.type_combo.addItem(mt["name"], mt["id"])
        type_row.addWidget(self.type_combo)

        info_btn = QPushButton("ℹ️  Info")
        info_btn.setStyleSheet(f"background:transparent; color:{C_BLUE}; border:none;")
        info_btn.clicked.connect(self._show_info)
        type_row.addWidget(info_btn)
        type_row.addStretch()
        layout.addLayout(type_row)

        # Duration
        dur_row = QHBoxLayout()
        dur_row.addWidget(h_label("Duration (min):", 12))
        self.dur_spin = QSpinBox()
        self.dur_spin.setRange(1, 120)
        self.dur_spin.setValue(10)
        self.dur_spin.setStyleSheet(f"""
            QSpinBox {{ background:{C_SURFACE2}; color:{C_TEXT};
                        border-radius:6px; padding:4px 8px; }}
        """)
        dur_row.addWidget(self.dur_spin)
        dur_row.addStretch()
        layout.addLayout(dur_row)

        # Notes
        layout.addWidget(h_label("Notes (optional):", 11, color=C_MUTED))
        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(60)
        self.notes_edit.setStyleSheet(f"""
            QTextEdit {{ background:{C_SURFACE2}; color:{C_TEXT};
                         border-radius:6px; padding:6px; font-size:12px; }}
        """)
        layout.addWidget(self.notes_edit)

        # Log button
        log_btn = QPushButton("🧘  Log Meditation")
        log_btn.setStyleSheet(f"""
            QPushButton {{
                background:{C_BLUE}; color:#1e1e2e;
                border-radius:8px; padding:8px; font-weight:bold;
            }}
            QPushButton:hover {{ background:#74a8f7; }}
        """)
        log_btn.clicked.connect(self._log)
        layout.addWidget(log_btn)

        # Recent log
        layout.addWidget(h_label("Recent sessions:", 11, color=C_MUTED))
        self.log_list = QVBoxLayout()
        self.log_list.setSpacing(4)
        log_container = QWidget()
        log_container.setLayout(self.log_list)
        layout.addWidget(log_container)

        self._refresh_log()

    def _show_info(self):
        idx = self.type_combo.currentIndex()
        if 0 <= idx < len(self._types):
            dlg = MeditationInfoDialog(self._types[idx], self)
            dlg.exec()

    def _log(self):
        type_id  = self.type_combo.currentData()
        duration = self.dur_spin.value()
        notes    = self.notes_edit.toPlainText().strip()
        models.log_meditation(type_id, duration, notes)
        models.add_xp("health", 10)
        self.notes_edit.clear()
        self._refresh_log()

    def _refresh_log(self):
        for i in reversed(range(self.log_list.count())):
            self.log_list.itemAt(i).widget().deleteLater()

        logs = models.get_meditation_logs(limit=6)
        for entry in logs:
            row = QHBoxLayout()
            lbl = h_label(
                f"  {entry['date']}  ·  {entry['type_name']}  ·  {entry['duration']} min",
                11, color=C_TEXT
            )
            row.addWidget(lbl)
            w = QWidget()
            w.setLayout(row)
            w.setStyleSheet(f"background:{C_SURFACE2}; border-radius:6px;")
            w.setFixedHeight(30)
            self.log_list.addWidget(w)


# ── Objectives ─────────────────────────────────────────────────────────────

class ObjectivesPanel(QWidget):
    def __init__(self, xp_bar: XPBar):
        super().__init__()
        self.xp_bar = xp_bar
        self._build()

    def _build(self):
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setSpacing(6)
        self.refresh()

    def refresh(self):
        for i in reversed(range(self.layout_.count())):
            item = self.layout_.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        objectives = models.get_objectives("health")
        for obj in objectives:
            row = QHBoxLayout()

            check = QPushButton("✅" if obj["completed"] else "⬜")
            check.setFixedSize(32, 32)
            check.setStyleSheet("background:transparent; border:none; font-size:16px;")
            check.clicked.connect(lambda _, o=obj: self._toggle(o))

            title = h_label(obj["title"], 12, bold=not obj["completed"],
                            color=C_MUTED if obj["completed"] else C_TEXT)
            xp_lbl = h_label(f"+{obj['xp_reward']} XP", 10, color=C_ACCENT)
            xp_lbl.setFixedWidth(60)
            xp_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

            desc = h_label(obj["description"] or "", 10, color=C_MUTED)
            desc.setWordWrap(True)

            left = QVBoxLayout()
            left.addWidget(title)
            left.addWidget(desc)

            row.addWidget(check)
            row.addLayout(left, 1)
            row.addWidget(xp_lbl)

            w = QWidget()
            w.setLayout(row)
            c = C_SURFACE2 if obj["completed"] else C_SURFACE
            w.setStyleSheet(f"background:{c}; border-radius:8px; padding:4px;")
            self.layout_.addWidget(w)

    def _toggle(self, obj: dict):
        if obj["completed"]:
            models.uncomplete_objective(obj["id"])
        else:
            result = models.complete_objective(obj["id"], "health")
            if result and result.get("levelled_up"):
                self._show_levelup(result["level"])
        self.xp_bar.refresh()
        self.refresh()

    def _show_levelup(self, new_level: int):
        dlg = QDialog(self)
        dlg.setWindowTitle("Level Up!")
        dlg.setStyleSheet(f"background:{C_SURFACE}; color:{C_TEXT};")
        layout = QVBoxLayout(dlg)
        layout.addWidget(h_label("🎉  Level Up!", 22, bold=True, color=C_ACCENT))
        layout.addWidget(h_label(f"Health tree is now Level {new_level}!", 14, color=C_TEXT))
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(dlg.accept)
        layout.addWidget(btns)
        dlg.exec()


# ── Health Tab ─────────────────────────────────────────────────────────────

class HealthTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{C_BG};")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(16)

        # Title + XP bar
        title = h_label("HEALTH STATUS", 18, bold=True, color=C_ACCENT)
        title.setStyleSheet(f"letter-spacing: 3px; border-bottom: 1px solid {C_ACCENT};")
        outer.addWidget(title)

        self.xp_bar = XPBar()
        outer.addWidget(self.xp_bar)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none; background:transparent;")
        content = QWidget()
        content.setStyleSheet(f"background:{C_BG};")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        # ── Left column: Gym + Meditation ──
        left = QVBoxLayout()
        left.setSpacing(16)

        gym_card = card()
        gym_layout = QVBoxLayout(gym_card)
        gym_layout.addWidget(h_label("🏋️  Gym Tracker", 14, bold=True))
        gym_layout.addSpacing(4)
        self.gym_cal = GymCalendar()
        gym_layout.addWidget(self.gym_cal)
        left.addWidget(gym_card)

        med_card = card()
        med_layout = QVBoxLayout(med_card)
        med_layout.addWidget(h_label("🧘  Meditation", 14, bold=True))
        med_layout.addSpacing(4)
        med_layout.addWidget(MeditationPanel())
        left.addWidget(med_card)
        left.addStretch()

        # ── Right column: Objectives ──
        right = QVBoxLayout()
        obj_card = card()
        obj_layout = QVBoxLayout(obj_card)
        obj_layout.addWidget(h_label("🎯  Objectives", 14, bold=True))
        obj_layout.addSpacing(4)

        self.objectives = ObjectivesPanel(self.xp_bar)
        obj_layout.addWidget(self.objectives)
        obj_layout.addStretch()
        right.addWidget(obj_card)
        right.addStretch()

        content_layout.addLayout(left, 3)
        content_layout.addLayout(right, 2)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.xp_bar.refresh()

    def materialize(self):
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(600)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()