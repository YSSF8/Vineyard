from customtkinter import CTkToplevel
import tkinter as tk

class ThemeMaker:
    _instance = None
    _window = None
    _initialized = False
    _on_close_callback = None

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
        self._window.geometry("700x400")
        self._window.resizable(False, False)
        
        self.center_window()
        
        self._window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self._window.bind("<Destroy>", self._on_destroy)
        
        self._window.focus_force()

    def center_window(self):
        self._window.update_idletasks()
        width = 700
        height = 400
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