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
    
    def refresh(self):
        self.highlight()
    
    def validate_syntax(self):
        text = self.text_widget.get('1.0', tk.END)
        lines = text.split('\n')
        errors = []
        warnings = []

        self.text_widget.tag_remove('error', '1.0', tk.END)
        self.text_widget.tag_remove('warning', '1.0', tk.END)

        has_version = False
        has_header = False
        has_entries = False

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            if line.startswith('Windows Registry Editor Version'):
                has_version = True
                if not re.match(r'^Windows Registry Editor Version \d+\.\d+$', line):
                    errors.append(f"Line {line_num}: Invalid version format")
                    self.mark_error(line_num, 0, len(line))
            elif line.startswith('[') and line.endswith(']'):
                has_header = True
                if not re.match(r'^\[[^\]]+\]$', line):
                    errors.append(f"Line {line_num}: Invalid registry header format")
                    self.mark_error(line_num, 0, len(line))
            elif '=' in line and not line.startswith(';'):
                has_entries = True
                if not self.validate_key_value(line, line_num):
                    errors.append(f"Line {line_num}: Invalid key-value format")
            elif not line.startswith(';'):
                errors.append(f"Line {line_num}: Invalid syntax")
                self.mark_error(line_num, 0, len(line))

        if not has_version:
            warnings.append("Missing 'Windows Registry Editor Version' header")

        if not has_header:
            warnings.append("Missing registry header (e.g., [HKEY_CURRENT_USER\\Control Panel\\Colors])")

        if not has_entries:
            warnings.append("No color entries found")

        return len(errors) == 0, errors, warnings

    def validate_key_value(self, line, line_num):
        try:
            key_part, value_part = line.split('=', 1)
            key = key_part.strip()
            value = value_part.strip()

            if not (key.startswith('"') and key.endswith('"')):
                self.mark_error(line_num, 0, len(key_part))
                return False

            if not (value.startswith('"') and value.endswith('"')):
                self.mark_error(line_num, len(key_part) + 1, len(line))
                return False

            inner_value = value.strip('"')

            if re.match(r'^\d{1,3}\s+\d{1,3}\s+\d{1,3}$', inner_value):
                rgb_values = inner_value.split()
                for val in rgb_values:
                    if not (0 <= int(val) <= 255):
                        self.mark_warning(line_num, line.find(inner_value), line.find(inner_value) + len(inner_value))
                        return True
                    
            return True
        except Exception:
            self.mark_error(line_num, 0, len(line))
            return False
    
    def mark_error(self, line_num, start_pos, end_pos):
        self.text_widget.tag_add('error', 
                               f"{line_num}.{start_pos}", 
                               f"{line_num}.{end_pos}")

    def mark_warning(self, line_num, start_pos, end_pos):
        self.text_widget.tag_add('warning', 
                               f"{line_num}.{start_pos}", 
                               f"{line_num}.{end_pos}")

class RegTextWidget(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.highlighter = None
        self.create_widgets()
    
    def create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.text_widget = tk.Text(
            self,
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            undo=True,
            maxundo=-1,
            wrap=tk.WORD
        )

        self.text_widget.grid(row=0, column=0, sticky="nsew")

        v_scrollbar.config(command=self.text_widget.yview)
        h_scrollbar.config(command=self.text_widget.xview)

        self.highlighter = RegSyntaxHighlighter(self.text_widget)
    
    def insert(self, index, text, tags=None):
        if tags:
            self.text_widget.insert(index, text, tags)
        else:
            self.text_widget.insert(index, text)

        self.highlighter.highlight()
    
    def delete(self, start, end=None):
        self.text_widget.delete(start, end)
        self.highlighter.highlight()
    
    def get(self, start, end=None):
        return self.text_widget.get(start, end)

    def clear(self):
        self.text_widget.delete('1.0', tk.END)
    
    def configure_text(self, **kwargs):
        self.text_widget.configure(**kwargs)