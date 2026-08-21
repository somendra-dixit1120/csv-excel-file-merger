import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

root = tk.Tk()
root.title("CSV / Excel Merger Tool")
root.geometry("700x600")

file_paths = []          # selected files
column_vars = {}         # column_name -> tk.IntVar (checkbox state)
column_mode = tk.StringVar(value="all")   # "all" ya "specific"


def read_columns(path):
    """Ek file ke columns nikalta hai (bina poora data load kiye)."""
    if path.lower().endswith(".csv"):
        return list(pd.read_csv(path, nrows=0).columns)
    else:
        return list(pd.read_excel(path, nrows=0).columns)


def refresh_columns():
    """Jab bhi files add/remove hon, common columns dobara nikalo aur checkboxes banao."""
    for widget in column_frame.winfo_children():
        widget.destroy()
    column_vars.clear()

    if not file_paths:
        return

    # sabhi files ke columns nikalo, aur jo COMMON hain wahi lo
    col_sets = [set(read_columns(p)) for p in file_paths]
    common = set.intersection(*col_sets)
    first_file_cols = read_columns(file_paths[0])
    common_columns = [c for c in first_file_cols if c in common]

    if not common_columns:
        tk.Label(column_frame, text="Files me koi common column nahi mila!",
                 fg="red").pack()
        return

    for col in common_columns:
        var = tk.IntVar(value=1)   # default: sab checked
        cb = tk.Checkbutton(column_frame, text=col, variable=var)
        cb.pack(anchor="w")
        column_vars[col] = var

    toggle_column_visibility()


def toggle_column_visibility():
    """'All' mode me checkboxes hide, 'Specific' mode me show."""
    if column_mode.get() == "specific":
        column_frame.pack(pady=5, fill="x", padx=30)
    else:
        column_frame.pack_forget()


def add_files():
    paths = filedialog.askopenfilenames(
        title="CSV ya Excel files select karo",
        filetypes=[("CSV/Excel files", "*.csv *.xlsx *.xls")]
    )
    for p in paths:
        if p not in file_paths:
            file_paths.append(p)
            file_listbox.insert(tk.END, p)
    status_label.config(text=f"{len(file_paths)} file(s) select ki gayi hain.")
    refresh_columns()


# --- Buttons ---
add_btn = tk.Button(root, text="+ Add Files", command=add_files,
                     bg="#2e7d32", fg="white")
add_btn.pack(pady=10)

# --- Listbox ---
file_listbox = tk.Listbox(root, width=90, height=8, selectmode=tk.EXTENDED)
file_listbox.pack(pady=5)

status_label = tk.Label(root, text="Koi file select nahi hui.")
status_label.pack()

# --- Column mode selection ---
mode_frame = tk.LabelFrame(root, text="Kaunse columns collect karne hain?", padx=10, pady=10)
mode_frame.pack(pady=10, fill="x", padx=20)

tk.Radiobutton(mode_frame, text="Sab columns (poori file)", variable=column_mode,
               value="all", command=toggle_column_visibility).pack(anchor="w")
tk.Radiobutton(mode_frame, text="Sirf specific columns (neeche se chuno)", variable=column_mode,
               value="specific", command=toggle_column_visibility).pack(anchor="w")

column_frame = tk.Frame(root)   # ye specific mode me checkboxes dikhayega

root.mainloop()