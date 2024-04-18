import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from threading import Thread

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")

        # Set window icon
        self.root.iconbitmap("youtube.ico")

        # Disable resizing
        self.root.resizable(False, False)

        # URL entry
        self.url_label = tk.Label(root, text="Enter YouTube URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        # Save location entry
        self.save_label = tk.Label(root, text="Save Location:")
        self.save_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.save_entry = tk.Entry(root, width=40)
        self.save_entry.grid(row=1, column=1, padx=10, pady=10)
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_save_location)
        self.browse_button.grid(row=1, column=2, padx=5, pady=10)

        # Download button
        self.download_button = tk.Button(root, text="Start Download", command=self.start_download)
        self.download_button.grid(row=2, column=1, padx=(0, 50), pady=10)  # Adjust padx here

        # Download status label
        self.status_label = tk.Label(root, text="", anchor="center")
        self.status_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Progress variables
        self.progress = tk.DoubleVar()
        self.progress.set(0)  # Set initial value to 0
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate", variable=self.progress)
        self.progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="we")  # Place progress bar below the status label

        self.total_bytes = 0
        self.bytes_downloaded = 0  # Added this variable

    def browse_save_location(self):
        save_path = filedialog.askdirectory()
        self.save_entry.delete(0, tk.END)
        self.save_entry.insert(0, save_path)

    def start_download(self):
        url = self.url_entry.get()
        save_path = self.save_entry.get()

        if not url:
            self.status_label.config(text="Error: Please enter a YouTube URL.")
            return

        if not save_path:
            self.status_label.config(text="Error: Please select a save location.")
            return

        try:
            yt = YouTube(url, on_progress_callback=self.show_progress)
        except RegexMatchError:
            self.status_label.config(text="Error: Invalid YouTube URL.")
            return

        self.download_button.config(state="disabled")
        self.status_label.config(text="Downloading...")
        self.progress.set(0)  # Reset progress to 0
        self.download_thread = Thread(target=self.download_video, args=(yt, save_path))
        self.download_thread.start()

    def download_video(self, yt, save_path):
        try:
            stream = yt.streams.get_highest_resolution()
            self.total_bytes = stream.filesize

            # Get the default filename provided by pytube
            downloaded_file = stream.download(output_path=save_path)

            # Update the status label
            self.status_label.config(text="Download completed!")
        except Exception as e:
            if isinstance(e, RegexMatchError):
                self.status_label.config(text="Error: Invalid YouTube URL.")
            else:
                self.status_label.config(text="An error occurred: " + str(e))
        self.download_button.config(state="normal")

    def show_progress(self, stream, chunk, bytes_remaining):
        self.bytes_downloaded = self.total_bytes - bytes_remaining  # Updated bytes_downloaded
        percentage = (self.bytes_downloaded / self.total_bytes) * 100
        self.progress.set(percentage)
        self.status_label.config(text=f"Downloading... {percentage:.2f}% ({self.bytes_downloaded / (1024*1024):.2f} MB / {self.total_bytes / (1024*1024):.2f} MB)")

# Create main window
root = tk.Tk()
app = YouTubeDownloader(root)
root.mainloop()
