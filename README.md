# 📥 YouTube Video & Music Downloader

This is a simple Python-based YouTube downloader that allows users to download videos or audio in multiple formats: `mp4`, `m4a`, and `mp3`. It uses the powerful `yt-dlp` library under the hood.

---

## ✨ Features

- Download **videos** in `.mp4` format
- Download **audio** in `.m4a` or **converted** `.mp3`
- Choose format via user input
- Lightweight and fast
- CLI-based interface

---

## ⚙️ Requirements

- Python 3.8 or higher
- Platform: Windows, macOS, or Linux
- Python packages:
  - `yt-dlp`

---

## 🔧 Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/Reines5/YoutubeVideoAndMusicDownloader.git
cd youtube-downloader
```

## 2. Create a virtual environment

Create an isolated Python environment to manage dependencies:
```
python -m venv .venv
```

## 3. Activate the virtual environment

On Windows:
```
.venv\Scripts\activate
```

On macOS/Linux:
```
source .venv/bin/activate
```

## ▶️ How to Run the Project

After activating the virtual environment and installing `yt-dlp`, run:
```
python main.py
```
The program will ask you for the YouTube URL and the desired format:

-`mp4` → Downloads video
-`m4a` → Downloads audio
-`mp3` → Downloads and converts audio to .mp3 (FFmpeg required)

💡 If you plan to download mp3, make sure you have FFmpeg installed and added to your system PATH:

- [Download FFmpeg](https://ffmpeg.org/download.html)



# 📦 Build a Standalone .exe (Optional for Windows)
If you'd like to distribute your downloader as a standalone .exe file with no Python required, follow these steps:

## 1. Install PyInstaller
```
pip install pyinstaller
```

## 2. Build the executable
```
pyinstaller --onefile --console main.py
```

- `--onefile`: packages everything into a single .exe file
- `--console`: keeps the terminal window for interaction
  
The output file will be created in the dist/ folder.

## ❗ Notes
-The tool relies on yt-dlp, which automatically fetches the latest YouTube download logic.
-yt-dlp does not require an API key.
-If the video format you selected isn't available, yt-dlp will choose the closest match.

## 📝 License

This project is licensed under the [MIT License](LICENSE).

## 📬 Contact
Feel free to open an issue if you find bugs or want to suggest improvements.
