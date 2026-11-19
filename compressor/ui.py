import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List
from .engine import ImageCompressor

class CompressorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Compressor & Optimizer")
        self.geometry("780x560")
        self.minsize(640, 480)
        self.engine = ImageCompressor()
        self.file_list: List[str] = []
        self._init_theme()
        self._build_ui()

    def _init_theme(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.configure(bg="#f4f6f9")
        self.style.configure("TFrame", background="#f4f6f9")
        self.style.configure("TLabel", background="#f4f6f9", font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 15, "bold"), foreground="#2c3e50")
        self.style.configure("Accent.TButton", font=("Helvetica", 10, "bold"), background="#2980b9", foreground="white")
        self.style.map("Accent.TButton", background=[("active", "#3498db")])

    def _build_ui(self):
        header_frame = ttk.Frame(self, padding="15 10 15 5")
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Image Compressor Studio", style="Header.TLabel").pack(side=tk.LEFT)

        ctrl_frame = ttk.LabelFrame(self, text=" Compression Settings ", padding=10)
        ctrl_frame.pack(fill=tk.X, padx=15, pady=5)

        ttk.Label(ctrl_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.quality_var = tk.IntVar(value=75)
        self.quality_slider = ttk.Scale(ctrl_frame, from_=10, to=100, variable=self.quality_var, orient=tk.HORIZONTAL, command=self._update_quality_lbl)
        self.quality_slider.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.quality_val_lbl = ttk.Label(ctrl_frame, text="75%")
        self.quality_val_lbl.grid(row=0, column=2, sticky=tk.W, padx=5)

        ttk.Label(ctrl_frame, text="Format:").grid(row=0, column=3, sticky=tk.W, padx=5)
        self.fmt_var = tk.StringVar(value="ORIGINAL")
        fmt_combo = ttk.Combobox(ctrl_frame, textvariable=self.fmt_var, values=["ORIGINAL", "JPEG", "WEBP", "PNG"], width=10, state="readonly")
        fmt_combo.grid(row=0, column=4, sticky=tk.W, padx=5)

        ttk.Label(ctrl_frame, text="Max Dim (px):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=4)
        self.max_dim_var = tk.StringVar(value="1920")
        dim_entry = ttk.Entry(ctrl_frame, textvariable=self.max_dim_var, width=10)
        dim_entry.grid(row=1, column=1, sticky=tk.W, padx=5)

        ttk.Label(ctrl_frame, text="Target KB (0=Ignore):").grid(row=1, column=3, sticky=tk.W, padx=5)
        self.target_kb_var = tk.StringVar(value="0")
        kb_entry = ttk.Entry(ctrl_frame, textvariable=self.target_kb_var, width=10)
        kb_entry.grid(row=1, column=4, sticky=tk.W, padx=5)
        ctrl_frame.columnconfigure(1, weight=1)

        list_frame = ttk.Frame(self, padding="15 5 15 5")
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("path", "orig_size", "status"), show="headings", height=10)
        self.tree.heading("path", text="File Path")
        self.tree.heading("orig_size", text="Original Size")
        self.tree.heading("status", text="Status / Reduction")
        self.tree.column("path", width=380, anchor=tk.W)
        self.tree.column("orig_size", width=110, anchor=tk.E)
        self.tree.column("status", width=180, anchor=tk.CENTER)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(self, padding="15 10 15 10")
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="+ Add Files", command=self._add_files).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="+ Add Folder", command=self._add_folder).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Clear", command=self._clear_list).pack(side=tk.LEFT, padx=3)

        self.start_btn = ttk.Button(btn_frame, text="Start Compression", style="Accent.TButton", command=self._start_thread)
        self.start_btn.pack(side=tk.RIGHT, padx=3)

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill=tk.X, padx=15, pady=(0, 10))

    def _update_quality_lbl(self, val):
        self.quality_val_lbl.config(text=f"{int(float(val))}%")

    def _add_files(self):
        exts = self.engine.get_supported_extensions()
        pat = " ".join(f"*{e}" for e in exts)
        files = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", pat), ("All Files", "*.*")])
        for f in files:
            if f not in self.file_list:
                self.file_list.append(f)
                sz = os.path.getsize(f) / 1024.0
                self.tree.insert("", tk.END, iid=f, values=(os.path.basename(f), f"{sz:.1f} KB", "Ready"))

    def _add_folder(self):
        folder = filedialog.askdirectory(title="Select Image Folder")
        if not folder:
            return
        exts = self.engine.get_supported_extensions()
        for root, _, files in os.walk(folder):
            for file in files:
                if any(file.lower().endswith(e) for e in exts):
                    path = os.path.join(root, file)
                    if path not in self.file_list:
                        self.file_list.append(path)
                        sz = os.path.getsize(path) / 1024.0
                        self.tree.insert("", tk.END, iid=path, values=(os.path.basename(path), f"{sz:.1f} KB", "Ready"))

    def _clear_list(self):
        self.tree.delete(*self.tree.get_children())
        self.file_list.clear()

    def _start_thread(self):
        if not self.file_list:
            messagebox.showinfo("Info", "Please add images to compress first.")
            return
        out_dir = filedialog.askdirectory(title="Select Output Destination")
        if not out_dir:
            return
        self.start_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._process_batch, args=(out_dir,), daemon=True).start()

    def _process_batch(self, out_dir: str):
        try:
            max_d = int(self.max_dim_var.get()) if self.max_dim_var.get().strip() else None
        except ValueError:
            max_d = None

        try:
            target_kb = int(self.target_kb_var.get()) if self.target_kb_var.get().strip() else 0
        except ValueError:
            target_kb = 0

        total = len(self.file_list)
        self.progress["maximum"] = total
        self.progress["value"] = 0

        for i, src_path in enumerate(self.file_list):
            base, orig_ext = os.path.splitext(os.path.basename(src_path))
            selected_fmt = self.fmt_var.get()
            ext = f".{selected_fmt.lower()}" if selected_fmt != "ORIGINAL" else orig_ext
            out_path = os.path.join(out_dir, f"{base}_compressed{ext}")

            fmt_param = None if selected_fmt == "ORIGINAL" else selected_fmt
            res = self.engine.compress_single(
                input_path=src_path,
                output_path=out_path,
                quality=int(self.quality_var.get()),
                max_dimension=max_d,
                target_format=fmt_param,
                target_kb=target_kb
            )
            if res.success:
                msg = f"Saved {res.saved_percent}% ({res.compressed_bytes/1024:.1f} KB)"
            else:
                msg = f"Failed: {res.error_message}"
            self.after(0, self._update_row_status, src_path, msg, i + 1)

        self.after(0, self._on_finish)

    def _update_row_status(self, item_id: str, status_msg: str, progress_val: int):
        if self.tree.exists(item_id):
            vals = self.tree.item(item_id, "values")
            self.tree.item(item_id, values=(vals[0], vals[1], status_msg))
        self.progress["value"] = progress_val

    def _on_finish(self):
        self.start_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Completed", "Batch compression task finished!")
