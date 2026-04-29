"""
download_dialog.py — Pop-up dialog for video info & download.
"""

import os
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QProgressBar, QFrame, QSizePolicy,
    QScrollArea, QWidget, QMessageBox, QFileDialog,
)

from backend.fetcher import fetch_metadata
from backend.downloader import DownloadWorker


# ──────────────────────────────────────────────────────────────
# Metadata fetch worker (runs in thread so UI stays alive)
# ──────────────────────────────────────────────────────────────
class FetchWorker(QThread):
    done = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            data = fetch_metadata(self.url)
            self.done.emit(data)
        except Exception as exc:
            self.error.emit(str(exc))


# ──────────────────────────────────────────────────────────────
# Main Dialog
# ──────────────────────────────────────────────────────────────
class DownloadDialog(QDialog):
    """
    Platform-agnostic pop-up that:
      1. Accepts a URL
      2. Fetches metadata
      3. Shows video details
      4. Lets the user pick quality and download
    """

    def __init__(self, platform: str, parent=None):
        super().__init__(parent)
        self.platform = platform
        self.metadata: dict = {}
        self.download_worker: DownloadWorker | None = None
        self.fetch_worker: FetchWorker | None = None

        self.setWindowTitle(f"Fetch You — {platform}")
        self.setMinimumWidth(620)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._build_ui()

    # ── UI Construction ──────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(18)

        # Header row
        hdr = QHBoxLayout()
        icon_lbl = QLabel(self._platform_icon())
        icon_lbl.setFont(QFont("Segoe UI Emoji", 26))
        platform_lbl = QLabel(self.platform)
        platform_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        platform_lbl.setStyleSheet("color: #FFFFFF;")
        hdr.addWidget(icon_lbl)
        hdr.addWidget(platform_lbl)
        hdr.addStretch()
        root.addLayout(hdr)

        # URL input row
        url_row = QHBoxLayout()
        url_row.setSpacing(10)
        self.url_input = QLineEdit()
        self.url_input.setObjectName("url_input")
        self.url_input.setPlaceholderText(f"Paste {self.platform} video URL here…")
        self.url_input.returnPressed.connect(self._on_fetch)
        url_row.addWidget(self.url_input, 1)

        self.fetch_btn = QPushButton("Fetch Info")
        self.fetch_btn.setObjectName("btn_fetch")
        self.fetch_btn.setFixedWidth(110)
        self.fetch_btn.clicked.connect(self._on_fetch)
        url_row.addWidget(self.fetch_btn)
        root.addLayout(url_row)

        # Status label (spinner / errors)
        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: #6B7280; font-size: 12px;")
        self.status_lbl.hide()
        root.addWidget(self.status_lbl)

        # ── Info Card ────────────────────────────────────────
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.hide()
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        # Title
        self.title_lbl = QLabel()
        self.title_lbl.setObjectName("lbl_video_title")
        self.title_lbl.setWordWrap(True)
        card_layout.addWidget(self.title_lbl)

        # Meta row (duration only)
        self.meta_lbl = QLabel()
        self.meta_lbl.setObjectName("lbl_meta")
        card_layout.addWidget(self.meta_lbl)

        # Quality selector row
        quality_section = QLabel("QUALITY / FORMAT")
        quality_section.setObjectName("lbl_section_title")
        card_layout.addWidget(quality_section)

        fmt_row = QHBoxLayout()
        self.format_combo = QComboBox()
        fmt_row.addWidget(self.format_combo, 1)
        card_layout.addLayout(fmt_row)

        root.addWidget(self.card)

        # ── Progress area ────────────────────────────────────
        self.progress_frame = QFrame()
        self.progress_frame.hide()
        prog_layout = QVBoxLayout(self.progress_frame)
        prog_layout.setContentsMargins(0, 0, 0, 0)
        prog_layout.setSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        prog_layout.addWidget(self.progress_bar)

        self.dl_status_lbl = QLabel("Starting download…")
        self.dl_status_lbl.setStyleSheet("color: #6B7280; font-size: 11px;")
        self.dl_status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prog_layout.addWidget(self.dl_status_lbl)

        root.addWidget(self.progress_frame)

        # ── Bottom buttons ───────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.setStyleSheet(
            "QPushButton { background: #1C1E28; border: 1px solid #2C2F40;"
            "border-radius: 10px; padding: 10px 20px; color: #9CA3AF; font-size: 13px; }"
            "QPushButton:hover { background: #252836; color: #E8EAF0; }"
        )
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)

        self.download_btn = QPushButton("⬇  Download")
        self.download_btn.setObjectName("btn_download")
        self.download_btn.setFixedWidth(160)
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self._on_download)
        btn_row.addWidget(self.download_btn)

        root.addLayout(btn_row)

    # ── Helpers ─────────────────────────────────────────────
    def _platform_icon(self) -> str:
        icons = {"YouTube": "▶", "Reddit": "🤖", "Twitter": "🐦", "Instagram": "📸"}
        return icons.get(self.platform, "🌐")

    def _set_fetching(self, active: bool):
        self.fetch_btn.setEnabled(not active)
        self.url_input.setEnabled(not active)
        if active:
            self.status_lbl.setText("⏳  Fetching video info…")
            self.status_lbl.show()
            self.card.hide()
            self.download_btn.setEnabled(False)
        else:
            self.status_lbl.hide()

    # ── Slots ────────────────────────────────────────────────
    def _on_fetch(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "No URL", "Please paste a video URL first.")
            return

        self._set_fetching(True)

        self.fetch_worker = FetchWorker(url, self)
        self.fetch_worker.done.connect(self._on_metadata_ready)
        self.fetch_worker.error.connect(self._on_fetch_error)
        self.fetch_worker.start()

    def _on_metadata_ready(self, data: dict):
        self.metadata = data
        self._set_fetching(False)

        self.title_lbl.setText(data["title"])
        self.meta_lbl.setText(f"⏱ Duration: {data['duration']}")

        # Populate quality combo
        self.format_combo.clear()
        for fmt in data["formats"]:
            size = fmt["filesize"]
            size_str = f"  ({size / 1_048_576:.1f} MB)" if size else ""
            label = f"{fmt['resolution']}  [{fmt['ext']}]{size_str}"
            self.format_combo.addItem(label, userData=fmt["format_id"])

        self.card.show()
        self.download_btn.setEnabled(True)


    def _on_fetch_error(self, msg: str):
        self._set_fetching(False)
        self.status_lbl.setText(f"❌  {msg[:120]}")
        self.status_lbl.setStyleSheet("color: #EF4444; font-size: 12px;")
        self.status_lbl.show()

    def _on_download(self):
        if not self.metadata:
            return

        # Ask for save directory
        save_dir = QFileDialog.getExistingDirectory(
            self, "Choose Download Folder",
            os.path.expanduser("~/Downloads"),
        )
        if not save_dir:
            return

        fmt_id = self.format_combo.currentData() or "bestvideo+bestaudio/best"
        url = self.metadata["webpage_url"]

        self.download_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_frame.show()
        self.dl_status_lbl.setText("Starting download…")

        self.download_worker = DownloadWorker(url, fmt_id, save_dir, self)
        self.download_worker.progress.connect(self.progress_bar.setValue)
        self.download_worker.speed.connect(self._on_speed)
        self.download_worker.eta.connect(self._on_eta)
        self.download_worker.finished.connect(self._on_download_done)
        self.download_worker.error.connect(self._on_download_error)
        self.download_worker.start()

    def _on_speed(self, spd: str):
        self.dl_status_lbl.setText(f"Downloading at {spd}…")

    def _on_eta(self, eta: str):
        current = self.dl_status_lbl.text().split("·")[0].strip()
        self.dl_status_lbl.setText(f"{current}  ·  ETA {eta}")

    def _on_download_done(self, path: str):
        self.progress_bar.setValue(100)
        self.dl_status_lbl.setText("✅  Download complete!")
        fname = os.path.basename(path)
        QMessageBox.information(
            self, "Done!",
            f"<b>{fname}</b><br>saved to:<br>{os.path.dirname(path)}",
        )
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        self.url_input.setEnabled(True)

    def _on_download_error(self, msg: str):
        self.dl_status_lbl.setText(f"❌  {msg[:120]}")
        self.dl_status_lbl.setStyleSheet("color: #EF4444; font-size: 11px;")
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        self.url_input.setEnabled(True)

    def closeEvent(self, event):
        # Gracefully stop any running workers
        for worker in (self.fetch_worker, self.download_worker):
            if worker and worker.isRunning():
                worker.terminate()
                worker.wait(2000)
        super().closeEvent(event)
