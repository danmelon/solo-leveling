"""
main.py — Entry point for Life RPG.
Run with: python main.py
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

import db
from trees import health as health_tree


def seed_all_trees():
    """Seed data for all trees. Each tree module handles its own INSERT OR IGNORE."""
    health_tree.seed()
    # knowledge_tree.seed() etc. — added as we build each tree


def main():
    # 1. Init database schema
    db.init_db()

    # 2. Seed all trees
    seed_all_trees()

    # 3. Launch app
    app = QApplication(sys.argv)
    app.setApplicationName("Life RPG")
    app.setStyle("Fusion")

    # Dark palette as fallback
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor("#181825"))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Base,            QColor("#1e1e2e"))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#313244"))
    palette.setColor(QPalette.ColorRole.Text,            QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Button,          QColor("#313244"))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor("#cba6f7"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1e1e2e"))
    app.setPalette(palette)

    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()