from customtkinter import CTkToplevel, CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkScrollableFrame
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import json
import os
from datetime import datetime

class ThemeMaker:
    _instance = None
    _window = None
    _initialized = False
    _on_close_callback = None
    _color_entries = {}
    _original_colors = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeMaker, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True

    def set_on_close_callback(self, callback):
        self._on_close_callback = callback

    def open(self):
        if self._window is None or not self._window.winfo_exists():
            self.create_window()
        else:
            self._window.lift()
            self._window.focus_force()

    def create_window(self):
        self._window = CTkToplevel()
        self._window.title("Vineyard - Theme Maker")
        self._window.geometry("800x600")
        self._window.resizable(True, True)
        self._window.minsize(700, 500)
        
        self.center_window()

        main_container = CTkFrame(self._window)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=0)
        main_container.grid_columnconfigure(0, weight=1)

        color_pickers_container = CTkFrame(main_container)
        color_pickers_container.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        color_pickers_container.grid_columnconfigure(0, weight=1)
        color_pickers_container.grid_rowconfigure(0, weight=1)

        self.create_color_pickers(color_pickers_container)

        button_frame = CTkFrame(main_container)
        button_frame.grid(row=1, column=0, sticky="ew", pady=0)

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=0)
        button_frame.grid_columnconfigure(2, weight=0)

        cancel_btn = CTkButton(button_frame, text="Cancel", command=self.on_close, 
                              fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        cancel_btn.grid(row=0, column=1, padx=(5, 5), pady=10)

        save_btn = CTkButton(button_frame, text="Save Theme", command=self.save_theme)
        save_btn.grid(row=0, column=2, padx=(0, 0), pady=10)

        self._window.protocol("WM_DELETE_WINDOW", self.on_close)
        self._window.bind("<Destroy>", self._on_destroy)
        self._window.focus_force()

    def create_color_pickers(self, parent):
        scrollable_frame = CTkScrollableFrame(parent)
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)

        scrollable_frame.grid_columnconfigure(0, weight=1)

        try:
            with open('keys.json', 'r', encoding='utf-8') as f:
                keys = json.load(f)
        except FileNotFoundError:
            keys = {}

        row = 0
        for key, value in keys.items():
            if value is None:
                value = "#000000"

            self._original_colors[key] = value

            color_frame = CTkFrame(scrollable_frame)
            color_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
            
            color_frame.grid_columnconfigure(1, weight=1)

            label = CTkLabel(color_frame, text=key, width=200, anchor="w")
            label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")

            color_entry = CTkEntry(color_frame)
            color_entry.insert(0, value)
            color_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self._color_entries[key] = color_entry

            color_preview = CTkLabel(color_frame, text="", width=30, height=20, 
                                   fg_color=value, corner_radius=3)
            color_preview.grid(row=0, column=2, padx=5, pady=5)

            picker_btn = CTkButton(color_frame, text="Pick Color", width=80, height=20,
                                 command=lambda k=key, e=color_entry, p=color_preview: self.choose_color(k, e, p))
            picker_btn.grid(row=0, column=3, padx=(5, 10), pady=5)

            row += 1

    def choose_color(self, key, entry, preview):
        current_color = entry.get()
        color_code = colorchooser.askcolor(
            initialcolor=current_color,
            title=f"Choose color for {key}"
        )
        
        if color_code[1] is not None:
            new_color = color_code[1]
            entry.delete(0, tk.END)
            entry.insert(0, new_color)
            preview.configure(fg_color=new_color)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        else:
            r, g, b = 0, 0, 0
        return f"{r} {g} {b}"

    def save_theme(self):
        try:
            themes_dir = "./themes"
            if not os.path.exists(themes_dir):
                os.makedirs(themes_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"custom_theme_{timestamp}.reg"
            
            filename = filedialog.asksaveasfilename(
                initialdir=themes_dir,
                defaultextension=".reg",
                filetypes=[("Registry files", "*.reg"), ("All files", "*.*")],
                initialfile=default_filename,
                title="Save Theme As"
            )
            
            if not filename:
                return

            reg_content = self.generate_registry_file()

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(reg_content)

            self._original_colors = {key: entry.get() for key, entry in self._color_entries.items()}

            theme_name = os.path.basename(filename)
            messagebox.showinfo("Success", f"Theme saved successfully as:\n{theme_name}.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save theme:\n{str(e)}")

    def generate_registry_file(self):
        lines = []
        lines.append("Windows Registry Editor Version 5.00")
        lines.append("")
        lines.append("[HKEY_CURRENT_USER\\Control Panel\\Colors]")
        
        for key, entry in self._color_entries.items():
            hex_color = entry.get()
            rgb_color = self.hex_to_rgb(hex_color)
            lines.append(f'"{key}"="{rgb_color}"')
        
        return '\n'.join(lines)

    def center_window(self):
        self._window.update_idletasks()
        width = self._window.winfo_width()
        height = self._window.winfo_height()
        x = (self._window.winfo_screenwidth() // 2) - (width // 2)
        y = (self._window.winfo_screenheight() // 2) - (height // 2)
        self._window.geometry(f'{width}x{height}+{x}+{y}')

    def on_close(self):
        if self._window:
            if self._on_close_callback:
                self._on_close_callback()
            self._window.destroy()
            self._window = None

    def _on_destroy(self, event):
        if event.widget == self._window:
            self._window = None
            if self._on_close_callback:
                self._on_close_callback()

    def is_open(self):
        return self._window is not None and self._window.winfo_exists()