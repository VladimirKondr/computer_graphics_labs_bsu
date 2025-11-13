import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from ui.color_sliders_frame import ColorSlidersFrame
from ui.palette_frame import PaletteFrame

class App(tk.Tk):
    def __init__(self, model):
        super().__init__()
        self.model = model

        self.title("Color Picker (Вариант 4: CMYK-RGB-HSV)")
        self.minsize(width=800, height=450)
        
        tkFont.Font(name="appDefaultFont", family="Helvetica", size=12)
        tkFont.Font(name="appHeaderFont", family="Helvetica", size=12, weight="bold")

        self.option_add('*TSpinbox*font', "appDefaultFont")

        self.style = ttk.Style(self)
        self.style.configure('TLabel', font="appDefaultFont")
        self.style.configure('TEntry', font="appDefaultFont")
        self.style.configure('TLabelframe.Label', font="appHeaderFont")

        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)
        
        palette = PaletteFrame(left_frame, self.model)
        palette.pack(fill=tk.BOTH, expand=True)
        self.model.add_observer(palette)

        rgb_frame = ColorSlidersFrame(right_frame, self.model, "RGB",
                                      ('R', 'G', 'B'), (255, 255, 255),
                                      self.model.update_from_rgb)
        rgb_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        self.model.add_observer(rgb_frame)

        cmyk_frame = ColorSlidersFrame(right_frame, self.model, "CMYK",
                                       ('C', 'M', 'Y', 'K'), (100, 100, 100, 100),
                                       self.model.update_from_cmyk)
        cmyk_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        self.model.add_observer(cmyk_frame)
        
        hsv_frame = ColorSlidersFrame(right_frame, self.model, "HSV",
                                      ('H', 'S', 'V'), (360, 100, 100),
                                      self.model.update_from_hsv)
        hsv_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        self.model.add_observer(hsv_frame)
        
        self.model._notify()
