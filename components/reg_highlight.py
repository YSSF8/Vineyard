import tkinter as tk
from tkinter import ttk
import re

class RegSyntaxHighlighter:
    COLORS = {
        'background': '#1e1e1e',
        'foreground': '#d4d4d4',
        'caret': '#ffffff',
        'selection': '#264f78',
        'line_highlight': '#2d2d30',
        'gutter_bg': '#1e1e1e',
        'gutter_fg': '#858585',
        'keywords': '#569cd6',
        'strings': '#ce9178',
        'numbers': '#b5cea8',
        'comments': '#6a9955',
        'operators': '#d4d4d4',
        'brackets': '#ffd700',
        'hex_values': '#c586c0',
        'error': '#f44747',
        'warning': '#ff8800',
    }

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.setup_theme()
        self.bind_events()
    
    def setup_theme(self):
        self.text_widget.configure(
            bg=self.COLORS['background'],
            fg=self.COLORS['foreground'],
            insertbackground=self.COLORS['caret'],
            selectbackground=self.COLORS['selection'],
            selectforeground=self.COLORS['foreground'],
            inactiveselectbackground=self.COLORS['selection'],
            font=('Consolas', 10),
            relief='flat',
            padx=10,
            pady=10,
            wrap=tk.WORD
        )

        self.configure_tags()