import tkinter as tk
from tkinter import filedialog, messagebox
import os

def select_mp3_files():
    files = filedialog.askopenfilenames(
        title="Seleziona file MP3 da unire",
        filetypes=[("File MP3", "*.mp3")]
    )
    if files:
        listbox.delete(0, tk.END)
        for f in files:
            listbox.insert(tk.END, f)
        status_label.config(text=f"{len(files)} file selezionati.")

def choose_output_file():
    file = filedialog.asksaveasfilename(
        defaultextension=".mp3",
        filetypes=[("File MP3", "*.mp3")],
        title="Nome del file MP3 risultante"
    )
    if file:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, file)

def concatenate_mp3_files():
    files = listbox.get(0, tk.END)
    output_path = output_entry.get()

    if not files:
        messagebox.showwarning("Attenzione", "Seleziona almeno un file MP3.")
        return
    if not output_path:
        messagebox.showwarning("Attenzione", "Specifica un percorso di output.")
        return

    try:
        with open(output_path, "wb") as outfile:
            for mp3_file in files:
                with open(mp3_file, "rb") as infile:
                    outfile.write(infile.read())
        messagebox.showinfo("Successo", f"File creato con successo:\n{output_path}")
        status_label.config(text="Unione completata.")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante l'unione: {e}")
        status_label.config(text="Errore durante l'unione.")

# Interfaccia grafica
root = tk.Tk()
root.title("Unisci MP3 (senza ffmpeg)")
root.geometry("600x400")

tk.Button(root, text="Seleziona MP3", command=select_mp3_files).pack(pady=5)

listbox = tk.Listbox(root, width=80, height=10)
listbox.pack(pady=5)

tk.Label(root, text="File di output:").pack(pady=5)
output_entry = tk.Entry(root, width=60)
output_entry.pack(pady=5)
tk.Button(root, text="Scegli percorso", command=choose_output_file).pack(pady=5)

tk.Button(root, text="Unisci MP3", command=concatenate_mp3_files, bg="#4CAF50", fg="white").pack(pady=10)

status_label = tk.Label(root, text="")
status_label.pack(pady=5)

root.mainloop()
