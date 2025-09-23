from customtkinter import *
import os

THEMES_PATH = os.path.join(os.getcwd(), 'themes')

class ThemeList:
    def __init__(self, parent):
        self.frame = CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.title_label = CTkLabel(self.frame, text="Available Themes", font=CTkFont(size=16, weight="bold"))
        self.title_label.pack(pady=(0, 10))
        
        self.scrollable_frame = CTkScrollableFrame(self.frame, height=300)
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.theme_buttons = {}
        
        self.load_themes()

    def load_themes(self):
        if not os.path.exists(THEMES_PATH):
            os.makedirs(THEMES_PATH)
            print(f"Created themes directory at: {THEMES_PATH}")

        themes = [f for f in os.listdir(THEMES_PATH) if f.endswith('.reg') and f != 'revert.reg']
        
        if not themes:
            no_themes_label = CTkLabel(self.scrollable_frame, text="No theme files found in themes directory")
            no_themes_label.pack(pady=20)
            return
        
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
        delete_btn.pack(side="right", padx=5, pady=5)
        
        self.theme_buttons[theme_name] = {
            'frame': theme_frame,
            'apply_btn': apply_btn,
            'delete_btn': delete_btn
        }
    
    def apply_theme(self, theme_name):
        print(f"Applying theme: {theme_name}")
    
    def delete_theme(self, theme_name):
        theme_path = os.path.join(THEMES_PATH, theme_name)
        
        from tkinter import messagebox
        import tkinter as tk
        
        root = self.frame.winfo_toplevel()
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {theme_name}?")
        
        if result:
            try:
                os.remove(theme_path)
                print(f"Deleted theme: {theme_name}")
                
                if theme_name in self.theme_buttons:
                    self.theme_buttons[theme_name]['frame'].destroy()
                    del self.theme_buttons[theme_name]
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete theme: {str(e)}")
    
    def refresh_themes(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.theme_buttons.clear()
        self.load_themes()