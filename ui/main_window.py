"""
ui/main_window.py — App shell with sidebar navigation between trees.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame, QGraphicsDropShadowEffect,
    QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QFontDatabase

# -- Matching Palette from Health Tab --
C_BG       = "#050a0f"       # Deep Obsidian
C_SIDEBAR  = "rgba(10, 25, 35, 240)" 
C_ACCENT   = "#00d4ff"       # Electric Blue
C_TEXT     = "#ffffff"
C_MUTED    = "#507a8a"
C_HOVER    = "rgba(0, 212, 255, 30)"
C_SELECTED = "rgba(0, 212, 255, 60)"

TREES = [
    ("health",    "STATUS: HEALTH"),
    ("knowledge", "STATUS: KNOWLEDGE"),
    ("speech",    "STATUS: SPEECH"),
    ("purpose",   "STATUS: PURPOSE"),
    ("finance",   "STATUS: FINANCE"),
]

NAV_STYLE = f"""
    QPushButton {{
        background: transparent;
        color: {C_MUTED};
        border: none;
        border-left: 3px solid transparent;
        padding: 15px 20px;
        text-align: left;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 1px;
    }}
    QPushButton:hover {{
        background: {C_HOVER};
        color: {C_TEXT};
    }}
    QPushButton:checked {{
        background: {C_SELECTED};
        color: {C_ACCENT};
        border-left: 3px solid {C_ACCENT};
    }}
"""

#SIDEBAR_STYLE = "background-color: #1e1e2e; border-right: 1px solid #313244;"
#MAIN_STYLE    = "background-color: #181825;"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Life RPG")
        self.setMinimumSize(1100, 720)
        self.setStyleSheet(f"background-color: {C_BG};")

        root = QWidget()
        root.setStyleSheet("background-color: #181825; color: #cdd6f4;")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Sidebar ────────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {C_SIDEBAR};
                border-right: 1px solid {C_ACCENT};
            }}
        """)
        # Add a subtle glow to the sidebar border
        sidebar_shadow = QGraphicsDropShadowEffect()
        sidebar_shadow.setBlurRadius(20)
        sidebar_shadow.setColor(QColor(0, 212, 255, 40))
        sidebar_shadow.setOffset(2, 0)
        sidebar.setGraphicsEffect(sidebar_shadow)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 24, 0, 24)
        sidebar_layout.setSpacing(2)

        # Title: Styled like a System Header
        title = QLabel("THE SYSTEM")
        title.setStyleSheet(f"""
            color: {C_ACCENT}; 
            padding: 10px; 
            font-size: 18px; 
            font-weight: bold;
            letter-spacing: 4px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)

        # Decorative Subtitle
        subtitle = QLabel("PLAYER: Dandelion (RANK E)") # Fun flavor text
        subtitle.setStyleSheet(f"color: {C_MUTED}; font-size: 9px; padding-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(subtitle)

        # ── Stack (Main Content Area) ──────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;") # Tabs handle their own BG
        self._load_tabs()

        '''
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #313244;")
        sidebar_layout.addWidget(sep)
        sidebar_layout.addSpacing(8)
        '''

        # Nav buttons
        self.nav_buttons = []
        for i, (key, label) in enumerate(TREES):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet(NAV_STYLE)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self._switch(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()
        
        layout.addWidget(sidebar)
        layout.addWidget(self.stack)

        self._switch(0)  # Start on Health

    def _load_tabs(self):
        from ui.health_tab import HealthTab
        from ui.placeholder_tab import PlaceholderTab

        self.stack.addWidget(HealthTab())                         # 0 health
        self.stack.addWidget(PlaceholderTab("📚", "Knowledge"))  # 1
        self.stack.addWidget(PlaceholderTab("🗣️", "Speech"))     # 2
        self.stack.addWidget(PlaceholderTab("🚀", "Purpose"))    # 3
        self.stack.addWidget(PlaceholderTab("💰", "Finance"))    # 4

    def _switch(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)