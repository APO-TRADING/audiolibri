import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import asyncio
import edge_tts
import pdfplumber
from bs4 import BeautifulSoup
from ebooklib import epub

class AudiobookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audiobook Creator")
        self.root.geometry("600x600")

        self.file_label = ttk.Label(root, text="Seleziona i file:")
        self.file_label.pack(pady=5)
        self.file_listbox = tk.Listbox(root, width=70, height=5, selectmode=tk.MULTIPLE)
        self.file_listbox.pack(pady=5)
        self.browse_button = ttk.Button(root, text="Sfoglia", command=self.browse_files)
        self.browse_button.pack(pady=5)

        self.output_label = ttk.Label(root, text="Seleziona la cartella di output:")
        self.output_label.pack(pady=5)
        self.output_entry = tk.Entry(root, width=50)
        self.output_entry.pack(pady=5)
        self.output_browse_button = ttk.Button(root, text="Sfoglia", command=self.browse_output_folder)
        self.output_browse_button.pack(pady=5)

        self.locale_label = ttk.Label(root, text="Seleziona la lingua/paese:")
        self.locale_label.pack(pady=5)
        self.locale_combo = ttk.Combobox(root, state="readonly", width=30)
        self.locale_combo.pack(pady=5)
        self.locale_combo.bind("<<ComboboxSelected>>", self.update_voice_combo_filtered)

        self.voice_label = ttk.Label(root, text="Seleziona la voce:")
        self.voice_label.pack(pady=5)
        self.voice_combo = ttk.Combobox(root, state="readonly", width=30)
        self.voice_combo.pack(pady=5)

        self.speed_label = ttk.Label(root, text="Seleziona la velocità di lettura:")
        self.speed_label.pack(pady=5)
        self.speed_combo = ttk.Combobox(root, state="readonly", width=30)
        self.speed_combo['values'] = ['0.5', '0.75', '1.0', '1.25', '1.5', '1.75', '2.0']
        self.speed_combo.current(2)
        self.speed_combo.pack(pady=5)

        self.delete_parts_var = tk.BooleanVar()
        self.delete_parts_checkbox = ttk.Checkbutton(
            root, text="Elimina i file partX.mp3 dopo l'unione",
            variable=self.delete_parts_var
        )
        self.delete_parts_checkbox.pack(pady=5)

        self.voices = []
        threading.Thread(target=self.fetch_voices, daemon=True).start()

        self.create_button = ttk.Button(root, text="Crea Audiobooks", command=self.create_audiobooks)
        self.create_button.pack(pady=10)

        self.status_label = ttk.Label(root, text="")
        self.status_label.pack(pady=5)

    def browse_files(self):
        file_paths = filedialog.askopenfilenames(title="Seleziona uno o più file", filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf"), ("EPUB files", "*.epub")])
        self.file_listbox.delete(0, tk.END)
        for file_path in file_paths:
            self.file_listbox.insert(tk.END, file_path)

    def browse_output_folder(self):
        output_dir = filedialog.askdirectory(title="Seleziona la cartella di destinazione")
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, output_dir)

    def extract_text_from_pdf(self, pdf_path):
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text

    def extract_text_from_epub(self, epub_path):
        book = epub.read_epub(epub_path)
        text = ""
        for item in book.items:
            if item.get_type() == 9:
                soup = BeautifulSoup(item.content, 'html.parser')
                text += soup.get_text() + "\n"
        return text

    def text_to_speech_edge_tts(self, text, output_path, voice, speed):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        communicate = edge_tts.Communicate(text, voice)
        communicate.rate = float(speed)
        loop.run_until_complete(communicate.save(output_path))

    def split_text_into_chunks(self, text, chunk_size=5000):
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end >= len(text):
                chunks.append(text[start:])
                break
            else:
                last_period = text.rfind('.', start, end)
                if last_period != -1:
                    end = last_period + 1
                chunks.append(text[start:end])
                start = end
        return chunks

    def create_audiobooks(self):
        file_paths = self.file_listbox.get(0, tk.END)
        output_dir = self.output_entry.get()
        voice = self.voice_combo.get()
        speed = self.speed_combo.get()
        delete_parts = self.delete_parts_var.get()

        if not file_paths or not output_dir or not voice:
            messagebox.showwarning("Attenzione", "Completa tutti i campi obbligatori.")
            return

        self.create_button.config(state=tk.DISABLED)

        def generate():
            try:
                os.makedirs(output_dir, exist_ok=True)
                for file_path in file_paths:
                    try:
                        if file_path.endswith(".pdf"):
                            text = self.extract_text_from_pdf(file_path)
                        elif file_path.endswith(".epub"):
                            text = self.extract_text_from_epub(file_path)
                        else:
                            with open(file_path, "r", encoding="utf-8") as f:
                                text = f.read()
                    except Exception as e:
                        messagebox.showerror("Errore", f"Errore nella lettura di {file_path}: {str(e)}")
                        continue

                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    chunks = self.split_text_into_chunks(text)
                    part_files = []
                    for i, chunk in enumerate(chunks):
                        part_path = os.path.join(output_dir, f"{base_name}_part{i}.mp3")
                        try:
                            self.text_to_speech_edge_tts(chunk, part_path, voice, speed)
                            part_files.append(part_path)
                            self.status_label.config(text=f"Creata parte {i+1}/{len(chunks)} per {base_name}")
                        except Exception as e:
                            messagebox.showerror("Errore", f"Errore nella parte {i+1} per {base_name}: {str(e)}")
                            break

                    # Concatenazione binaria MP3
                    if part_files:
                        try:
                            final_path = os.path.join(output_dir, f"{base_name}.mp3")
                            with open(final_path, "wb") as outfile:
                                for pf in part_files:
                                    with open(pf, "rb") as infile:
                                        outfile.write(infile.read())

                            if os.path.exists(final_path) and delete_parts:
                                for pf in part_files:
                                    try:
                                        os.remove(pf)
                                    except Exception as e:
                                        print(f"Errore nell'eliminazione {pf}: {str(e)}")

                            self.status_label.config(text=f"Creato: {final_path}")
                        except Exception as e:
                            messagebox.showerror("Errore", f"Errore nell'unione per {base_name}: {str(e)}")

                messagebox.showinfo("Successo", "Audiobooks creati con successo!")
            finally:
                self.create_button.config(state=tk.NORMAL)

        threading.Thread(target=generate, daemon=True).start()

    def fetch_voices(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            voices = loop.run_until_complete(edge_tts.list_voices())
            self.voices = voices
            self.root.after(0, self.update_voice_combo)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Errore", f"Impossibile caricare le voci: {str(e)}"))

    def update_voice_combo(self):
        self.voice_by_locale = {}
        for v in self.voices:
            locale = v['Locale']
            if locale not in self.voice_by_locale:
                self.voice_by_locale[locale] = []
            self.voice_by_locale[locale].append(v['ShortName'])

        locales = sorted(self.voice_by_locale.keys())
        self.locale_combo['values'] = locales
        if locales:
            self.locale_combo.current(0)
            self.update_voice_combo_filtered()

    def update_voice_combo_filtered(self, event=None):
        selected_locale = self.locale_combo.get()
        voices = self.voice_by_locale.get(selected_locale, [])
        self.voice_combo['values'] = voices
        if voices:
            self.voice_combo.current(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudiobookApp(root)
    root.mainloop()
