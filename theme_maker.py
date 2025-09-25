from customtkinter import CTk
import os

class ThemeMaker:
    def __init__(self):
        root = CTk()

        root.title("Vineyard - Theme Maker")
        root.geometry("700x400")
        root.resizable(False, False)
        root.eval('tk::PlaceWindow . center')

        root.mainloop()