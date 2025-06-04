import os
import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys



class YouTubeDownloader:
    url = 'https://www.youtube.com/watch?v=MohURRfBojg'  # İndirmek istediğin video URL'sini buraya yaz
    path = './videos'
    
    # def mp4_download():
    #     ydl_opts = {
    #     'format': 'bestvideo+bestaudio/best',  # En iyi video ve ses kalitesini seç
    #     'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),       # Kaydedilen dosyanın ismi: video başlığı + uzantı
    #     'merge_output_format': 'mp4',
    #     'ffmpeg_location': './ffmpeg_bin/ffmpeg.exe',          # Video ve sesi mp4 olarak birleştir
    #     }

    #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #         ydl.download([url])

    # def mp3_download():
    #     ydl_opts = {
    #         'format': 'bestaudio',
    #         'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
    #         'merge_output_format': 'mp3',
    #         'ffmpeg_location': './ffmpeg_bin/ffmpeg.exe', 
    #     }

    #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #         ydl.download([url])

    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        self.video_url = tk.StringVar()
        self.download_path = tk.StringVar()
        self.format_choice = tk.StringVar(value="mp4")
        self.downloading = False
        self.ydl = None

        self.create_widgets()

    def create_widgets(self):
        #url
        self.video_url = tk.StringVar()
        tk.Label(self.root, text="Video URL").pack(pady=5)
        tk.Entry(self.root, textvariable=self.video_url, width=60).pack()

        # Format Seçimi
        tk.Label(self.root, text="Format").pack(pady=5)
        format_menu = ttk.Combobox(self.root, textvariable=self.format_choice, values=["mp4", "m4a"], state="readonly")
        format_menu.pack()

        # İndirme Konumu
        tk.Button(self.root, text="Klasör Seç", command=self.select_folder).pack(pady=5)
        tk.Label(self.root, textvariable=self.download_path).pack()

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, length=400)
        self.progress.pack(pady=10)

        # Butonlar
        self.download_btn = tk.Button(self.root, text="İndir", command=self.start_download)
        self.download_btn.pack(side="left", padx=40)

        self.cancel_btn = tk.Button(self.root, text="İptal Et", command=self.cancel_download, state="disabled")
        self.cancel_btn.pack(side="right", padx=40)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.download_path.set(path)

    def start_download(self):
        url = self.video_url.get().strip()
        print("DEBUG: URL ENTRY:", f"'{self.video_url.get()}'")
        path = self.download_path.get().strip()

        if not url:
            messagebox.showerror("Hata", "Lütfen bir video URL'si girin.")
            return
        if not path or not os.path.isdir(path):
            messagebox.showerror("Hata", "Lütfen geçerli bir klasör seçin.")
            return

        self.progress["value"] = 0
        self.downloading = True
        self.cancel_btn.config(state="normal")
        self.download_btn.config(state="disabled")

        thread = threading.Thread(target=self.download_video)
        thread.start()

    def download_video(self):
        format_choice = self.format_choice.get()
        url = self.video_url.get()
        path = self.download_path.get()

        # 👇 Burada base_path tanımlanıyor
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        ffmpeg_path = os.path.join(base_path, "ffmpeg_bin", "ffmpeg.exe")

        ydl_opts = {
            'format': 'bestaudio/best' if format_choice == "m4a" else 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
            'merge_output_format': format_choice,
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [self.hook],
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.ydl = ydl
                ydl.download([url])
        except Exception as e:
            messagebox.showerror("Hata", str(e))

        self.downloading = False
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

    def cancel_download(self):
        if self.downloading and self.ydl:
            self.ydl._download_retcode = 1  # indirilen iptal gibi davranması için hack
            messagebox.showinfo("İptal", "İndirme işlemi iptal edildi.")
            self.downloading = False
            self.cancel_btn.config(state="disabled")
            self.download_btn.config(state="normal")

    def hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = downloaded / total * 100
                self.progress["value"] = percent
                self.root.update_idletasks()

# Uygulamayı başlat
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()