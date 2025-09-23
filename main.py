from customtkinter import *
from components.header import Header
from components.header_utilities import *
from components.theme_list import ThemeList

set_appearance_mode("dark")
set_default_color_theme("blue")

root = CTk()
root.title("Vineyard - Theme Manager")
root.geometry("700x500")

header = CTkFrame(root, height=50, corner_radius=0)
header.pack(fill="x", side="top")

header_init = Header(header)

header_init.add_button("Revert", command=run_revert_command)
header_init.add_button("Open Themes Path", command=open_themes_path)
header_init.add_button("Refresh", command=lambda: theme_list.refresh_themes())

theme_list = ThemeList(root)

status_bar = CTkFrame(root, height=30, corner_radius=0)
status_bar.pack(fill="x", side="bottom")
status_label = CTkLabel(status_bar, text="Ready")
status_label.pack(side="left", padx=10)

root.mainloop()