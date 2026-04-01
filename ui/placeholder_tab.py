"""
ui/placeholder_tab.py — Stub widget shown for trees not yet implemented.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class PlaceholderTab(QWidget):
    def __init__(self, icon: str, name: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Arial", 48))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name_lbl = QLabel(f"{name} Tree")
        name_lbl.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        name_lbl.setStyleSheet("color: #cba6f7;")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        coming_lbl = QLabel("Coming soon — we'll build this next!")
        coming_lbl.setStyleSheet("color: #6c7086; font-size: 14px;")
        coming_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_lbl)
        layout.addWidget(name_lbl)
        layout.addSpacing(8)
        layout.addWidget(coming_lbl)