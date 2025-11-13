import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont

class ColorSlidersFrame(ttk.Frame):
    def __init__(self, master, model, title, components, max_values, model_update_func):
        super().__init__(master, padding=10)
        self.model = model
        self.model_update_func = model_update_func
        self._is_internal_update = False

        frame = ttk.LabelFrame(self, text=title, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.vars = []
        self.scales = []
        self.entries = []

        for i, (label, max_val) in enumerate(zip(components, max_values)):
            var = tk.IntVar(value=0)
            self.vars.append(var)

            ttk.Label(frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=5)

            scale = ttk.Scale(frame, from_=0, to=max_val, orient=tk.HORIZONTAL, variable=var,
                              command=lambda e, v=var: self._on_change())
            scale.grid(row=i, column=1, sticky='ew', padx=5)
            self.scales.append(scale)
            
            entry = ttk.Entry(frame, textvariable=var, width=5, font="appDefaultFont")
            entry.grid(row=i, column=2, padx=5)
            entry.bind('<Return>', lambda e: self._on_change())
            entry.bind('<FocusOut>', lambda e: self._on_change())
            self.entries.append(entry)

        frame.columnconfigure(1, weight=1)

    def _on_change(self):
        if self._is_internal_update:
            return
        
        values = [v.get() for v in self.vars]
        self.model_update_func(*values, source=self)

    def update_from_model(self):
        self._is_internal_update = True
        
        if self.model_update_func == self.model.update_from_rgb:
            values = self.model.get_rgb()
        elif self.model_update_func == self.model.update_from_cmyk:
            values = self.model.get_cmyk()
        elif self.model_update_func == self.model.update_from_hsv:
            values = self.model.get_hsv()
            values = (values[0] % 360.0, values[1], values[2])
        else:
            values = []

        for var, val in zip(self.vars, values):
            var.set(val)

        self._is_internal_update = False