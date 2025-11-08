from customtkinter import CTkLabel, CTkToplevel, CTkFrame, CTkButton

class ContextMenu:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.items = []
        self._create_window()
    
    def _create_window(self):
        self.window = CTkToplevel(self.parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(corner_radius=8)
        
        self.frame = CTkFrame(
            self.window,
            corner_radius=8,
            border_width=1,
            fg_color=("gray90", "gray20")
        )
        self.frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.window.bind("<FocusOut>", lambda e: self.hide())
        self.window.bind("<Escape>", lambda e: self.hide())
        
        self.window.withdraw()
    
    def add_command(self, label, command, accelerator="", icon="", enabled=True):
        item_frame = CTkFrame(self.frame, fg_color="transparent", height=32)
        item_frame.pack(fill="x", padx=4, pady=(1, 0))
        
        item_data = {
            'frame': item_frame,
            'command': command,
            'enabled': enabled,
            'widgets': []
        }
        
        if icon:
            icon_label = CTkLabel(item_frame, text=icon, width=20, font=("Segoe UI", 14))
            icon_label.pack(side="left", padx=(10, 5))
            item_data['icon'] = icon_label
            item_data['widgets'].append(icon_label)
        
        label_widget = CTkLabel(
            item_frame,
            text=label,
            anchor="w",
            font=("Segoe UI", 12),
            width=120
        )
        label_widget.pack(side="left", fill="x", expand=True)
        item_data['label'] = label_widget
        item_data['widgets'].append(label_widget)
        
        if accelerator:
            accel_label = CTkLabel(
                item_frame,
                text=accelerator,
                anchor="e",
                text_color="gray",
                font=("Segoe UI", 10)
            )
            accel_label.pack(side="right", padx=(10, 15))
            item_data['accelerator'] = accel_label
            item_data['widgets'].append(accel_label)
        
        item_data['widgets'].append(item_frame)
        
        self._update_item_appearance(item_data)
        
        def on_enter(e):
            if item_data['enabled']:
                item_frame.configure(fg_color=("gray80", "gray30"))
        
        def on_leave(e):
            item_frame.configure(fg_color="transparent")
        
        for widget in item_data['widgets']:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        self.items.append(item_data)
    
    def add_separator(self):
        separator = CTkFrame(self.frame, height=1, fg_color=("gray70", "gray40"))
        separator.pack(fill="x", padx=10, pady=(4, 0))
    
    def show(self, x, y):
        self.window.update_idletasks()
        width = 180
        height = self.window.winfo_reqheight()
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.deiconify()
        self.window.focus_set()
    
    def hide(self):
        if self.window and self.window.winfo_exists():
            self.window.withdraw()
    
    def enable_item(self, index, enabled):
        if 0 <= index < len(self.items):
            item = self.items[index]
            item['enabled'] = enabled
            self._update_item_appearance(item)
    
    def _update_item_appearance(self, item):
        enabled = item['enabled']
        
        text_color = ("gray10", "#DCE4EE") if enabled else "gray50"
        item['label'].configure(text_color=text_color)
        
        if 'icon' in item:
            item['icon'].configure(text_color=text_color)
        
        if 'accelerator' in item:
            accel_color = "gray" if enabled else "gray40"
            item['accelerator'].configure(text_color=accel_color)
        
        cursor = "hand2" if enabled else "arrow"
        for widget in item['widgets']:
            widget.configure(cursor=cursor)
            widget.unbind("<Button-1>")
            if enabled:
                widget.bind("<Button-1>", lambda e: self._execute(item['command']))
    
    def _execute(self, command):
        self.hide()
        command()