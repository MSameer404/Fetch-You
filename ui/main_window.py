"""
main_window.py — Main dashboard for Fetch You.
"""

import os
from PyQt6.QtCore import Qt, QVariantAnimation, QEasingCurve, QPoint, QSize
from PyQt6.QtGui import QFont, QLinearGradient, QColor, QPainter, QPixmap, QPen, QFontDatabase
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy,
    QGraphicsDropShadowEffect,
)

from ui.download_dialog import DownloadDialog


# ──────────────────────────────────────────────────────────────
# Strikethrough Label for stylish titles
# ──────────────────────────────────────────────────────────────
class StrikethroughLabel(QLabel):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#FA709A"), 4)
        painter.setPen(pen)
        
        y = self.height() // 2 + 8
        metrics = self.fontMetrics()
        w = metrics.horizontalAdvance(self.text())
        start_x = (self.width() - w) // 2
        painter.drawLine(start_x, y, start_x + w, y)


# ──────────────────────────────────────────────────────────────
# Animated platform card
# ──────────────────────────────────────────────────────────────
class PlatformCard(QFrame):
    """A clickable card for each platform with lift animation on hover."""

    def __init__(self, platform: str, icon: str, desc: str,
                 color_start: str, color_end: str, parent=None):
        super().__init__(parent)
        self.platform = platform
        self._setup(icon, desc, color_start, color_end)

        # Lift & Shadow Animation setup
        self._hover_anim = QVariantAnimation(self)
        self._hover_anim.setDuration(250)
        self._hover_anim.setStartValue(0.0)
        self._hover_anim.setEndValue(1.0)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_anim.valueChanged.connect(self._animate_hover_state)

    def _setup(self, icon: str, desc: str, c1: str, c2: str):
        self.setObjectName("card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(200, 220)

        self._grad_c1 = c1
        self._grad_c2 = c2

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 24, 16, 24)

        # Icon circle
        icon_bg = QFrame()
        icon_bg.setFixedSize(70, 70)
        icon_bg.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {c1}, stop:1 {c2});"
            "border-radius: 35px;"
        )
        icon_layout = QVBoxLayout(icon_bg)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 28))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent; color: white;")
        icon_layout.addWidget(icon_lbl)
        layout.addWidget(icon_bg, alignment=Qt.AlignmentFlag.AlignCenter)

        name_lbl = QLabel(self.platform)
        name_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet("color: #F3F4F6; background: transparent;")
        layout.addWidget(name_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setStyleSheet("color: #6B7280; font-size: 11px; background: transparent;")
        layout.addWidget(desc_lbl)

        # Drop shadow
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setOffset(0, 8)
        self.shadow.setColor(QColor(0, 0, 0, 140))
        self.setGraphicsEffect(self.shadow)

    def _animate_hover_state(self, val: float):
        # Scale shadow responsiveness
        self.shadow.setBlurRadius(int(30 + (val * 15)))
        self.shadow.setOffset(0, int(8 + (val * 8)))
        
        # Subtle color boundary change
        if val > 0.1:
            self.setStyleSheet(
                f"QFrame#card {{ background-color: #161824; border: 1.5px solid {self._grad_c1};"
                " border-radius: 20px; }"
            )
        else:
            self.setStyleSheet("")

    def enterEvent(self, event):
        self._hover_anim.setDirection(QVariantAnimation.Direction.Forward)
        if self._hover_anim.state() != QVariantAnimation.State.Running:
            self._hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover_anim.setDirection(QVariantAnimation.Direction.Backward)
        if self._hover_anim.state() != QVariantAnimation.State.Running:
            self._hover_anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dlg = DownloadDialog(self.platform, self.window())
            dlg.exec()
        super().mousePressEvent(event)


# ──────────────────────────────────────────────────────────────
# Gradient dashboard background
# ──────────────────────────────────────────────────────────────
class GradientBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Smooth full screen radial/linear gradient
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor("#08090C"))
        grad.setColorAt(0.4, QColor("#121422"))
        grad.setColorAt(1.0, QColor("#08090C"))
        painter.fillRect(self.rect(), grad)

        # Dynamic ambient orbs
        painter.setPen(Qt.PenStyle.NoPen)
        
        glow1 = QColor("#7C3AED")
        glow1.setAlpha(20)
        painter.setBrush(glow1)
        painter.drawEllipse(QPoint(int(self.width() * 0.1), int(self.height() * 0.2)), 250, 250)

        glow2 = QColor("#4F46E5")
        glow2.setAlpha(15)
        painter.setBrush(glow2)
        painter.drawEllipse(QPoint(int(self.width() * 0.9), int(self.height() * 0.8)), 300, 300)


# ──────────────────────────────────────────────────────────────
# Main Window
# ──────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fetch You")
        self.setMinimumSize(850, 600)
        self.resize(950, 650)
        self._build_ui()

    def _build_ui(self):
        # Use full window gradient wrapper
        central = GradientBackground(self)
        self.setCentralWidget(central)
        
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 20, 0, 20)
        root.setSpacing(10)

        # ── Header Section ───────────────────────────────────
        banner_layout = QVBoxLayout()
        banner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        banner_layout.setSpacing(6)

        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setSpacing(15)

        font_path = os.path.join(os.path.dirname(__file__), "HARRYP__.TTF")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            loaded_families = QFontDatabase.applicationFontFamilies(font_id)
            harry_font_name = loaded_families[0] if loaded_families else "Harry P"
        else:
            harry_font_name = "Impact"

        lbl_style = (
            f"font-family: '{harry_font_name}'; font-size: 110px; font-weight: bold;"
            "color: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #FA709A, stop:1 #FEE140); background: transparent;"
        )
        lbl_font = QFont(harry_font_name, 110)

        fetch_lbl = QLabel("Fetch")
        fetch_lbl.setFont(lbl_font)
        fetch_lbl.setStyleSheet(lbl_style)
        header_layout.addWidget(fetch_lbl)

        you_lbl = QLabel("You")
        you_lbl.setFont(lbl_font)
        you_lbl.setStyleSheet(lbl_style)
        header_layout.addWidget(you_lbl)

        banner_layout.addLayout(header_layout)

        tagline = QLabel("A software to Fetch Videos from Your Favourite Sites")
        tagline.setObjectName("lbl_tagline")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("color: #9CA3AF; font-size: 15px; background: transparent;")
        banner_layout.addWidget(tagline)

        root.addLayout(banner_layout)
        root.addSpacing(20)

        # ── Platform Cards Row ───────────────────────────────
        cards_section = QWidget()
        cards_section.setStyleSheet("background: transparent;")
        cards_layout = QHBoxLayout(cards_section)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cards_layout.setSpacing(24)
        cards_layout.setContentsMargins(40, 0, 40, 0)

        platforms = [
            ("YouTube",   "▶",  "Watch & download\nYouTube videos",  "#FF0000", "#CC0000"),
            ("Reddit",    "🤖", "Save Reddit\nvideo posts",          "#FF4500", "#D93900"),
            ("Twitter",   "🐦", "Download Twitter\nvideo clips",     "#1DA1F2", "#0D7DC7"),
            ("Instagram", "📸", "Grab Instagram\nreels & videos",    "#E1306C", "#833AB4"),
        ]
        for name, icon, desc, c1, c2 in platforms:
            card = PlatformCard(name, icon, desc, c1, c2, self)
            cards_layout.addWidget(card)

        root.addWidget(cards_section)
        root.addSpacing(20)


        # ── Footer ───────────────────────────────────────────
        footer = QLabel("Powered by yt-dlp  ·  Built with PyQt6")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #4B5563; font-size: 12px; padding-top: 10px;")
        root.addWidget(footer)

