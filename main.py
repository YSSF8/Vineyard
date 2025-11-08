from customtkinter import *
from components.header import Header
from components.header_utilities import *
from components.theme_list import ThemeList
from components.console import Console
from theme_maker import ThemeMaker

set_appearance_mode("dark")
set_default_color_theme("blue")

root = CTk()
root.title("Vineyard V1.1")
root.geometry("700x600")

try:
    root.state("zoomed")
except Exception:
    try:
        root.attributes("-zoomed", True)
    except Exception:
        root.update_idletasks()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        root.geometry(f"{w}x{h}+0+0")

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

header = CTkFrame(root, height=50, corner_radius=0)
header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

main_content = CTkFrame(root)
main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
main_content.grid_rowconfigure(0, weight=3)
main_content.grid_rowconfigure(1, weight=1)
main_content.grid_columnconfigure(0, weight=1)

header_init = Header(header)

theme_list_frame = CTkFrame(main_content)
theme_list_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

console_frame = CTkFrame(main_content)
console_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

console = Console(console_frame)
theme_list = ThemeList(theme_list_frame, console)

theme_maker = ThemeMaker()

def on_theme_maker_close():
    update_theme_maker_button_state()

def open_theme_maker():
    theme_maker.set_on_close_callback(on_theme_maker_close)
    theme_maker.open()
    update_theme_maker_button_state()

def update_theme_maker_button_state():
    if theme_maker.is_open():
        theme_maker_button.configure(state="disabled")
    else:
        theme_maker_button.configure(state="normal")

def check_theme_maker_status():
    if theme_maker.is_open():
        root.after(1000, check_theme_maker_status)
    else:
        update_theme_maker_button_state()

header_init.add_button("Revert", command=lambda: run_revert_command(console, root))
header_init.add_button("Open Themes Path", command=lambda: open_themes_path(console))
header_init.add_button("Refresh", command=lambda: theme_list.refresh_themes())
theme_maker_button = header_init.add_button("Theme Maker", command=open_theme_maker)
header_init.add_search(theme_list.filter_themes)

update_theme_maker_button_state()

console.system("Vineyard Theme Manager started successfully")

root.after(1000, check_theme_maker_status)

root.mainloop()