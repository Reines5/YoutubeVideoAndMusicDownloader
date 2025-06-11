import os
import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys

class YouTubeDownloader:

    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video & Audio Downloader v1.1")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        self.video_url = tk.StringVar()
        self.download_path = tk.StringVar()
        self.format_choice = tk.StringVar(value="mp4")
        self.downloading = False
        self.cancelled = False
        self.ydl = None

        self.create_widgets()

    def create_widgets(self):
        self.root.columnconfigure(0, weight=1, minsize=250)
        self.root.columnconfigure(1, weight=1, minsize=250)

        # 1st Row: Video URL Entry (with placeholder)
        self.video_url = tk.StringVar()
        self.url_entry = tk.Entry(self.root, textvariable=self.video_url, width=30, fg='grey')
        self.url_entry.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.url_entry.insert(0, "Please enter video URL (Please press Enter!)")
        self.url_entry.bind("<FocusIn>", self.clear_url_placeholder)
        self.url_entry.bind("<FocusOut>", self.add_url_placeholder)
        self.url_entry.bind("<FocusOut>", self.on_url_entry_change)
        self.url_entry.bind("<Return>", self.on_url_entry_change)

        # 2nd Row: Video Title Entry (with placeholder)
        self.video_title = tk.StringVar()
        self.title_entry = tk.Entry(self.root, textvariable=self.video_title, width=30, fg='grey')
        self.title_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.title_entry.insert(0, "Video Title (Editable)")
        self.title_entry.bind("<FocusIn>", self.clear_title_placeholder)
        self.title_entry.bind("<FocusOut>", self.add_title_placeholder)

        # 3rd Row: Download Folder
        tk.Button(self.root, text="Choose Download Folder", command=self.select_folder).grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        tk.Label(self.root, textvariable=self.download_path).grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # 4th Row: Video Format
        tk.Label(self.root, text="Video Format").grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        format_menu = ttk.Combobox(self.root, textvariable=self.format_choice, values=["mp4", "m4a", "mp3"], state="readonly")
        format_menu.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        format_menu.bind("<<ComboboxSelected>>", lambda e: self.on_format_change())

        # 5th Row: Video Quality
        tk.Label(self.root, text="Video Quality", name="quality_label").grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.quality_choice = tk.StringVar()
        self.quality_menu = ttk.Combobox(self.root, textvariable=self.quality_choice, state="readonly")
        self.quality_menu.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        # 6th Row: Audio Format
        self.audio_format_label = tk.Label(self.root, text="Audio Format (for MP4)")
        self.audio_format_label.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        self.audio_format_choice = tk.StringVar(value="m4a")
        self.audio_format_menu = ttk.Combobox(
            self.root,
            textvariable=self.audio_format_choice,
            values=["m4a", "mp3"],
            state="readonly"
        )
        self.audio_format_menu.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

        # 7th Row: Progress Bar and Info Label
        self.progress = ttk.Progressbar(self.root, length=400)
        self.progress.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.progress_label = tk.Label(self.root, text="", fg="green")
        self.progress_label.grid(row=7, column=0, columnspan=2, padx=10, pady=(0,10), sticky="ew")

        # 8th Row: Download and Cancel Download buttons
        self.download_btn = tk.Button(self.root, text="Download", command=self.start_download)
        self.download_btn.grid(row=8, column=0, padx=10, pady=10, sticky="ew")

        self.cancel_btn = tk.Button(self.root, text="Cancel Download", command=self.cancel_download, state="disabled")
        self.cancel_btn.grid(row=8, column=1, padx=10, pady=10, sticky="ew")

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.download_path.set(path)

    def start_download(self):
        url = self.video_url.get().strip()
        print("DEBUG: URL ENTRY:", f"'{self.video_url.get()}'")
        path = self.download_path.get().strip()

        if not url:
            messagebox.showerror("Input Error", "Please enter a YouTube video URL.")
            return
        if not path or not os.path.isdir(path):
            messagebox.showerror("Input Error", "Please select a valid download folder.")
            return

        self.progress["value"] = 0
        self.downloading = True
        self.cancel_btn.config(state="normal")
        self.download_btn.config(state="disabled")

        # Start download in a new thread based on selected format
        if self.format_choice.get() == "mp4":
            thread = threading.Thread(target=self.download_video)
        else:
            thread = threading.Thread(target=self.download_audio_highest)
        thread.start()

    def on_format_change(self):
        fmt = self.format_choice.get()
        quality_label = self.root.nametowidget(".quality_label")

        # Hide all relevant widgets first
        quality_label.grid_forget()
        self.quality_menu.grid_forget()
        self.audio_format_label.grid_forget()
        self.audio_format_menu.grid_forget()

        if fmt == "mp4":
            # Show quality and audio format widgets in correct order
            quality_label.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
            self.quality_menu.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
            self.audio_format_label.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
            self.audio_format_menu.grid(row=5, column=1, padx=10, pady=10, sticky="ew")
            self.root.geometry("500x450")
            self.fetch_qualities()
        else:
            self.root.geometry("500x300")

    def fetch_qualities(self):
        url = self.video_url.get().strip()
        # Check placeholder and format
        if not url or url == "Please enter video URL (Please press Enter!)" or self.format_choice.get() != "mp4":
            self.quality_menu['values'] = []
            self.quality_choice.set("")
            self.video_title.set("")
            return
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                # Fetch video title and set it to the title entry
                title = info.get('title', '')
                if title:
                    self.video_title.set(title)
                formats = info.get('formats', [])
                best_by_height = {}
                for f in formats:
                    ext = f.get('ext', '')
                    if ext != "mp4":
                        continue
                    height = f.get('height', '')
                    if not height:
                        continue
                    tbr = f.get('tbr', 0) or 0  # total bitrate
                    # For each resolution, keep only the highest bitrate option
                    if height not in best_by_height or tbr > best_by_height[height].get('tbr', 0):
                        best_by_height[height] = f
                # Sort resolutions from lowest to highest
                sorted_heights = sorted(best_by_height.keys(), key=lambda x: int(x))
                qualities = []
                for height in sorted_heights:
                    f = best_by_height[height]
                    format_id = f.get('format_id', '')
                    ext = f.get('ext', '')
                    fps = f.get('fps', '')
                    acodec = f.get('acodec', 'none')
                    vcodec = f.get('vcodec', 'none')
                    filesize = f.get('filesize', 0) or f.get('filesize_approx', 0)
                    size_mb = f"{round(filesize/1024/1024,1)}MB" if filesize else ""
                    label = f"{format_id} - {height}p {ext} "
                    if vcodec != 'none' and acodec != 'none':
                        label += "(video+audio)"
                    elif vcodec != 'none':
                        label += "(video only)"
                    elif acodec != 'none':
                        label += "(audio only)"
                    if fps:
                        label += f" {fps}fps"
                    if size_mb:
                        label += f" {size_mb}"
                    qualities.append(label)
                if qualities:
                    self.quality_menu['values'] = qualities
                    self.quality_choice.set(qualities[0])
        except Exception as e:
            self.quality_menu['values'] = []
            self.quality_choice.set("")
            self.video_title.set("")

    def download_video(self):
        format_choice = self.format_choice.get()
        url = self.video_url.get()
        path = self.download_path.get()
        selected_quality = self.quality_choice.get().split(" - ")[0]
        audio_format = self.audio_format_choice.get()

        if format_choice == "mp4" and audio_format == "mp3":
            messagebox.showerror(
                "Format Error",
                "MP4 video cannot be combined with MP3 audio. Please select M4A as the audio format."
            )
            self.downloading = False
            self.download_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")
            return

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        ffmpeg_path = os.path.join(base_path, "ffmpeg_bin", "ffmpeg.exe")

        # Check if selected quality contains both video and audio
        selected_format_info = None
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                for f in info.get('formats', []):
                    if f.get('format_id') == selected_quality:
                        selected_format_info = f
                        break
        except Exception as e:
            messagebox.showerror("Error", f"Could not retrieve quality information: {e}")
            self.downloading = False
            self.download_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")
            return

        # If selected quality has both video and audio, download only that format
        if selected_format_info and selected_format_info.get('acodec', 'none') != 'none':
            ydl_format = selected_quality
            merge_output = False
        else:
            # If only video, merge with best available audio
            ydl_format = f"{selected_quality}+bestaudio[ext=m4a]/bestaudio"
            merge_output = True

        title = self.video_title.get().strip() or '%(title)s'
        ydl_opts = {
            'outtmpl': os.path.join(path, f'{title}.%(ext)s'),
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [self.hook],
            'quiet': True,
            'format': ydl_format,
        }
        if merge_output:
            ydl_opts['merge_output_format'] = 'mp4'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.ydl = ydl
                ydl.download([url])
            # Download successful:
            self.progress["value"] = 100
            self.progress_label.config(text="Download completed!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.progress_label.config(text="")
        self.downloading = False
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
 
    def cancel_download(self):
        if self.downloading:
            self.cancelled = True
            messagebox.showinfo("Download Cancelled", "The download has been cancelled by the user.")
            self.downloading = False
            self.cancel_btn.config(state="disabled")
            self.download_btn.config(state="normal")

    def hook(self, d):
        if self.cancelled:
            raise Exception("Download cancelled by the user.")
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = downloaded / total * 100
                self.progress["value"] = percent
                self.root.update_idletasks()

    def download_audio_highest(self):
        url = self.video_url.get()
        path = self.download_path.get()
        audio_format = self.format_choice.get()  # m4a or mp3

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        ffmpeg_path = os.path.join(base_path, "ffmpeg_bin", "ffmpeg.exe")

        # Use the user-provided or auto-fetched video title as filename
        title = self.video_title.get().strip() or '%(title)s'

        if audio_format == "mp3":
            ydl_opts = {
                'outtmpl': os.path.join(path, f'{title}.%(ext)s'),
                'ffmpeg_location': ffmpeg_path,
                'progress_hooks': [self.hook],
                'quiet': True,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:  # m4a
            ydl_opts = {
                'outtmpl': os.path.join(path, f'{title}.%(ext)s'),
                'ffmpeg_location': ffmpeg_path,
                'progress_hooks': [self.hook],
                'quiet': True,
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.ydl = ydl
                ydl.download([url])
            # Download successful:
            self.progress["value"] = 100
            self.progress_label.config(text="Download completed!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.progress_label.config(text="")
        self.downloading = False
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

    def clear_url_placeholder(self, event):
        if self.url_entry.get() == "Please enter video URL (Please press Enter!)":
            self.url_entry.delete(0, tk.END)
            self.url_entry.config(fg='black')

    def add_url_placeholder(self, event):
        if not self.url_entry.get():
            self.url_entry.insert(0, "Please enter video URL (Please press Enter!)")
            self.url_entry.config(fg='grey')

    def clear_title_placeholder(self, event):
        if self.title_entry.get() == "Video Title":
            self.title_entry.delete(0, tk.END)
            self.title_entry.config(fg='black')

    def add_title_placeholder(self, event):
        if not self.title_entry.get():
            self.title_entry.insert(0, "Video Title")
            self.title_entry.config(fg='grey')

    def on_url_entry_change(self, event):
        # Reset progress bar and label
        self.progress["value"] = 0
        self.progress_label.config(text="")
        url = self.video_url.get().strip()
        # Check placeholder
        if not url or url == "Please enter video URL":
            self.quality_menu['values'] = []
            self.quality_choice.set("")
            self.video_title.set("")
            return
        # Update quality and title only on focus out or Enter key
        if event.type == "9" or (event.type == "2" and event.keysym == "Return"):
            if self.format_choice.get() == "mp4":
                self.fetch_qualities()

# Application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
