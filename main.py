from customtkinter import *
from components.header import Header
from components.header_utilities import *

root = CTk()

root.title("Vineyard")
root.geometry("700x500")

header = CTkFrame(root, height=50, corner_radius=0)
header.pack(fill="x", side="top")

header_init = Header(header)

header_init.add_button("Revert", command=run_revert_command)
header_init.add_button("Open Themes Path", command=open_themes_path)

root.mainloop()