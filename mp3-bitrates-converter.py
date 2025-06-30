import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
from pathlib import Path

CONFIG_FILE = "config.txt"

class MP3CompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Compressor")

        self.file_paths = []
        self.ffmpeg_path = self.load_ffmpeg_path()
        self.output_path = ""

        # GUI widgets
        self.select_button = tk.Button(root, text="Seleziona MP3", command=self.select_files)
        self.select_button.pack(pady=10)

        self.bitrate_label = tk.Label(root, text="Bitrate (kbps, minimo 32):")
        self.bitrate_label.pack()
        self.bitrate_var = tk.StringVar(value="128")
        self.bitrate_entry = tk.Entry(root, textvariable=self.bitrate_var)
        self.bitrate_entry.pack(pady=5)

        self.output_button = tk.Button(root, text="Seleziona cartella di output", command=self.select_output_folder)
        self.output_button.pack(pady=10)

        self.convert_button = tk.Button(root, text="Comprimi", command=self.compress_files)
        self.convert_button.pack(pady=20)

        self.change_ffmpeg_button = tk.Button(root, text="Cambia percorso ffmpeg.exe", command=self.select_ffmpeg_path)
        self.change_ffmpeg_button.pack(pady=5)

    def load_ffmpeg_path(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                path = f.read().strip()
                if os.path.isfile(path):
                    return path
        return self.select_ffmpeg_path()

    def select_ffmpeg_path(self):
        path = filedialog.askopenfilename(title="Seleziona ffmpeg.exe", filetypes=[("ffmpeg.exe", "ffmpeg.exe")])
        if not path:
            messagebox.showerror("Errore", "È necessario selezionare ffmpeg.exe per continuare.")
            self.root.quit()
        with open(CONFIG_FILE, "w") as f:
            f.write(path)
        return path

    def select_files(self):
        self.file_paths = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
        if self.file_paths:
            messagebox.showinfo("File selezionati", f"{len(self.file_paths)} file selezionati.")

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path = folder
            messagebox.showinfo("Cartella selezionata", f"Output: {self.output_path}")

    def compress_files(self):
        if not self.file_paths:
            messagebox.showerror("Errore", "Nessun file selezionato.")
            return
        if not self.output_path:
            messagebox.showerror("Errore", "Nessuna cartella di output selezionata.")
            return

        try:
            bitrate = int(self.bitrate_var.get())
            if bitrate < 32:
                raise ValueError
        except ValueError:
            messagebox.showerror("Errore", "Inserisci un bitrate valido (>=32).")
            return

        for file in self.file_paths:
            filename = os.path.basename(file)
            output_file = os.path.join(self.output_path, filename)

            command = [
                self.ffmpeg_path,
                "-y",
                "-i", file,
                "-b:a", f"{bitrate}k",
                output_file
            ]

            try:
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                messagebox.showerror("Errore", f"Errore durante la conversione di {filename}")
                continue

        messagebox.showinfo("Completato", "Compressione completata con successo!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MP3CompressorApp(root)
    root.mainloop()
