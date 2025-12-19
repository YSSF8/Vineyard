from customtkinter import *
from tkinter import filedialog, messagebox
import os
import subprocess
import threading
import json
import re
from .ron_converter import RonConverter, MODERN_KEYS, LEGACY_KEYS

THEMES_PATH = os.path.join(os.getcwd(), 'themes')

class ThemeList:
    def __init__(self, parent, console):
        self.console = console
        self.parent_window = parent.winfo_toplevel()
        
        self.wine_major_version = self._detect_wine_version()
        
        self.frame = CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._update_allowed_keys()

        self.header_frame = CTkFrame(self.frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)
        self.header_frame.grid_columnconfigure(2, weight=1)

        self.title_label = CTkLabel(self.header_frame, text="Available Themes", font=CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=1)

        self.import_btn = CTkButton(self.header_frame, text="Import .ron", width=100, command=self.import_ron_theme)
        self.import_btn.grid(row=0, column=2, sticky="e")

        self.scrollable_frame = CTkScrollableFrame(self.frame)
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.theme_buttons = {}
        self._loading_task = None
        
        self._setup_global_scroll()
        self.load_themes()

    def _detect_wine_version(self):
        try:
            result = subprocess.run(['wine', '--version'], capture_output=True, text=True)
            output = result.stdout.strip()
            
            match = re.search(r"wine-(\d+)", output)
            if match:
                version = int(match.group(1))
                self.console.info(f"Detected Wine System: {output} (Major: {version})")
                return version
            
            self.console.warning(f"Could not parse Wine version from '{output}'. Defaulting to Legacy.")
            return 8
        except FileNotFoundError:
            self.console.error("Wine not found. Defaulting to Legacy mode.")
            return 8
        except Exception as e:
            self.console.error(f"Error checking version: {e}")
            return 8

    def _update_allowed_keys(self):
        target_keys = MODERN_KEYS if self.wine_major_version >= 9 else LEGACY_KEYS
        try:
            current = {}
            if os.path.exists('keys.json'):
                with open('keys.json', 'r') as f: current = json.load(f)
            
            updated = False
            for key in target_keys:
                if key not in current:
                    current[key] = "Color"
                    updated = True
            
            if updated or not os.path.exists('keys.json'):
                with open('keys.json', 'w') as f: json.dump(current, f, indent=4)
        except: pass

    def _setup_global_scroll(self):
        def _on_wheel(e):
            if not self.scrollable_frame.winfo_exists(): return
            try:
                if os.name == "nt" and e.delta:
                    self.scrollable_frame._parent_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
                elif e.num == 4: self.scrollable_frame._parent_canvas.yview_scroll(-1, "units")
                elif e.num == 5: self.scrollable_frame._parent_canvas.yview_scroll(1, "units")
            except: pass
        self.parent_window.bind("<MouseWheel>", _on_wheel, add="+")
        self.parent_window.bind("<Button-4>", _on_wheel, add="+")
        self.parent_window.bind("<Button-5>", _on_wheel, add="+")

    def load_themes(self):
        if self._loading_task: self.frame.after_cancel(self._loading_task)
        for w in self.scrollable_frame.winfo_children(): w.destroy()
        self.theme_buttons = {}

        if not os.path.exists(THEMES_PATH): os.makedirs(THEMES_PATH)
        themes = sorted([f for f in os.listdir(THEMES_PATH) if f.endswith('.reg') and f != 'revert.reg'], key=lambda x: x.lower())
        
        if not themes:
            CTkLabel(self.scrollable_frame, text="No themes found.", font=CTkFont(size=14)).pack(pady=20)
            return

        def batch(start=0):
            if not self.scrollable_frame.winfo_exists(): return
            end = min(start + 15, len(themes))
            for i in range(start, end): self.create_theme_btn(themes[i])
            if end < len(themes): self._loading_task = self.frame.after(10, lambda: batch(end))
        batch()

    def create_theme_btn(self, name):
        f = CTkFrame(self.scrollable_frame)
        f.pack(fill="x", padx=5, pady=2)
        CTkLabel(f, text=os.path.splitext(name)[0], anchor="w").pack(side="left", padx=10, fill="x", expand=True)
        
        def b(txt, cmd, c=None, h=None):
            btn = CTkButton(f, text=txt, width=60, command=cmd)
            if c: btn.configure(fg_color=c)
            if h: btn.configure(hover_color=h)
            btn.pack(side="right", padx=5, pady=5)
        
        b("Delete", lambda: self.delete_theme(name), "#d9534f", "#c9302c")
        b("Apply", lambda: self.apply_theme(name))
        b("Edit", lambda: self.edit_theme(name))
        self.theme_buttons[name] = {'frame': f}

    def edit_theme(self, name):
        from theme_maker import ThemeMaker
        ThemeMaker().open_in_edit_mode(os.path.join(THEMES_PATH, name), name)

    def apply_theme(self, name):
        path = os.path.join(THEMES_PATH, name)
        self.console.system(f"Applying {name}...")
        threading.Thread(target=lambda: self._run_apply(path, name), daemon=True).start()

    def _run_apply(self, path, name):
        try:
            subprocess.run(['wine', 'regedit', '/S', path], capture_output=True, text=True, check=True)
            self.console.success(f"Applied: {name}")
            if self.wine_major_version >= 9:
                self.console.info("Wine 9.0+ detected: Restart running apps to see changes.")
        except Exception as e:
            self.console.error(f"Error applying theme: {e}")

    def delete_theme(self, name):
        if messagebox.askyesno("Confirm", f"Delete {name}?"):
            try:
                os.remove(os.path.join(THEMES_PATH, name))
                if name in self.theme_buttons:
                    self.theme_buttons[name]['frame'].destroy()
                    del self.theme_buttons[name]
            except: pass

    def filter_themes(self, query):
        query = query.lower()
        visible_themes = []
        for theme_name, widgets in self.theme_buttons.items():
            display_name = os.path.splitext(theme_name)[0].lower()
            if query in display_name:
                visible_themes.append((display_name, widgets))
            else:
                widgets['frame'].pack_forget()

        visible_themes.sort(key=lambda x: x[0])
        for _, widgets in visible_themes:
            widgets['frame'].pack(fill="x", padx=5, pady=2)

    def import_ron_theme(self):
        path = filedialog.askopenfilename(filetypes=[("RON", "*.ron"), ("All", "*.*")])
        if not path: return
        try:
            name = os.path.splitext(os.path.basename(path))[0]
            with open(path, 'r', encoding='utf-8') as f: content = f.read()
            
            self.console.system(f"Transpiling {name} (Target: Wine {self.wine_major_version})...")
            
            reg = RonConverter.convert(content, name, self.wine_major_version)
            
            with open(os.path.join(THEMES_PATH, f"{name}.reg"), 'w', encoding='utf-8') as f: f.write(reg)
            self.console.success(f"Imported: {name}")
            self.load_themes()
        except Exception as e: self.console.error(f"Import failed: {e}")