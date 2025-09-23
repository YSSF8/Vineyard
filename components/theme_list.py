from customtkinter import *
import os
import subprocess
import sys

THEMES_PATH = os.path.join(os.getcwd(), 'themes')

class ThemeList:
    def __init__(self, parent, console):
        self.console = console 
        self.frame = CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.title_label = CTkLabel(self.frame, text="Available Themes", font=CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(0, 10))
        
        self.scrollable_frame = CTkScrollableFrame(self.frame, height=400)
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.theme_buttons = {}
        
        self.load_themes()

    def load_themes(self):
        if not os.path.exists(THEMES_PATH):
            os.makedirs(THEMES_PATH)
            self.console.info(f"Created themes directory at: {THEMES_PATH}")

        themes = [f for f in os.listdir(THEMES_PATH) if f.endswith('.reg') and f != 'revert.reg']
        
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
        
        name_label = CTkLabel(theme_frame, text=theme_name, anchor="w")
        name_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
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
    def create_theme_button(self, theme_name):
        theme_frame = CTkFrame(self.scrollable_frame)
        theme_frame.pack(fill="x", padx=5, pady=2)
        
        display_name = theme_name.replace(".reg", "")
        name_label = CTkLabel(theme_frame, text=display_name, anchor="w")
        name_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
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
            'delete_btn': delete_btn
        }
        
        self.theme_buttons[theme_name] = {
            'frame': theme_frame,
            'apply_btn': apply_btn,
            'delete_btn': delete_btn
        }

    def apply_theme(self, theme_name):
        theme_path = os.path.join(THEMES_PATH, theme_name)
        self.console.system(f"Applying theme: {theme_name}")

        try:
            if sys.platform == "linux":
                command = ['wine', 'regedit', theme_path]
                self.console.info("Using 'wine regedit' for Linux.")

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            self.console.success(f"Successfully applied theme: {theme_name}")
            self.console.debug(f"Command output: {result.stdout}")

        except subprocess.CalledProcessError as e:
            self.console.error(f"Failed to apply theme {theme_name}: {e.stderr}")
        except FileNotFoundError:
            if sys.platform == "linux":
                self.console.error("'wine' command not found. Please ensure Wine is installed and in your PATH.")
        except Exception as e:
            self.console.error(f"Unexpected error applying theme: {str(e)}")

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