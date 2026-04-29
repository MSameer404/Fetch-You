"""
downloader.py — Download management with progress reporting.
Runs in a QThread to keep the UI responsive.
"""

import os
import yt_dlp
from PyQt6.QtCore import QThread, pyqtSignal


class DownloadWorker(QThread):
    """
    Worker thread that downloads a video using yt-dlp.

    Signals:
        progress(int)          — Download percentage (0-100)
        speed(str)             — Current speed string, e.g. "1.2 MiB/s"
        eta(str)               — Estimated time remaining, e.g. "0:42"
        finished(str)          — Path to finished file
        error(str)             — Error message on failure
    """

    progress = pyqtSignal(int)
    speed = pyqtSignal(str)
    eta = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url: str, format_id: str, output_dir: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.format_id = format_id
        self.output_dir = output_dir
        self._output_file = ""

    # ------------------------------------------------------------------
    # yt-dlp progress hook
    # ------------------------------------------------------------------
    def _progress_hook(self, d: dict):
        if d["status"] == "downloading":
            # Percentage
            pct_str = d.get("_percent_str", "0%").strip().replace("%", "")
            try:
                pct = int(float(pct_str))
            except ValueError:
                pct = 0
            self.progress.emit(min(pct, 99))

            # Speed
            spd = d.get("_speed_str", "").strip()
            if spd:
                self.speed.emit(spd)

            # ETA
            eta_str = d.get("_eta_str", "").strip()
            if eta_str:
                self.eta.emit(eta_str)

        elif d["status"] == "finished":
            self._output_file = d.get("filename", "")
            self.progress.emit(100)

    # ------------------------------------------------------------------
    # Thread entry point
    # ------------------------------------------------------------------
    def run(self):
        os.makedirs(self.output_dir, exist_ok=True)

        outtmpl = os.path.join(self.output_dir, "%(title)s.%(ext)s")

        ydl_opts = {
            "format": self.format_id,
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "progress_hooks": [self._progress_hook],
            # Merge video+audio when separate streams are chosen
            "merge_output_format": "mp4",
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                if not self._output_file:
                    # Resolve final path ourselves
                    self._output_file = ydl.prepare_filename(info)
            self.finished.emit(self._output_file)
        except Exception as exc:
            self.error.emit(str(exc))
