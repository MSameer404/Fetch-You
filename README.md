# Fetch You

A sleek, modern YouTube and video downloader built with Python and PyQt6.

## ✨ Features
- **Intuitive UI**: Clean, responsive, and easy-to-use interface.
- **High-Resolution Downloads**: Fetch and download videos in various resolutions (from 144p up to 4K/Best Available).
- **Real-Time Progress**: Live updates on download percentage, speed, and ETA.
- **Multithreaded**: Downloads run in the background, keeping the app smooth and responsive.
- **Format Flexibility**: Automatically chooses the best video/audio streams for high-quality merging.

## 🛠️ Tech Stack
- **Frontend**: [PyQt6](https://riverbankcomputing.com/software/pyqt/)
- **Core Engine**: [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **Packaging**: PyInstaller

## 🚀 Getting Started

### Prerequisites
- Python >= 3.13

### Using `uv` (Recommended)
If you have `uv` installed, setting up is a breeze:

```powershell
# Synchronize dependencies
uv sync

# Run the application
uv run main.py
```

### Using Standard `pip`
Alternatively, you can set up a traditional virtual environment:

```powershell
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📦 Building Executable
To package the application into a standalone `.exe` for Windows:

```powershell
pyinstaller main.spec
```

## 📄 License
This project is licensed under the MIT License.

---
*Disclaimer: This tool is intended for personal use and downloading content you have the right to access. Please respect the terms of service of any platform you use this with.*
