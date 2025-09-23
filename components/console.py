from customtkinter import *
import tkinter as tk
from datetime import datetime
import re

class Console(CTkFrame):
    def __init__(self, parent, height=200):
        super().__init__(parent)
        self.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.height = height
        self.max_lines = 1000
        self.current_lines = 0
        
        self.colors = {
            'info': '#FFFFFF',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'debug': '#17a2b8',
            'system': '#6f42c1',
            'default': '#cccccc'
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        header_frame = CTkFrame(self)
        header_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        CTkLabel(header_frame, text="Console", font=CTkFont(size=20, weight="bold")).pack(side="left", padx=10, pady=5)
        
        button_frame = CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=5, pady=5)
        
        CTkButton(button_frame, text="Clear", width=80, command=self.clear_console).pack(side="left", padx=5)
        CTkButton(button_frame, text="Copy", width=80, command=self.copy_to_clipboard).pack(side="left", padx=5)
        
        console_frame = CTkFrame(self)
        console_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.text_widget = tk.Text(
            console_frame,
            wrap=tk.WORD,
            bg='#1a1a1a',
            fg='#ffffff',
            insertbackground='white',
            selectbackground='#3d3d3d',
            font=('Consolas', 10),
            padx=10,
            pady=10,
            state=tk.DISABLED
        )

        scrollbar = CTkScrollbar(console_frame, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.setup_text_tags()
    
    def setup_text_tags(self):
        self.text_widget.config(state=tk.NORMAL)
        
        for msg_type, color in self.colors.items():
            self.text_widget.tag_configure(msg_type, foreground=color)
        
        self.text_widget.tag_configure('timestamp', foreground='#6c757d')
        
        self.text_widget.tag_configure('bold', font=('Consolas', 10, 'bold'))
        
        self.text_widget.config(state=tk.DISABLED)
    
    def write(self, message, msg_type='info'):
        self.text_widget.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_widget.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        self.text_widget.insert(tk.END, message, msg_type)
        self.text_widget.insert(tk.END, "\n")
        
        self.text_widget.see(tk.END)
        
        self.current_lines += 1
        if self.current_lines > self.max_lines:
            self.trim_lines()
        
        self.text_widget.config(state=tk.DISABLED)
    
    def trim_lines(self):
        lines_to_remove = self.current_lines - self.max_lines
        if lines_to_remove > 0:
            self.text_widget.delete(1.0, f"{lines_to_remove + 1}.0")
            self.current_lines = self.max_lines
    
    def clear_console(self):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.current_lines = 0
        self.text_widget.config(state=tk.DISABLED)
        self.write("Console cleared", 'system')
    
    def copy_to_clipboard(self):
        try:
            content = self.text_widget.get(1.0, tk.END)
            self.clipboard_clear()
            self.clipboard_append(content.strip())
            self.write("Console content copied to clipboard", 'success')
        except Exception as e:
            self.write(f"Failed to copy to clipboard: {str(e)}", 'error')
    
    def info(self, message):
        self.write(message, 'info')
    
    def success(self, message):
        self.write(message, 'success')
    
    def warning(self, message):
        self.write(message, 'warning')
    
    def error(self, message):
        self.write(message, 'error')
    
    def debug(self, message):
        self.write(message, 'debug')
    
    def system(self, message):
        self.write(message, 'system')
    
    def print_exception(self, exception):
        import traceback
        tb_str = traceback.format_exc()
        self.error(f"Exception occurred:\n{tb_str}")