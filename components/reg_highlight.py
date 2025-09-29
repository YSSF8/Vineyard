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
    
    def highlight_brackets(self, line, line_num):
        open_bracket = line.find('[')
        close_bracket = line.find(']')

        if open_bracket != -1:
            self.text_widget.tag_add('brackets', f"{line_num}.{open_bracket}", f"{line_num}.{open_bracket + 1}")

        if close_bracket != -1:
            self.text_widget.tag_add('brackets', f"{line_num}.{close_bracket}", f"{line_num}.{close_bracket + 1}")
    
    def highlight_key_value(self, line, line_num):
        if '=' not in line:
            return

        key_part, value_part = line.split('=', 1)
        key_start = line.find('"')
        key_end = line.find('"', key_start + 1) + 1 if key_start != -1 else -1

        if key_start != -1 and key_end != -1:
            self.text_widget.tag_add('string_key', f"{line_num}.{key_start}", f"{line_num}.{key_end}")

        operator_pos = line.find('=')

        if operator_pos != -1:
            self.text_widget.tag_add('operator', f"{line_num}.{operator_pos}", f"{line_num}.{operator_pos + 1}")

        value_start = operator_pos + 1

        if value_start < len(line):
            value_text = line[value_start:]

            if value_text.strip().startswith('"') and value_text.strip().endswith('"'):
                value_start_abs = value_start + value_text.find('"')
                value_end_abs = value_start + value_text.rfind('"') + 1
                self.text_widget.tag_add('string_value', f"{line_num}.{value_start_abs}", f"{line_num}.{value_end_abs}")
                inner_value = value_text.strip('" ')
                self.highlight_value_content(inner_value, line_num, value_start_abs + 1)
    
    def highlight_value_content(self, value, line_num, start_offset):
        rgb_pattern = r'\b\d{1,3}\s+\d{1,3}\s+\d{1,3}\b'
        for match in re.finditer(rgb_pattern, value):
            rgb_start = start_offset + match.start()
            rgb_end = start_offset + match.end()
            self.text_widget.tag_add('rgb_values', f"{line_num}.{rgb_start}", f"{line_num}.{rgb_end}")

        hex_pattern = r'#[0-9a-fA-F]{6}'
        for match in re.finditer(hex_pattern, value):
            hex_start = start_offset + match.start()
            hex_end = start_offset + match.end()
            self.text_widget.tag_add('hex_value', f"{line_num}.{hex_start}", f"{line_num}.{hex_end}")

    def clear_highlighting(self):
        for tag in self.text_widget.tag_names():
            if tag != 'sel':
                self.text_widget.tag_remove(tag, '1.0', tk.END)