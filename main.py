"""
main.py — Entry point for Fetch You.
"""

import sys
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon

from ui.main_window import MainWindow


def load_stylesheet(app: QApplication):
    qss_path = os.path.join(os.path.dirname(__file__), "ui", "styles.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main():
    # Enable HiDPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Fetch You")
    app.setOrganizationName("FetchYou")

    app.setFont(QFont("Segoe UI", 10))

    # Load local .ico asset
    icon_path = os.path.join(os.path.dirname(__file__), "ui", "logo.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    load_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
