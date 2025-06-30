import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re

def split_text_into_parts(text, num_parts):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    # Calcolo del numero totale di parole
    total_words = sum(len(sentence.split()) for sentence in sentences)
    words_per_part = total_words // num_parts

    parts = []
    current_part = ""
    current_word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())
        if current_word_count + sentence_word_count <= words_per_part or len(parts) == num_parts - 1:
            current_part += sentence + " "
            current_word_count += sentence_word_count
        else:
            parts.append(current_part.strip())
            current_part = sentence + " "
            current_word_count = sentence_word_count

    parts.append(current_part.strip())
    return parts

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    entry_file.delete(0, tk.END)
    entry_file.insert(0, file_path)

def start_split():
    file_path = entry_file.get()
    try:
        num_parts = int(entry_parts.get())
        if num_parts < 1:
            raise ValueError
    except ValueError:
        messagebox.showerror("Errore", "Inserisci un numero valido di parti.")
        return

    if not os.path.isfile(file_path):
        messagebox.showerror("Errore", "File non trovato.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    parts = split_text_into_parts(text, num_parts)
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    output_dir = os.path.join(os.path.dirname(file_path), f"{base_name}_split")
    os.makedirs(output_dir, exist_ok=True)

    for i, part in enumerate(parts):
        output_path = os.path.join(output_dir, f"{base_name}_part{i+1}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(part)

    messagebox.showinfo("Completato", f"File diviso in {len(parts)} parti in:\n{output_dir}")

# GUI
root = tk.Tk()
root.title("Splitter eBook in Parti")

tk.Label(root, text="File TXT:").grid(row=0, column=0, sticky="e")
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1, padx=5)
tk.Button(root, text="Sfoglia", command=browse_file).grid(row=0, column=2, padx=5)

tk.Label(root, text="Numero di parti:").grid(row=1, column=0, sticky="e")
entry_parts = tk.Entry(root, width=10)
entry_parts.grid(row=1, column=1, sticky="w")

tk.Button(root, text="Dividi", command=start_split).grid(row=2, column=1, pady=10)

root.mainloop()
