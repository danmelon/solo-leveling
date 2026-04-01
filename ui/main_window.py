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


TREES = [
    ("health",    "❤️  Health"),
    ("knowledge", "📚  Knowledge"),
    ("speech",    "🗣️  Speech"),
    ("purpose",   "🚀  Purpose"),
    ("finance",   "💰  Finance"),
]

NAV_STYLE = """
    QPushButton {
        background: transparent;
        color: #cdd6f4;
        border: none;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: left;
        font-size: 14px;
    }
    QPushButton:hover {
        background: #313244;
    }
    QPushButton:checked {
        background: #45475a;
        color: #cba6f7;
        font-weight: bold;
    }
"""

SIDEBAR_STYLE = "background-color: #1e1e2e; border-right: 1px solid #313244;"
MAIN_STYLE    = "background-color: #181825;"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Life RPG")
        self.setMinimumSize(1100, 720)

        root = QWidget()
        root.setStyleSheet("background-color: #181825; color: #cdd6f4;")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Sidebar ────────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(SIDEBAR_STYLE)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 24, 12, 24)
        sidebar_layout.setSpacing(4)

        title = QLabel("🖥️ The System")
        title.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #cba6f7; padding-bottom: 16px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #313244;")
        sidebar_layout.addWidget(sep)
        sidebar_layout.addSpacing(8)

        # ── Stack ──────────────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(MAIN_STYLE)
        self._load_tabs()

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