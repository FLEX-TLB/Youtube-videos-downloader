from tkinter import Tk, Label, Entry, Button, StringVar, Listbox, Scrollbar, END
from tkinter import ttk
from tkinter import filedialog
import sys
import os
yt_dlp_path = os.path.abspath('yt-dlp')
sys.path.append(yt_dlp_path)
import yt_dlp
from threading import Thread


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")

        # Load the icon file
        icon_path = "youtube.ico"

        # Set the icon
        root.after(100, lambda: root.iconbitmap(icon_path))


        # Disable resizing
        self.root.resizable(False, False)

        # URL entry
        self.url_label = Label(root, text="Enter YouTube URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)
        self.url_entry.bind("<KeyRelease>", self.on_url_entry_change)

        # Save location entry
        self.save_label = Label(root, text="Save Location:")
        self.save_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.save_entry = Entry(root, width=40)
        self.save_entry.grid(row=1, column=1, padx=10, pady=10)
        self.browse_button = Button(root, text="Browse", command=self.browse_save_location)
        self.browse_button.grid(row=1, column=2, padx=5, pady=10)

        # Format selection dropdown
        self.format_label = Label(root, text="Select quality:")
        self.format_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.format_combobox = ttk.Combobox(root, width=45, state="readonly")
        self.format_combobox.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Download button
        self.download_button = Button(root, text="Start Download", command=self.start_download)
        self.download_button.grid(row=3, column=1, padx=(0, 50), pady=10)  

        # Download status label
        self.status_label = Label(root, text="", anchor="center")
        self.status_label.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Progress variables
        self.progress = StringVar()
        self.progress.set(0)  
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate", variable=self.progress)
        self.progress_bar.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="we")  

        self.total_bytes = 0
        self.bytes_downloaded = 0  

    def browse_save_location(self):
        save_path = filedialog.askdirectory()
        self.save_entry.delete(0, END)
        self.save_entry.insert(0, save_path)

    def on_url_entry_change(self, event):
        self.populate_format_list()

    def populate_format_list(self):
        url = self.url_entry.get()
        if not url:
            return
        self.format_combobox['values'] = ["Getting formats..."]
        Thread(target=self.fetch_formats, args=(url,)).start()

    def fetch_formats(self, url):
        formats = self.get_available_formats(url)
        format_dict = {}
        format_list = []
        for format in formats:
            if format.get('acodec') == 'mp4a.40.2' and format.get('vcodec') != 'none':
                format_description = f"{format['resolution']}"
                format_id = format['format_id']
                format_list.append(format_description)
                format_dict[format_description] = format_id
        self.format_combobox['values'] = format_list
        self.format_dict = format_dict

    def start_download(self):
        url = self.url_entry.get()
        save_path = self.save_entry.get()
        selected_format_description = self.format_combobox.get()
        if not url:
            self.status_label.config(text="Error: Please enter a YouTube URL.")
            return
        if not save_path:
            self.status_label.config(text="Error: Please select a save location.")
            return
        if selected_format_description not in self.format_dict:
            self.status_label.config(text="Error: Please select a valid format.")
            return
        selected_format = self.format_dict[selected_format_description]
        self.download_button.config(state="disabled")
        self.status_label.config(text=" Starting download...")
        self.progress.set(0)  # Reset progress to 0
        Thread(target=self.download_video, args=(url, save_path, selected_format)).start()

    def download_video(self, url, save_path, selected_format):
        ydl_opts = {
            'outtmpl': save_path + '/%(title)s.%(ext)s',
            'quiet': True,
            'format': selected_format,
            'progress_hooks': [self.show_progress]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
                self.status_label.config(text="Download completed!")
            except Exception as e:
                self.status_label.config(text="An error occurred: " + str(e))
            finally:
                self.download_button.config(state="normal")

    def show_progress(self, d):
        if d['status'] == 'downloading':
            downloaded_bytes = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes', 1)
            percentage = downloaded_bytes / total_bytes * 100
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            downloaded_mb = downloaded_bytes / (1024 * 1024)
            total_mb = total_bytes / (1024 * 1024)
            self.progress.set(percentage)
            self.status_label.config(text=f"Downloading... {percentage:.2f}% ({downloaded_mb:.2f}MB / {total_mb:.2f}MB) at {speed}, ETA: {eta}")
        elif d['status'] == 'finished':
            self.progress.set(100)
            self.status_label.config(text="Download completed!")

    def get_available_formats(self, url):
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            return formats

root = Tk()
app = YouTubeDownloader(root)
root.mainloop()
