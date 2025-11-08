from customtkinter import CTkToplevel, CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkScrollableFrame, CTkTabview
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import json
import os
from datetime import datetime

class ThemeMaker:
    _instance = None
    _window = None
    _initialized = False
    _on_close_callback = None
    _color_entries = {}
    _original_colors = {}
    _reg_text_widget = None
    _is_edit_mode = False
    _current_edit_file = None
    _save_button = None
    _save_as_button = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeMaker, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
    
    def _create_color_row(self, parent, key, value, row):
        color_frame = CTkFrame(parent)
        color_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        color_frame.grid_columnconfigure(1, weight=1)

        label = CTkLabel(color_frame, text=key, width=200, anchor="w")
        label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")

        color_entry = CTkEntry(color_frame)
        color_entry.insert(0, value)
        color_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self._color_entries[key] = color_entry

        color_preview = CTkLabel(color_frame, text="", width=30, height=20, 
                               fg_color=value, corner_radius=3)
        color_preview.grid(row=0, column=2, padx=5, pady=5)
        self._preview_labels[key] = color_preview

        picker_btn = CTkButton(color_frame, text="Pick Color", width=80, height=20,
                             command=lambda k=key, e=color_entry, p=color_preview: self.choose_color(k, e, p))
        picker_btn.grid(row=0, column=3, padx=(5, 10), pady=5)
    
    def _create_context_menu(self):
        """Create the context menu for the Advanced tab text editor"""
        self._context_menu = tk.Menu(self._window, tearoff=0)
        self._context_menu.add_command(label="Cut", command=self._cut_text, accelerator="Ctrl+X")
        self._context_menu.add_command(label="Copy", command=self._copy_text, accelerator="Ctrl+C")
        self._context_menu.add_command(label="Paste", command=self._paste_text, accelerator="Ctrl+V")
        self._context_menu.add_command(label="Delete", command=self._delete_text, accelerator="Del")
        self._context_menu.add_separator()
        self._context_menu.add_command(label="Format code", command=self._format_code, accelerator="Ctrl+Shift+F")
        self._context_menu.add_command(label="Reset", command=self._reset_advanced_tab, accelerator="Ctrl+Shift+R")

        self._reg_text_widget.text_widget.bind("<Button-3>", self._show_context_menu)
        self._reg_text_widget.text_widget.bind("<Button-2>", self._show_context_menu)

        self._reg_text_widget.text_widget.bind('<Control-Shift-f>', lambda e: self._format_code())
        self._reg_text_widget.text_widget.bind('<Control-Shift-F>', lambda e: self._format_code())
        self._reg_text_widget.text_widget.bind('<Control-Shift-r>', lambda e: self._reset_advanced_tab())
        self._reg_text_widget.text_widget.bind('<Control-Shift-R>', lambda e: self._reset_advanced_tab())
    
    def _show_context_menu(self, event):
        try:
            sel_start = self._reg_text_widget.text_widget.index("sel.first")
            sel_end = self._reg_text_widget.text_widget.index("sel.last")
            has_selection = True
        except tk.TclError:
            has_selection = False

        self._context_menu.entryconfig("Cut", state="normal" if has_selection else "disabled")
        self._context_menu.entryconfig("Copy", state="normal" if has_selection else "disabled")
        self._context_menu.entryconfig("Delete", state="normal" if has_selection else "disabled")

        self._context_menu.tk_popup(event.x_root, event.y_root)
    
    def _cut_text(self):
        self._reg_text_widget.text_widget.event_generate("<<Cut>>")

    def _copy_text(self):
        self._reg_text_widget.text_widget.event_generate("<<Copy>>")

    def _paste_text(self):
        self._reg_text_widget.text_widget.event_generate("<<Paste>>")

    def _delete_text(self):
        try:
            self._reg_text_widget.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

    def _format_code(self):
        if not self._reg_text_widget or not hasattr(self, '_initial_reg_content'):
            return

        current_content = self._reg_text_widget.get('1.0', tk.END)
        current_dict = self._parse_reg_values(current_content)

        reset_dict = self._parse_reg_values(self._initial_reg_content)

        formatted_lines = ["Windows Registry Editor Version 5.00", ""]
        formatted_lines.append("[HKEY_CURRENT_USER\\Control Panel\\Colors]")

        all_keys = sorted(current_dict.keys())
        for key in all_keys:
            value = current_dict[key]
            formatted_lines.append(f'"{key}"="{value}"')

        formatted_content = '\n'.join(formatted_lines)
        self._reg_text_widget.delete('1.0', tk.END)
        self._reg_text_widget.insert('1.0', formatted_content)

        self._reg_text_widget.highlighter.highlight()
        self._reg_text_widget.line_numbers.update_line_numbers()

    def _reset_advanced_tab(self):
        if not hasattr(self, '_initial_reg_content') or not self._initial_reg_content:
            return

        if messagebox.askyesno("Reset", 
                              "Reset Advanced tab to initial state?\n\nThis will discard all changes made in the Advanced tab."):
            self._reg_text_widget.delete('1.0', tk.END)
            self._reg_text_widget.insert('1.0', self._initial_reg_content)
            self._reg_text_widget.highlighter.highlight()

    def _parse_reg_values(self, content):
        values = {}
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if line and '=' in line and not line.startswith(';') and not line.startswith('['):
                try:
                    key_part, value_part = line.split('=', 1)
                    key = key_part.strip().strip('"')
                    value = value_part.strip().strip('"')
                    if key:
                        values[key] = value
                except:
                    continue
                
        return values

    def set_on_close_callback(self, callback):
        self._on_close_callback = callback

    def open(self):
        if self._window is None or not self._window.winfo_exists():
            self._is_edit_mode = False
            self._current_edit_file = None
            self.create_window()
        else:
            self._window.lift()
            self._window.focus_force()
    
    def open_in_edit_mode(self, file_path, theme_name):
        display_name = os.path.splitext(theme_name)[0]

        if self._window is None or not self._window.winfo_exists():
            self._is_edit_mode = True
            self._current_edit_file = file_path
            self.create_window()
            self.load_theme_from_file(file_path)
            self._window.title(f"Vineyard - Theme Maker - Editing: {display_name}")
        else:
            self._is_edit_mode = True
            self._current_edit_file = file_path
            self.load_theme_from_file(file_path)
            self._window.title(f"Vineyard - Theme Maker - Editing: {display_name}")
            self.update_save_buttons()

        self._window.lift()
        self._window.focus_force()

    def create_window(self):
        self._window = CTkToplevel()
        
        if self._is_edit_mode:
            theme_name = os.path.splitext(os.path.basename(self._current_edit_file))[0]
            self._window.title(f"Vineyard - Theme Maker - Editing: {theme_name}")
        else:
            self._window.title("Vineyard - Theme Maker")
            
        self._window.geometry("800x600")
        self._window.resizable(True, True)
        self._window.minsize(700, 500)
        
        self.center_window()

        main_container = CTkFrame(self._window)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=0)
        main_container.grid_columnconfigure(0, weight=1)

        tabview = CTkTabview(main_container)
        tabview.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        basic_tab = tabview.add("Basic")
        advanced_tab = tabview.add("Advanced")
        
        basic_tab.grid_columnconfigure(0, weight=1)
        basic_tab.grid_rowconfigure(0, weight=1)
        advanced_tab.grid_columnconfigure(0, weight=1)
        advanced_tab.grid_rowconfigure(0, weight=1)
        
        self.create_basic_tab(basic_tab)
        self.create_advanced_tab(advanced_tab)

        button_frame = CTkFrame(main_container)
        button_frame.grid(row=1, column=0, sticky="ew", pady=0)

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=0)
        button_frame.grid_columnconfigure(2, weight=0)
        button_frame.grid_columnconfigure(3, weight=0)

        cancel_btn = CTkButton(button_frame, text="Cancel", command=self.on_close, 
                              fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        cancel_btn.grid(row=0, column=1, padx=(5, 5), pady=10)

        self._save_as_button = CTkButton(button_frame, text="Save As", 
                                       command=self.save_theme_as)
        self._save_as_button.grid(row=0, column=2, padx=(5, 5), pady=10)

        save_text = "Save" if self._is_edit_mode else "Save Theme"
        self._save_button = CTkButton(button_frame, text=save_text, command=self.save_theme)
        self._save_button.grid(row=0, column=3, padx=(0, 0), pady=10)

        self.update_save_buttons()

        self._window.protocol("WM_DELETE_WINDOW", self.on_close)
        self._window.bind("<Destroy>", self._on_destroy)
        self._window.focus_force()

    def create_basic_tab(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        scrollable_frame = CTkScrollableFrame(parent)
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        scrollable_frame.grid_columnconfigure(0, weight=1)

        try:
            with open('keys.json', 'r', encoding='utf-8') as f:
                keys = json.load(f)
        except FileNotFoundError:
            keys = {}

        self._preview_labels = {}
        self._color_entries = {}

        keys_items = list(keys.items())
        batch_size = 20

        def process_batch(start_index):
            end_index = min(start_index + batch_size, len(keys_items))

            for i in range(start_index, end_index):
                key, value = keys_items[i]
                if value is None:
                    value = "#000000"

                self._original_colors[key] = value
                self._create_color_row(scrollable_frame, key, value, i)

            if end_index < len(keys_items):
                self._window.after(10, process_batch, end_index)
            else:
                self.update_reg_code_from_basic()

        process_batch(0)

    def create_advanced_tab(self, parent):
        from components.reg_highlight import RegTextWidget

        advanced_container = CTkFrame(parent)
        advanced_container.pack(fill="both", expand=True, padx=0, pady=0)
        advanced_container.grid_rowconfigure(0, weight=1)
        advanced_container.grid_rowconfigure(1, weight=0)
        advanced_container.grid_columnconfigure(0, weight=1)

        self._reg_text_widget = RegTextWidget(advanced_container)
        self._reg_text_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        button_frame = CTkFrame(advanced_container)
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=0)
        button_frame.grid_columnconfigure(2, weight=0)

        update_btn = CTkButton(button_frame, text="Update from Basic Tab", 
                              command=self.update_reg_code_from_basic)
        update_btn.grid(row=0, column=1, padx=(5, 5), pady=5)

        apply_btn = CTkButton(button_frame, text="Apply to Basic Tab", 
                             command=self.update_basic_from_reg_code)
        apply_btn.grid(row=0, column=2, padx=(0, 0), pady=5)

        self.update_reg_code_from_basic()
        self._initial_reg_content = self._reg_text_widget.get('1.0', tk.END)

        self._create_context_menu()

    def update_reg_code_from_basic(self):
        if self._reg_text_widget:
            reg_content = self.generate_registry_file()
            self._reg_text_widget.delete('1.0', tk.END)
            self._reg_text_widget.insert('1.0', reg_content)

    def update_basic_from_reg_code(self):
        if not self._reg_text_widget:
            return

        is_valid, errors, warnings = self._reg_text_widget.validate_content()

        if not is_valid:
            error_msg = "Cannot apply due to syntax errors:\n\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n\n... and {len(errors) - 5} more errors"
            if warnings:
                error_msg += "\n\nWarnings:\n" + "\n".join(warnings[:3])
            messagebox.showerror("Syntax Errors", error_msg)
            return

        if warnings:
            warning_msg = "Warnings found:\n\n" + "\n".join(warnings)
            if not messagebox.askyesno("Warnings", warning_msg + "\n\nContinue anyway?"):
                return

        try:
            reg_content = self._reg_text_widget.get('1.0', tk.END)
            lines = reg_content.split('\n')

            updated_count = 0
            for line in lines:
                line = line.strip()
                if line and not line.startswith(';') and not line.startswith('[') and not line.startswith('Windows'):
                    if '=' in line:
                        key_part, value_part = line.split('=', 1)
                        key = key_part.strip().strip('"')
                        value = value_part.strip().strip('"')

                        if key in self._color_entries and ' ' in value:
                            rgb_values = value.split()
                            if len(rgb_values) == 3:
                                try:
                                    r, g, b = map(int, rgb_values)
                                    if not all(0 <= val <= 255 for val in [r, g, b]):
                                        continue

                                    hex_color = f"#{r:02x}{g:02x}{b:02x}".upper()
                                    self._color_entries[key].delete(0, tk.END)
                                    self._color_entries[key].insert(0, hex_color)

                                    if hasattr(self, '_preview_labels') and key in self._preview_labels:
                                        self._preview_labels[key].configure(fg_color=hex_color)

                                    updated_count += 1
                                except ValueError:
                                    continue
                                
            self.update_reg_code_from_basic()

            return True

        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse registry code:\n{str(e)}")
            return False

    def choose_color(self, key, entry, preview):
        current_color = entry.get()

        theme_window = self._window

        color_code = colorchooser.askcolor(
            initialcolor=current_color,
            title=f"Choose color for {key}"
        )

        if color_code[1] is not None:
            new_color = color_code[1]
            entry.delete(0, tk.END)
            entry.insert(0, new_color)
            preview.configure(fg_color=new_color)
            if hasattr(self, '_preview_labels') and key in self._preview_labels:
                self._preview_labels[key].configure(fg_color=new_color)

            if theme_window and theme_window.winfo_exists():
                theme_window.lift()
                theme_window.focus_force()
                entry.focus_set()

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        else:
            r, g, b = 0, 0, 0
        return f"{r} {g} {b}"

    def rgb_to_hex(self, rgb_string):
        try:
            r, g, b = map(int, rgb_string.split())
            return f"#{r:02x}{g:02x}{b:02x}".upper()
        except:
            return "#000000"
    
    def update_save_buttons(self):
        if self._save_button and self._save_as_button:
            if self._is_edit_mode:
                self._save_button.configure(text="Save")
                self._save_as_button.grid()
            else:
                self._save_button.configure(text="Save Theme")
                self._save_as_button.grid_remove()

    def load_theme_from_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reg_content = f.read()

            lines = reg_content.split('\n')
            color_values = {}

            for line in lines:
                line = line.strip()
                if line and not line.startswith(';') and not line.startswith('[') and not line.startswith('Windows'):
                    if '=' in line:
                        key_part, value_part = line.split('=', 1)
                        key = key_part.strip().strip('"')
                        value = value_part.strip().strip('"')

                        if ' ' in value:
                            rgb_values = value.split()
                            if len(rgb_values) == 3:
                                try:
                                    r, g, b = map(int, rgb_values)
                                    hex_color = f"#{r:02x}{g:02x}{b:02x}".upper()
                                    color_values[key] = hex_color
                                except ValueError:
                                    continue

            for key, hex_color in color_values.items():
                if key in self._color_entries:
                    self._color_entries[key].delete(0, tk.END)
                    self._color_entries[key].insert(0, hex_color)

                    if hasattr(self, '_preview_labels') and key in self._preview_labels:
                        self._preview_labels[key].configure(fg_color=hex_color)

            self.update_reg_code_from_basic()

            self._initial_reg_content = self._reg_text_widget.get('1.0', tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load theme: {str(e)}")

    def save_theme_as(self):
        was_edit_mode = self._is_edit_mode
        current_file = self._current_edit_file

        self._is_edit_mode = False
        self._current_edit_file = None

        try:
            self.save_theme()

            if not self._is_edit_mode and was_edit_mode:
                self._is_edit_mode = True
        except Exception:
            self._is_edit_mode = was_edit_mode
            self._current_edit_file = current_file
            raise

    def save_theme(self):
        try:
            if hasattr(self, '_reg_text_widget') and self._reg_text_widget:
                is_valid, errors, warnings = self._reg_text_widget.validate_content()

                if not is_valid:
                    error_msg = "Cannot save due to syntax errors:\n\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        error_msg += f"\n\n... and {len(errors) - 5} more errors"
                    messagebox.showerror("Syntax Errors", error_msg)
                    return

                if warnings:
                    warning_msg = "Warnings found:\n\n" + "\n".join(warnings)
                    if not messagebox.askyesno("Warnings", warning_msg + "\n\nSave anyway?"):
                        return

                self.update_basic_from_reg_code()

            self.update_reg_code_from_basic()

            themes_dir = "./themes"
            if not os.path.exists(themes_dir):
                os.makedirs(themes_dir)

            if self._is_edit_mode and self._current_edit_file:
                filename = self._current_edit_file
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_filename = f"custom_theme_{timestamp}.reg"

                filename = filedialog.asksaveasfilename(
                    initialdir=themes_dir,
                    defaultextension=".reg",
                    filetypes=[("Registry files", "*.reg"), ("All files", "*.*")],
                    initialfile=default_filename,
                    title="Save Theme As"
                )

                if not filename:
                    return

            reg_content = self._reg_text_widget.get('1.0', tk.END) if self._reg_text_widget else self.generate_registry_file()

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(reg_content)

            self._original_colors = {key: entry.get() for key, entry in self._color_entries.items()}

            theme_name = os.path.basename(filename)

            if self._is_edit_mode:
                messagebox.showinfo("Success", f"Theme saved successfully:\n{theme_name}")
            else:
                messagebox.showinfo("Success", f"Theme saved successfully as:\n{theme_name}.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save theme:\n{str(e)}")

    def generate_registry_file(self):
        lines = []
        lines.append("Windows Registry Editor Version 5.00")
        lines.append("")
        lines.append("[HKEY_CURRENT_USER\\Control Panel\\Colors]")
        
        for key, entry in self._color_entries.items():
            hex_color = entry.get()
            rgb_color = self.hex_to_rgb(hex_color)
            lines.append(f'"{key}"="{rgb_color}"')
        
        return '\n'.join(lines)

    def center_window(self):
        self._window.update_idletasks()
        width = self._window.winfo_width()
        height = self._window.winfo_height()
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