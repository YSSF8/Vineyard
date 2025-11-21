from customtkinter import *
import os
import subprocess
import threading
import json

THEMES_PATH = os.path.join(os.getcwd(), 'themes')

class ThemeList:
    def __init__(self, parent, console):
        self.console = console
        self.parent_window = parent.winfo_toplevel()
        self.frame = CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.title_label = CTkLabel(self.frame, text="Available Themes", font=CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(0, 10))
        
        self.scrollable_frame = CTkScrollableFrame(self.frame)
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.theme_buttons = {}
        self._loading_task = None
        
        self._setup_global_scroll()
        
        self.load_themes()

    def _setup_global_scroll(self):
        def _on_mouse_wheel(event):
            if not self.scrollable_frame.winfo_exists() or not self.scrollable_frame.winfo_viewable():
                return

            try:
                x1 = self.scrollable_frame.winfo_rootx()
                y1 = self.scrollable_frame.winfo_rooty()
                x2 = x1 + self.scrollable_frame.winfo_width()
                y2 = y1 + self.scrollable_frame.winfo_height()
                
                if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
                    if os.name == "nt":
                        if event.delta:
                            units = int(-1 * (event.delta / 120))
                            self.scrollable_frame._parent_canvas.yview_scroll(units, "units")
                    elif event.num == 4:
                         self.scrollable_frame._parent_canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                         self.scrollable_frame._parent_canvas.yview_scroll(1, "units")
            except Exception:
                pass

        self.parent_window.bind("<MouseWheel>", _on_mouse_wheel, add="+")
        self.parent_window.bind("<Button-4>", _on_mouse_wheel, add="+")
        self.parent_window.bind("<Button-5>", _on_mouse_wheel, add="+")

    def load_themes(self):
        if self._loading_task:
            self.frame.after_cancel(self._loading_task)

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.theme_buttons = {}

        if not os.path.exists(THEMES_PATH):
            os.makedirs(THEMES_PATH)
            self.console.info(f"Created themes directory at: {THEMES_PATH}")

        themes = sorted([f for f in os.listdir(THEMES_PATH) if f.endswith('.reg') and f != 'revert.reg'], key=lambda x: os.path.splitext(x)[0].lower())
        
        if not themes:
            no_themes_label = CTkLabel(self.scrollable_frame, text="No themes found. Please add a .reg file to the themes directory.", font=CTkFont(size=14))
            no_themes_label.pack(pady=20)
            self.console.warning("No theme files found in themes directory")
            return
        
        self.console.info(f"Found {len(themes)} theme(s)")

        initial_batch = 15
        subsequent_batch = 20
        
        def process_batch(start_index, is_initial=False):
            if not self.scrollable_frame.winfo_exists(): return

            batch_limit = initial_batch if is_initial else subsequent_batch
            end_index = min(start_index + batch_limit, len(themes))

            for i in range(start_index, end_index):
                self.create_theme_button(themes[i])

            if end_index < len(themes):
                self._loading_task = self.frame.after(10, lambda: process_batch(end_index, False))

        process_batch(0, is_initial=True)

    def create_theme_button(self, theme_name):
        theme_frame = CTkFrame(self.scrollable_frame)
        theme_frame.pack(fill="x", padx=5, pady=2)
        
        display_name = os.path.splitext(theme_name)[0]
        name_label = CTkLabel(theme_frame, text=display_name, anchor="w")
        name_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
        def create_btn(text, cmd, color=None, hover=None):
            btn = CTkButton(
                theme_frame, text=text, width=60, command=cmd
            )
            if color: btn.configure(fg_color=color)
            if hover: btn.configure(hover_color=hover)
            btn.pack(side="right", padx=5, pady=5)
            return btn

        delete_btn = create_btn("Delete", lambda: self.delete_theme(theme_name), "#d9534f", "#c9302c")
        apply_btn = create_btn("Apply", lambda: self.apply_theme(theme_name))
        edit_btn = create_btn("Edit", lambda: self.edit_theme(theme_name))
        
        self.theme_buttons[theme_name] = {
            'frame': theme_frame,
            'apply_btn': apply_btn,
            'edit_btn': edit_btn,
            'delete_btn': delete_btn
        }
    
    def edit_theme(self, theme_name):
        theme_path = os.path.join(THEMES_PATH, theme_name)
        display_name = os.path.splitext(theme_name)[0]
        self.console.system(f"Opening theme for editing: {display_name}")
        
        from theme_maker import ThemeMaker
        theme_maker = ThemeMaker()
        theme_maker.open_in_edit_mode(theme_path, theme_name)
    
    def set_theme_maker(self, theme_maker_instance):
        self.theme_maker = theme_maker_instance
    
    def read_reg_file(self, path):
        encodings = ["utf-16", "utf-8", "latin-1", "cp1252"]
        for enc in encodings:
            try:
                if enc == "utf-16":
                    try:
                        with open(path, "r", encoding="utf-16") as f: return f.read()
                    except UnicodeError:
                        with open(path, "rb") as f: return f.read().decode("utf-16-le")
                else:
                    with open(path, "r", encoding=enc) as f: return f.read()
            except (UnicodeDecodeError, UnicodeError): continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f: return f.read()
        except:
            raise ValueError(f"Could not decode {path}")

    def convert_reg_to_dict(self, reg_content):
        reg_dict = {}
        lines = reg_content.splitlines()
        in_colors_section = False

        for line in lines:
            line = line.strip()
            if not line or line.startswith(";") or line.startswith("Windows"): continue

            if line.startswith("[") and line.endswith("]"):
                in_colors_section = "Control Panel\\Colors" in line
                continue

            elif '=' in line and in_colors_section:
                try:
                    key, value = line.split("=", 1)
                    reg_dict[key.strip().strip('"')] = value.strip().strip('"')
                except: continue

        return reg_dict

    def normalize_key(self, key):
        return key.strip().lower()
    
    def validate_theme(self, theme_dict, allowed_dict, path="root"):
        if not isinstance(theme_dict, dict): return True

        colors_section = theme_dict
        if "HKEY_CURRENT_USER" in theme_dict:
            colors_section = theme_dict.get("HKEY_CURRENT_USER", {}).get("Control Panel", {}).get("Colors", {})

        norm_allowed = {self.normalize_key(k): v for k, v in allowed_dict.items()}

        for key, value in colors_section.items():
            if self.normalize_key(key) not in norm_allowed:
                self.console.error(f"Unknown key '{key}'")
                return False
        return True

    def apply_theme(self, theme_name):
        theme_path = os.path.join(THEMES_PATH, theme_name)
        display_name = os.path.splitext(theme_name)[0]
        self.console.system(f"Validating theme: {display_name}...")

        try:
            with open('keys.json', 'r') as f: allowed_keys = json.load(f)
        except: allowed_keys = {}

        reg_content = self.read_reg_file(theme_path)
        theme_dict = self.convert_reg_to_dict(reg_content)

        if not self.validate_theme(theme_dict, allowed_keys):
            self.console.error(f"Theme {display_name} contains unknown keys. Aborting.")
            return

        self.console.system(f"Applying theme: {display_name}...")

        def run_theme():
            try:
                result = subprocess.run(['wine', 'regedit', theme_path], capture_output=True, text=True, check=True)
                self.console.success(f"Successfully applied theme: {display_name}")
            except subprocess.CalledProcessError as e:
                self.console.error(f"Failed to apply theme {display_name}: {e.stderr}")
            except FileNotFoundError:
                self.console.error("'wine' command not found.")
            except Exception as e:
                self.console.error(f"Error applying theme: {str(e)}")

        threading.Thread(target=run_theme, daemon=True).start()

    def delete_theme(self, theme_name):
        from tkinter import messagebox
        theme_path = os.path.join(THEMES_PATH, theme_name)
        
        if messagebox.askyesno("Confirm Delete", f"Delete {theme_name}?"):
            try:
                os.remove(theme_path)
                self.console.success(f"Deleted theme: {theme_name}")

                if theme_name in self.theme_buttons:
                    self.theme_buttons[theme_name]['frame'].destroy()
                    del self.theme_buttons[theme_name]
            except Exception as e:
                self.console.error(f"Could not delete theme: {str(e)}")

    def refresh_themes(self):
        self.console.system("Refreshing theme list...")
        self.load_themes()
        self.console.success("Theme list refreshed successfully")
    
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