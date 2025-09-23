from customtkinter import *

class MessageBox():
    def __init__(self, title: str, message: str):
        root = CTk()

        root.title(title)
        root.geometry("300x150")

        text = CTkLabel(root, text=message)
        text.pack(pady=20)

        root.mainloop()