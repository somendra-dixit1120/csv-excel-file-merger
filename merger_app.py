import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.title("CSV / Excel Merger Tool")
root.geometry("700x560")

file_paths = []   # yaha hum selected files ka path store karenge

def add_files():
    paths = filedialog.askopenfilenames(
        title="CSV ya Excel files select karo",
        filetypes=[("CSV/Excel files", "*.csv *.xlsx *.xls")]
    )
    for p in paths:
        if p not in file_paths:
            file_paths.append(p)
            file_listbox.insert(tk.END, p)   # file listbox me dikhado
    status_label.config(text=f"{len(file_paths)} file(s) select ki gayi hain.")

# --- Button ---
add_btn = tk.Button(root, text="+ Add Files", command=add_files,
                     bg="#2e7d32", fg="white")
add_btn.pack(pady=10)

# --- Listbox (file names dikhane ke liye) ---
file_listbox = tk.Listbox(root, width=90, height=15, selectmode=tk.EXTENDED)
file_listbox.pack(pady=10)

# --- Status label ---
status_label = tk.Label(root, text="Koi file select nahi hui.")
status_label.pack()

root.mainloop()