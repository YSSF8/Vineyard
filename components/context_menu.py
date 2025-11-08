from customtkinter import CTkLabel, CTkToplevel, CTkFrame, CTkButton

class ContextMenu:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.items = []
        self._create_window()