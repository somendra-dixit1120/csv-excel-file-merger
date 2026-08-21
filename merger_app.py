import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

root = tk.Tk()
root.title("CSV / Excel Merger Tool")
root.geometry("700x650")
root.resizable(True, True)   # ab window resize/scroll ho sakti hai

file_paths = []
column_vars = {}
column_mode = tk.StringVar(value="all")


def read_columns(path):
    if path.lower().endswith(".csv"):
        return list(pd.read_csv(path, nrows=0).columns)
    else:
        return list(pd.read_excel(path, nrows=0).columns)


def refresh_columns():
    for widget in column_frame.winfo_children():
        widget.destroy()
    column_vars.clear()
    if not file_paths:
        return
    col_sets = [set(read_columns(p)) for p in file_paths]
    common = set.intersection(*col_sets)
    first_file_cols = read_columns(file_paths[0])
    common_columns = [c for c in first_file_cols if c in common]
    if not common_columns:
        tk.Label(column_frame, text="Files me koi common column nahi mila!", fg="red").pack()
        return
    for col in common_columns:
        var = tk.IntVar(value=1)
        tk.Checkbutton(column_frame, text=col, variable=var).pack(anchor="w")
        column_vars[col] = var
    toggle_column_visibility()


def toggle_column_visibility():
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


def merge_and_export():
    if not file_paths:
        messagebox.showwarning("Koi file nahi", "Pehle kam se kam 1 file select karo.")
        return

    # kaunse columns rakhne hain
    if column_mode.get() == "specific":
        chosen_cols = [c for c, v in column_vars.items() if v.get() == 1]
        if not chosen_cols:
            messagebox.showwarning("Column chuno", "Kam se kam ek column select karo.")
            return
    else:
        chosen_cols = None   # None = sab columns

    dataframes = []
    for path in file_paths:
        if path.lower().endswith(".csv"):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)
        if chosen_cols:
            df = df[chosen_cols]   # sirf selected columns rakho
        dataframes.append(df)

    merged = pd.concat(dataframes, ignore_index=True)
    before = len(merged)
    merged = merged.drop_duplicates()   # poori row match wala duplicate hatao
    after = len(merged)

    # --- Save location poochho ---
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

    messagebox.showinfo("Ho gaya!",
        f"Master file save ho gayi:\n{save_path}\n\n"
        f"Total rows: {after} ({before - after} duplicate hataye gaye)")


# --- Buttons ---
add_btn = tk.Button(root, text="+ Add Files", command=add_files, bg="#2e7d32", fg="white")
add_btn.pack(pady=10)

file_listbox = tk.Listbox(root, width=90, height=8, selectmode=tk.EXTENDED)
file_listbox.pack(pady=5)

status_label = tk.Label(root, text="Koi file select nahi hui.")
status_label.pack()

mode_frame = tk.LabelFrame(root, text="Kaunse columns collect karne hain?", padx=10, pady=10)
mode_frame.pack(pady=10, fill="x", padx=20)

tk.Radiobutton(mode_frame, text="Sab columns (poori file)", variable=column_mode,
               value="all", command=toggle_column_visibility).pack(anchor="w")
tk.Radiobutton(mode_frame, text="Sirf specific columns (neeche se chuno)", variable=column_mode,
               value="specific", command=toggle_column_visibility).pack(anchor="w")

column_frame = tk.Frame(root)

merge_btn = tk.Button(root, text="Merge & Export Master File", width=30, height=2,
                       bg="#1565c0", fg="white", command=merge_and_export)
merge_btn.pack(pady=15)

root.mainloop()