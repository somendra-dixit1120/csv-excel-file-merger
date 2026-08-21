import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import sys
import time


def resource_path(relative_path):
    """Get absolute path to a resource, works for dev and for PyInstaller .exe"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# ============================================================
#  BACKGROUND SETTINGS
# ============================================================
# 1) To change background COLOR: just edit the value below.
BG_COLOR = "#0b1531"   # dark navy shade matching the background image

# 2) To use a BACKGROUND IMAGE instead of a solid color:
#    - install pillow first:   python -m pip install pillow
#    - set USE_BG_IMAGE = True
#    - set BG_IMAGE_PATH to your image file
USE_BG_IMAGE = True
BG_IMAGE_PATH = "background.png"   # <-- your image file path

# Text color (light, so it's readable on the dark background)
FG_COLOR = "#e8eefc"
# ============================================================

root = tk.Tk()
root.title("CSV Merger")
root.geometry("950x700")
root.resizable(True, True)
root.configure(bg=BG_COLOR)

file_paths = []
column_vars = {}

remove_dup_var = tk.IntVar(value=1)
specific_col_var = tk.IntVar(value=0)
all_col_var = tk.IntVar(value=1)

# ---------------- Background Image (optional) ----------------
if USE_BG_IMAGE:
    from PIL import Image, ImageTk

    bg_image_raw = Image.open(resource_path(BG_IMAGE_PATH))
    bg_photo = None
    bg_label = tk.Label(root)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    bg_label.lower()

    def resize_bg_image(event=None):
        global bg_photo
        w = root.winfo_width()
        h = root.winfo_height()
        if w > 1 and h > 1:
            resized = bg_image_raw.resize((w, h))
            bg_photo = ImageTk.PhotoImage(resized)
            bg_label.configure(image=bg_photo)

    root.bind("<Configure>", resize_bg_image)


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
        tk.Checkbutton(column_frame, text=col, variable=var, bg=BG_COLOR, fg=FG_COLOR,
                       selectcolor="#1a2550").pack(side=tk.LEFT, padx=5)
        column_vars[col] = var


def toggle_columns_visibility():
    if specific_col_var.get() == 1:
        all_col_var.set(0)
        column_frame.grid(row=3, column=0, columnspan=3, sticky="w", padx=20, pady=(0, 5))
    else:
        column_frame.grid_forget()


def toggle_all_columns():
    if all_col_var.get() == 1:
        specific_col_var.set(0)
        column_frame.grid_forget()


# ---------------- Button Actions ----------------
def add_files():
    paths = filedialog.askopenfilenames(
        title="Select CSV or Excel files",
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
        messagebox.showwarning("No files", "Please add at least 1 file first.")
        return

    if specific_col_var.get() == 1:
        chosen_cols = [c for c, v in column_vars.items() if v.get() == 1]
        if not chosen_cols:
            messagebox.showwarning("Select column", "Please select at least one column.")
            return
    else:
        chosen_cols = None

    total_files = len(file_paths)
    progress_bar["maximum"] = total_files
    progress_bar["value"] = 0

    dataframes = []
    file_times = []

    for i, path in enumerate(file_paths):
        t0 = time.time()

        df = read_df(path)
        if chosen_cols:
            df = df[chosen_cols]
        dataframes.append(df)

        t1 = time.time()
        file_times.append(t1 - t0)

        # progress bar update
        progress_bar["value"] = i + 1

        # remaining time estimate (average time per file * files left)
        avg_time = sum(file_times) / len(file_times)
        files_left = total_files - (i + 1)
        remaining = round(avg_time * files_left, 1)
        countdown_label.config(text=f"Time remaining: {remaining} sec")

        root.update_idletasks()
        root.update()

    countdown_label.config(text="Merging... finalizing")
    root.update_idletasks()

    start_merge_time = time.time()
    merged = pd.concat(dataframes, ignore_index=True)

    if remove_dup_var.get() == 1:
        merged = merged.drop_duplicates()

    save_path = filedialog.asksaveasfilename(
        title="Where do you want to save the merged file?",
        defaultextension=".xlsx",
        filetypes=[("Excel file", "*.xlsx"), ("CSV file", "*.csv")]
    )
    if not save_path:
        countdown_label.config(text="Time remaining: -")
        return

    if save_path.lower().endswith(".csv"):
        merged.to_csv(save_path, index=False)
    else:
        merged.to_excel(save_path, index=False)

    total_elapsed = round(sum(file_times) + (time.time() - start_merge_time), 2)
    size_kb = round(os.path.getsize(save_path) / 1024, 1)

    size_label.config(text=f"File size: {size_kb} KB")
    time_label.config(text=f"Merging time: {total_elapsed} sec")
    countdown_label.config(text="Time remaining: 0 sec (done)")
    result_label.config(text=f"Merged rows: {len(merged)}")
    messagebox.showinfo("Done!", f"Merged file saved to:\n{save_path}")


# ---------------- UI Layout (grid based for precise positions) ----------------

outer = tk.Frame(root, bg=BG_COLOR, highlightbackground="#3a4a7a", highlightthickness=2)
outer.pack(fill="both", expand=True, padx=8, pady=8)

outer.grid_columnconfigure(0, weight=0)   # left content
outer.grid_columnconfigure(1, weight=1)   # spacer (pushes things apart)
outer.grid_columnconfigure(2, weight=0)   # right content

# Title (row 0, full width)
tk.Label(outer, text="CSV Merger", font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR) \
    .grid(row=0, column=0, columnspan=3, pady=(15, 5))

# ---- Row 1: Add/Remove/Erase box (LEFT) + credit line (RIGHT) ----
top_box = tk.Frame(outer, bg=BG_COLOR, highlightbackground="#3a4a7a", highlightthickness=2)
top_box.grid(row=1, column=0, sticky="w", padx=20, pady=10)

tk.Button(top_box, text="Add +", width=12, command=add_files,
          bg=FG_COLOR, fg="black", relief="solid", bd=1).pack(side=tk.LEFT, padx=1, pady=1)
tk.Button(top_box, text="Remove", width=14, command=remove_selected,
          bg=FG_COLOR, fg="black", relief="solid", bd=1).pack(side=tk.LEFT, padx=1, pady=1)
tk.Button(top_box, text="Erase all", width=12, command=erase_all,
          bg=FG_COLOR, fg="black", relief="solid", bd=1).pack(side=tk.LEFT, padx=1, pady=1)

tk.Label(outer, text="CSV Merger:  Made by Somendra Dixit",
         font=("Segoe UI", 9, "bold"), bg=BG_COLOR, fg=FG_COLOR) \
    .grid(row=1, column=2, sticky="e", padx=20, pady=10)

# ---- Row 2: Table box (full width) ----
table_box = tk.Frame(outer, bg=BG_COLOR, highlightbackground="#3a4a7a", highlightthickness=2)
table_box.grid(row=2, column=0, columnspan=3, sticky="ew", padx=20, pady=10)

columns = ("file_name", "total_column", "total_row")
tree = ttk.Treeview(table_box, columns=columns, show="headings", height=8)
tree.heading("file_name", text="File name")
tree.heading("total_column", text="Total columns")
tree.heading("total_row", text="Total rows")
tree.column("file_name", width=500)
tree.column("total_column", width=120, anchor="center")
tree.column("total_row", width=120, anchor="center")
tree.pack(fill="x", padx=10, pady=10)

# column_frame placed dynamically at row 3 when "select specific columns" is checked
column_frame = tk.Frame(outer, bg=BG_COLOR)

# "cleaning options" label (row 4)
tk.Label(outer, text="Cleaning options", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg=FG_COLOR) \
    .grid(row=4, column=0, sticky="w", padx=20, pady=(10, 0))

# ---- Row 5: options box (LEFT) + merge box (RIGHT) ----
options_box = tk.Frame(outer, bg=BG_COLOR, highlightbackground="#3a4a7a", highlightthickness=2)
options_box.grid(row=5, column=0, sticky="w", padx=20, pady=10)

tk.Checkbutton(options_box, text="Remove duplicate rows", variable=remove_dup_var,
               bg=BG_COLOR, fg=FG_COLOR, selectcolor="#1a2550", anchor="w").pack(anchor="w", padx=10, pady=3)
tk.Checkbutton(options_box, text="Select specific columns", variable=specific_col_var,
               command=toggle_columns_visibility, bg=BG_COLOR, fg=FG_COLOR, selectcolor="#1a2550",
               anchor="w").pack(anchor="w", padx=10, pady=3)
tk.Checkbutton(options_box, text="Merge all columns", variable=all_col_var,
               command=toggle_all_columns, bg=BG_COLOR, fg=FG_COLOR, selectcolor="#1a2550",
               anchor="w").pack(anchor="w", padx=10, pady=3)

merge_box = tk.Frame(outer, bg=BG_COLOR, highlightbackground="#3a4a7a", highlightthickness=2)
merge_box.grid(row=5, column=2, sticky="e", padx=20, pady=10)

tk.Button(merge_box, text="Merge and save", width=16, height=2, bg=FG_COLOR, fg="black",
          relief="solid", bd=1, command=merge_and_save).grid(row=0, column=0, rowspan=3, padx=15, pady=15)

size_label = tk.Label(merge_box, text="File size: -", bg=BG_COLOR, fg=FG_COLOR)
size_label.grid(row=0, column=1, sticky="w", padx=10)
time_label = tk.Label(merge_box, text="Merging time: -", bg=BG_COLOR, fg=FG_COLOR)
time_label.grid(row=1, column=1, sticky="w", padx=10)
countdown_label = tk.Label(merge_box, text="Time remaining: -", bg=BG_COLOR, fg="#5fa8ff")
countdown_label.grid(row=2, column=1, sticky="w", padx=10)

# ---- Row 6: progress bar (full width) ----
progress_bar = ttk.Progressbar(outer, orient="horizontal", mode="determinate")
progress_bar.grid(row=6, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 5))

result_label = tk.Label(outer, text="", font=("Segoe UI", 9, "bold"), fg="#4caf50", bg=BG_COLOR)
result_label.grid(row=7, column=0, columnspan=3, pady=(0, 10))

root.mainloop()