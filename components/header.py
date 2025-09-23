from customtkinter import CTkFrame, CTkButton

class Header(CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, height=50, corner_radius=0, **kwargs)
        self.pack(fill="x", side="top")

    def add_button(self, text, command=None):
        button = CTkButton(self, text=text, command=command)
        button.pack(pady=5, padx=5, side="right", anchor="n")
        return button