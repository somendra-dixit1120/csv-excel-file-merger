import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import time

root = tk.Tk()
root.title("CSV Merger")
root.geometry("900x650")
root.resizable(True, True)

file_paths = []
column_vars = {}

# checkbox states
remove_dup_var = tk.IntVar(value=1)      # duplicate rows hatao
specific_col_var = tk.IntVar(value=0)    # specific column select karo
all_col_var = tk.IntVar(value=1)         # sab columns lo (default)


# ---------------- Helper Functions ----------------
def read_df(path):
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    else:
        return pd.read_excel(path)


def read_columns(path):
    if path.lower().endswith(".csv"):
        return list(pd.read_csv(path, nrows=0).columns)
    else:
        return list(pd.read_excel(path, nrows=0).columns)


def refresh_column_checkboxes():
    for widget in column_frame.winfo_children():
        widget.destroy()
    column_vars.clear()
    if not file_paths:
        return
    col_sets = [set(read_columns(p)) for p in file_paths]
    common = set.intersection(*col_sets)
    first_cols = read_columns(file_paths[0])
    common_columns = [c for c in first_cols if c in common]
    for col in common_columns:
        var = tk.IntVar(value=1)
        tk.Checkbutton(column_frame, text=col, variable=var).pack(side=tk.LEFT, padx=5)
        column_vars[col] = var


def toggle_columns_visibility():
    if specific_col_var.get() == 1:
        all_col_var.set(0)
        column_frame.pack(fill="x", padx=10, pady=(5, 0))
    else:
        column_frame.pack_forget()


def toggle_all_columns():
    if all_col_var.get() == 1:
        specific_col_var.set(0)
        column_frame.pack_forget()


# ---------------- Button Actions ----------------
def add_files():
    paths = filedialog.askopenfilenames(
        title="CSV ya Excel files select karo",
        filetypes=[("CSV/Excel files", "*.csv *.xlsx *.xls")]
    )
    for p in paths:
        if p not in file_paths:
            df = read_df(p)
            file_paths.append(p)
            tree.insert("", tk.END, iid=p, values=(
                os.path.basename(p), len(df.columns), len(df)
            ))
    refresh_column_checkboxes()
    result_label.config(text="")


def remove_selected():
    selected = tree.selection()
    for item in selected:
        tree.delete(item)
        if item in file_paths:
            file_paths.remove(item)
    refresh_column_checkboxes()


def erase_all():
    for item in tree.get_children():
        tree.delete(item)
    file_paths.clear()
    refresh_column_checkboxes()
    result_label.config(text="")


def merge_and_save():
    if not file_paths:
        messagebox.showwarning("Koi file nahi", "Pehle kam se kam 1 file add karo.")
        return

    start_time = time.time()

    if specific_col_var.get() == 1:
        chosen_cols = [c for c, v in column_vars.items() if v.get() == 1]
        if not chosen_cols:
            messagebox.showwarning("Column chuno", "Kam se kam ek column select karo.")
            return
    else:
        chosen_cols = None

    dataframes = []
    for path in file_paths:
        df = read_df(path)
        if chosen_cols:
            df = df[chosen_cols]
        dataframes.append(df)

    merged = pd.concat(dataframes, ignore_index=True)

    if remove_dup_var.get() == 1:
        merged = merged.drop_duplicates()

    save_path = filedialog.asksaveasfilename(
        title="Master file kahan save karni hai?",
        defaultextension=".xlsx",
        filetypes=[("Excel file", "*.xlsx"), ("CSV file", "*.csv")]
    )
    if not save_path:
        return

    if save_path.lower().endswith(".csv"):
        merged.to_csv(save_path, index=False)
    else:
        merged.to_excel(save_path, index=False)

    elapsed = round(time.time() - start_time, 2)
    size_kb = round(os.path.getsize(save_path) / 1024, 1)

    result_label.config(
        text=f"✅ Merged: {len(merged)} rows  |  File size: {size_kb} KB  |  Merging time: {elapsed} sec"
    )
    messagebox.showinfo("Ho gaya!", f"Master file save ho gayi:\n{save_path}")


# ---------------- UI Layout ----------------

# Title
tk.Label(root, text="CSV merger", font=("Segoe UI", 16, "bold")).pack(pady=(10, 0))
tk.Label(root, text="CSV Merger:  Made by Somendra Dixit",
         font=("Segoe UI", 9, "italic"), fg="#555").pack()

# Top buttons
top_frame = tk.Frame(root)
top_frame.pack(pady=10)
tk.Button(top_frame, text="Add +", width=12, bg="#2e7d32", fg="white",
          command=add_files).grid(row=0, column=0, padx=5)
tk.Button(top_frame, text="Remove", width=12, command=remove_selected).grid(row=0, column=1, padx=5)
tk.Button(top_frame, text="Erase all", width=12, command=erase_all).grid(row=0, column=2, padx=5)

# File table (File name / Total column / Total row)
table_frame = tk.Frame(root)
table_frame.pack(pady=10, fill="x", padx=20)

columns = ("file_name", "total_column", "total_row")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
tree.heading("file_name", text="File name")
tree.heading("total_column", text="Total column")
tree.heading("total_row", text="Total row")
tree.column("file_name", width=450)
tree.column("total_column", width=100, anchor="center")
tree.column("total_row", width=100, anchor="center")
tree.pack(fill="x")

# Column picker (specific columns) — dikhta hai jab "select specific column" check ho
column_frame = tk.Frame(root)

# Clearing option section
tk.Label(root, text="clearing option", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 0))

options_frame = tk.Frame(root)
options_frame.pack(fill="x", padx=20, pady=5)

tk.Checkbutton(options_frame, text="remove duplicate rows", variable=remove_dup_var).pack(anchor="w")
tk.Checkbutton(options_frame, text="select specific column", variable=specific_col_var,
               command=toggle_columns_visibility).pack(anchor="w")
tk.Checkbutton(options_frame, text="merge all columns", variable=all_col_var,
               command=toggle_all_columns).pack(anchor="w")

# Merge and save button + result
bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=15)
tk.Button(bottom_frame, text="Merge and save", width=20, height=2, bg="#1565c0", fg="white",
          command=merge_and_save).pack()

result_label = tk.Label(root, text="", font=("Segoe UI", 9), fg="#333")
result_label.pack(pady=5)

root.mainloop()