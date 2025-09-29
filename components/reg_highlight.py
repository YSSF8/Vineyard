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
    
    def configure_tags(self):
        tags_config = {
            'version': {'foreground': self.COLORS['keywords'], 'font': ('Consolas', 10, 'bold')},
            'header': {'foreground': self.COLORS['keywords'], 'font': ('Consolas', 10, 'bold')},
            'comment': {'foreground': self.COLORS['comments'], 'font': ('Consolas', 10, 'italic')},
            'string_key': {'foreground': self.COLORS['strings']},
            'string_value': {'foreground': self.COLORS['strings']},
            'rgb_values': {'foreground': self.COLORS['numbers']},
            'hex_value': {'foreground': self.COLORS['hex_values']},
            'operator': {'foreground': self.COLORS['operators']},
            'brackets': {'foreground': self.COLORS['brackets']},
            'line_highlight': {'background': self.COLORS['line_highlight']},
            'error': {'foreground': self.COLORS['error'], 'underline': True, 'underlinefg': self.COLORS['error']},
            'warning': {'foreground': self.COLORS['warning'], 'underline': True, 'underlinefg': self.COLORS['warning']},
        }

        for tag_name, config in tags_config.items():
            self.text_widget.tag_configure(tag_name, **config)
    
    def bind_events(self):
        self.text_widget.bind('<KeyRelease>', lambda e: self.highlight())
        self.text_widget.bind('<ButtonRelease>', lambda e: self.highlight())
        self.text_widget.bind('<<Modified>>', self.on_modified)
    
    def on_modified(self, event=None):
        if self.text_widget.edit_modified():
            self.highlight()
            self.text_widget.edit_modified(False)
    
    def highlight(self):
        for tag in self.text_widget.tag_names():
            if tag not in ['sel', 'error', 'warning']:
                self.text_widget.tag_remove(tag, '1.0', tk.END)
            else:
                self.text_widget.tag_remove(tag, '1.0', tk.END)

        text = self.text_widget.get('1.0', tk.END)
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            self.highlight_line(line, line_num)
    
    def highlight_line(self, line, line_num):
        if not line.strip():
            return

        line_start = f"{line_num}.0"
        line_end = f"{line_num}.{len(line)}"

        if line.startswith('Windows Registry Editor Version'):
            self.text_widget.tag_add('version', line_start, line_end)

        elif line.strip().startswith(';'):
            self.text_widget.tag_add('comment', line_start, line_end)

        elif line.startswith('[') and line.endswith(']'):
            self.text_widget.tag_add('header', line_start, line_end)
            self.highlight_brackets(line, line_num)

        elif '=' in line:
            self.highlight_key_value(line, line_num)