from customtkinter import CTkFrame, CTkButton, CTkEntry

class Header(CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, height=50, corner_radius=0, **kwargs)
        self.pack(fill="x", side="top")

    def add_button(self, text, command=None):
        button = CTkButton(self, text=text, command=command)
        button.pack(pady=5, padx=2, side="right", anchor="n")
        return button

    def add_search(self, callback):
        search_entry = CTkEntry(self, placeholder_text="Search themes...")
        search_entry.pack(pady=5, padx=5, side="left", anchor="n", fill="x", expand=True)

        def on_key_release(event):
            query = search_entry.get().strip()
            callback(query)

        search_entry.bind("<KeyRelease>", on_key_release)
        return search_entry