from customtkinter import *
import os
import subprocess
import threading
import json

THEMES_PATH = os.path.join(os.getcwd(), 'themes')

class ThemeList:
    def __init__(self, parent, console):
        self.console = console
        self.frame = CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.title_label = CTkLabel(self.frame, text="Available Themes", font=CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(0, 10))
        
        self.scrollable_frame = CTkScrollableFrame(self.frame)
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.theme_buttons = {}
        
        self.load_themes()

    def load_themes(self):
        if not os.path.exists(THEMES_PATH):
            os.makedirs(THEMES_PATH)
            self.console.info(f"Created themes directory at: {THEMES_PATH}")

        themes = sorted([f for f in os.listdir(THEMES_PATH) if f.endswith('.reg') and f != 'revert.reg'], key=lambda x: os.path.splitext(x)[0].lower())
        
        if not themes:
            no_themes_label = CTkLabel(self.scrollable_frame, text="No themes found. Please add a .reg file to the themes directory to see it here.", font=CTkFont(size=14))
            no_themes_label.pack(pady=20)
            self.console.warning("No theme files found in themes directory")
            return
        
        self.console.info(f"Found {len(themes)} theme(s) in themes directory")
        for theme in themes:
            self.create_theme_button(theme)

    def create_theme_button(self, theme_name):
        theme_frame = CTkFrame(self.scrollable_frame)
        theme_frame.pack(fill="x", padx=5, pady=2)
        
        display_name = os.path.splitext(theme_name)[0]
        name_label = CTkLabel(theme_frame, text=display_name, anchor="w")
        name_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
        edit_btn = CTkButton(
            theme_frame,
            text="Edit",
            width=60,
            command=lambda t=theme_name: self.edit_theme(t)
        )
        edit_btn.pack(side="right", padx=5, pady=5)
        
        apply_btn = CTkButton(
            theme_frame,
            text="Apply",
            width=60,
            command=lambda t=theme_name: self.apply_theme(t)
        )
        apply_btn.pack(side="right", padx=5, pady=5)
        
        delete_btn = CTkButton(
            theme_frame, 
            text="Delete", 
            width=60,
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=lambda t=theme_name: self.delete_theme(t)
        )
        delete_btn.pack(side="right", padx=5, pady=5)
        
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
                        with open(path, "r", encoding="utf-16") as f:
                            content = f.read()
                        return content
                    except UnicodeError:
                        with open(path, "rb") as f:
                            content = f.read()
                        return content.decode("utf-16-le")
                else:
                    with open(path, "r", encoding=enc) as f:
                        return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
            
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except:
            raise ValueError(f"Could not decode {path} with tried encodings {encodings}")

    def convert_reg_to_dict(self, reg_content):
        reg_dict = {}
        lines = reg_content.splitlines()
        current_path = None
        in_colors_section = False

        for line in lines:
            line = line.strip()
            if not line or line.startswith(";") or line.startswith("Windows Registry Editor"):
                continue

            if line.startswith("[") and line.endswith("]"):
                current_path = line[1:-1]
                in_colors_section = "Control Panel\\Colors" in current_path
                continue

            elif '=' in line and in_colors_section:
                key, value = line.split("=", 1)
                key = key.strip().strip('"')
                value = value.strip().strip('"')
                reg_dict[key] = value

        return reg_dict

    def normalize_key(self, key):
        return key.strip().lower()
    
    def validate_theme(self, theme_dict, allowed_dict, path="root"):
        if not isinstance(theme_dict, dict):
            return True

        colors_section = theme_dict
        if "HKEY_CURRENT_USER" in theme_dict:
            colors_section = theme_dict["HKEY_CURRENT_USER"]
            if "Control Panel" in colors_section:
                colors_section = colors_section["Control Panel"]
                if "Colors" in colors_section:
                    colors_section = colors_section["Colors"]

        norm_allowed = {self.normalize_key(k): v for k, v in allowed_dict.items()}

        for key, value in colors_section.items():
            norm_key = self.normalize_key(key)
            if norm_key not in norm_allowed:
                self.console.error(f"Unknown key '{key}' at path '{path}'")
                return False

            if isinstance(value, dict):
                if not self.validate_theme(value, norm_allowed[norm_key], path=f"{path}\\{key}"):
                    return False

        return True

    def apply_theme(self, theme_name):
        theme_path = os.path.join(THEMES_PATH, theme_name)
        display_name = os.path.splitext(theme_name)[0]

        self.console.system(f"Validating theme: {display_name}...")

        with open('keys.json', 'r') as f:
            allowed_keys = json.load(f)

        reg_content = self.read_reg_file(theme_path)
        theme_dict = self.convert_reg_to_dict(reg_content)

        if not self.validate_theme(theme_dict, allowed_keys):
            self.console.error(f"Theme {display_name} contains unknown keys. Aborting.")
            return

        self.console.system(f"Applying theme: {display_name}...")

        def run_theme():
            try:
                command = ['wine', 'regedit', theme_path]
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.console.success(f"Successfully applied theme: {display_name}")
            except subprocess.CalledProcessError as e:
                self.console.error(f"Failed to apply theme {display_name}: {e.stderr}")
            except FileNotFoundError:
                self.console.error("'wine' command not found. Please ensure Wine is installed and in your PATH.")
            except Exception as e:
                self.console.error(f"Unexpected error applying theme: {str(e)}")

        threading.Thread(target=run_theme, daemon=True).start()

    def delete_theme(self, theme_name):
        theme_path = os.path.join(THEMES_PATH, theme_name)
        
        from tkinter import messagebox
        import tkinter as tk
        
        root = self.frame.winfo_toplevel()
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {theme_name}?")
        
        if result:
            try:
                os.remove(theme_path)
                self.console.success(f"Deleted theme: {theme_name}")
                
                if theme_name in self.theme_buttons:
                    self.theme_buttons[theme_name]['frame'].destroy()
                    del self.theme_buttons[theme_name]
                    
            except Exception as e:
                self.console.error(f"Could not delete theme: {str(e)}")
                messagebox.showerror("Error", f"Could not delete theme: {str(e)}")

    def refresh_themes(self):
        self.console.system("Refreshing theme list...")
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.theme_buttons.clear()
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