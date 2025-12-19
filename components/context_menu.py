from customtkinter import CTkLabel, CTkToplevel, CTkFrame

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
        self.window.withdraw()
        
        self.frame = CTkFrame(
            self.window,
            corner_radius=6,
            border_width=1,
            fg_color=("gray95", "gray20"),
            border_color=("gray80", "gray10")
        )
        self.frame.pack(fill="both", expand=True)
        
        self.window.bind("<FocusOut>", lambda e: self.hide())
        self.window.bind("<Escape>", lambda e: self.hide())
        
        self.parent.bind("<Button-1>", lambda e: self.hide(), add="+")
    
    def add_command(self, label, command, accelerator="", icon="", enabled=True):
        item_frame = CTkFrame(self.frame, fg_color="transparent", height=28)
        item_frame.pack(fill="x", padx=2, pady=1)
        
        item_data = {
            'frame': item_frame,
            'command': command,
            'enabled': enabled,
            'widgets': []
        }
        
        if icon:
            icon_label = CTkLabel(item_frame, text=icon, width=24, font=("Segoe UI", 14))
            icon_label.pack(side="left", padx=(8, 2))
            item_data['icon'] = icon_label
            item_data['widgets'].append(icon_label)
        else:
            spacer = CTkFrame(item_frame, width=24, height=1, fg_color="transparent")
            spacer.pack(side="left", padx=(8, 2))
            item_data['widgets'].append(spacer)

        if accelerator:
            accel_label = CTkLabel(
                item_frame,
                text=accelerator,
                anchor="e",
                font=("Segoe UI", 10),
                width=65
            )
            accel_label.pack(side="right", padx=(5, 10))
            item_data['accelerator'] = accel_label
            item_data['widgets'].append(accel_label)
        
        label_widget = CTkLabel(
            item_frame,
            text=label,
            anchor="w",
            font=("Segoe UI", 12)
        )
        label_widget.pack(side="left", fill="x", expand=True, padx=(5, 5))
        item_data['label'] = label_widget
        item_data['widgets'].append(label_widget)
        
        item_data['widgets'].append(item_frame)
        self._update_item_appearance(item_data)
        
        def on_enter(e):
            if item_data['enabled']:
                item_frame.configure(fg_color=("gray85", "#3A3A3A"))
        
        def on_leave(e):
            item_frame.configure(fg_color="transparent")
        
        for widget in item_data['widgets']:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            if enabled:
                widget.bind("<ButtonRelease-1>", lambda e: self._execute(item_data['command']))
        
        self.items.append(item_data)
    
    def add_separator(self):
        separator = CTkFrame(self.frame, height=2, fg_color=("gray80", "gray30"))
        separator.pack(fill="x", padx=5, pady=4)
    
    def show(self, x, y):
        self.window.deiconify()
        self.window.update_idletasks()
        
        req_width = self.frame.winfo_reqwidth()
        width = max(req_width + 20, 220)
        height = self.frame.winfo_reqheight()
        
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        
        if x + width > screen_w: x -= width
        if y + height > screen_h: y -= height
            
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.focus_set()
    
    def hide(self):
        if self.window and self.window.winfo_exists():
            self.window.withdraw()
    
    def enable_item(self, index, enabled):
        if 0 <= index < len(self.items):
            item = self.items[index]
            item['enabled'] = enabled
            self._update_item_appearance(item)
            
            for widget in item['widgets']:
                widget.unbind("<ButtonRelease-1>")
                if enabled:
                    widget.bind("<ButtonRelease-1>", lambda e, cmd=item['command']: self._execute(cmd))
    
    def _update_item_appearance(self, item):
        enabled = item['enabled']
        text_color = ("gray10", "gray90") if enabled else "gray60"
        accel_color = ("gray40", "gray50") if enabled else "gray60"
        
        item['label'].configure(text_color=text_color)
        if 'icon' in item:
            item['icon'].configure(text_color=text_color)
        if 'accelerator' in item:
            item['accelerator'].configure(text_color=accel_color)
        
        cursor = "hand2" if enabled else "arrow"
        for widget in item['widgets']:
            widget.configure(cursor=cursor)

    def _execute(self, command):
        self.hide()
        command()