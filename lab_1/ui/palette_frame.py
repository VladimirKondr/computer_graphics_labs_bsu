import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from PIL import Image, ImageTk
import color_utils
import math

class PaletteFrame(ttk.Frame):
    def __init__(self, master, model):
        super().__init__(master, padding=10)
        self.model = model
        self._is_internal_update = False
        
        self.palette_size = 0
        self.center_x = 0
        self.center_y = 0
        self.radius = 0
        self._resize_timer = None

        main_frame = ttk.LabelFrame(self, text="Палитра и предпросмотр", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        self.palette_canvas = tk.Canvas(main_frame, borderwidth=0, highlightthickness=0)
        self.palette_canvas.grid(row=0, column=0, rowspan=3, sticky="nsew") 

        self.canvas_image_item = self.palette_canvas.create_image(0, 0, anchor='nw')
        self.photo_image_ref = None

        self.value_var = tk.DoubleVar(value=100.0)
        self.value_slider = ttk.Scale(main_frame, from_=100, to=0, orient=tk.VERTICAL,
                                      variable=self.value_var, command=self._on_value_slider_change)
        self.value_slider.grid(row=0, column=1, rowspan=3, sticky='ns', padx=10)

        right_column = ttk.Frame(main_frame)
        right_column.grid(row=0, column=2, rowspan=3, sticky='ns', padx=(10, 0))

        self.preview_label = ttk.Label(right_column, text="Текущий цвет:")
        self.preview_label.pack(anchor='w')
        self.preview = tk.Frame(right_column, width=100, height=100, relief='sunken', borderwidth=1)
        self.preview.pack(pady=5)
        
        self.hex_label_title = ttk.Label(right_column, text="HEX:")
        self.hex_label_title.pack(anchor='w', pady=(10, 0))

        self.hex_var = tk.StringVar()
        self.hex_entry = ttk.Entry(right_column, textvariable=self.hex_var, width=12, font="appDefaultFont")
        self.hex_entry.pack(anchor='w')
        self.hex_entry.bind('<Return>', self._on_hex_change)

        self.cursor_id = self.palette_canvas.create_oval(0, 0, 10, 10, outline='black', width=2)

        self.palette_canvas.bind('<B1-Motion>', self._on_palette_drag)
        self.palette_canvas.bind('<Button-1>', self._on_palette_drag)
        self.palette_canvas.bind('<Configure>', self._on_resize)

        self.bind('<Configure>', lambda e: self.update_widget_sizes())

    def _on_resize(self, event):
        if self._resize_timer:
            self.after_cancel(self._resize_timer)
        self._resize_timer = self.after(150, self._perform_redraw, event)

    def _perform_redraw(self, event):
        new_size = min(event.width, event.height)

        if new_size < 50 or new_size == self.palette_size:
            return
            
        self.palette_size = new_size
        self.center_x = new_size // 2
        self.center_y = new_size // 2
        self.radius = new_size // 2

        self._draw_palette()
        self.update_from_model()

    def _draw_palette(self):
        if self.palette_size == 0: return

        image = Image.new("RGB", (self.palette_size, self.palette_size), "white")
        pixels = image.load()

        for y in range(self.palette_size):
            for x in range(self.palette_size):
                dx, dy = x - self.center_x, y - self.center_y
                distance = math.sqrt(dx**2 + dy**2)

                if distance <= self.radius:
                    angle = math.atan2(dy, dx)
                    h = int((math.degrees(angle) + 360) % 360)
                    s = int((distance / self.radius) * 100)
                    r, g, b = color_utils.hsv_to_rgb(h, s, 100)
                    pixels[x, y] = (r, g, b)
        
        self.photo_image_ref = ImageTk.PhotoImage(image)
        self.palette_canvas.itemconfig(self.canvas_image_item, image=self.photo_image_ref)
        self.palette_canvas.tag_raise(self.cursor_id)

    def _on_palette_drag(self, event):
        if self._is_internal_update or self.radius == 0: return
        dx, dy = event.x - self.center_x, event.y - self.center_y
        distance = min(math.sqrt(dx**2 + dy**2), self.radius)
        
        h, s = 0, 0
        if distance > 0:
            angle = math.atan2(dy, dx)
            h = int((math.degrees(angle) + 360) % 360)
            s = int((distance / self.radius) * 100)
        else:
            h, s = self.model.get_hsv()[0], 0
        
        v = self.value_var.get()
        self._update_local_ui_and_notify_model(h, s, v)

    def _on_value_slider_change(self, event=None):
        if self._is_internal_update: return
        h, s, _ = self.model.get_hsv()
        v = self.value_var.get()
        self._update_local_ui_and_notify_model(h, s, v)

    def _update_local_ui_and_notify_model(self, h, s, v):
        self._update_cursor(h, s, v)
        r, g, b = color_utils.hsv_to_rgb(h, s, v)
        hex_color = color_utils.rgb_to_hex(r, g, b)
        self.preview.config(bg=hex_color)
        self.hex_var.set(hex_color)
        self.model.update_from_hsv(h, s, v, source=self)

    def _update_cursor(self, h, s, v):
        if self.radius == 0: return
        angle_rad = math.radians(h)
        distance = (s / 100) * self.radius
        
        x = self.center_x + distance * math.cos(angle_rad)
        y = self.center_y + distance * math.sin(angle_rad)
        
        self.palette_canvas.coords(self.cursor_id, x - 5, y - 5, x + 5, y + 5)
        cursor_outline = 'black' if v > 50 else 'white'
        self.palette_canvas.itemconfig(self.cursor_id, outline=cursor_outline)

    def _on_hex_change(self, event=None):
        if self._is_internal_update: return
        hex_code = self.hex_var.get().strip()
        if not hex_code.startswith('#'):
            hex_code = '#' + hex_code
        if len(hex_code) == 7:
            try:
                r = int(hex_code[1:3], 16)
                g = int(hex_code[3:5], 16)
                b = int(hex_code[5:7], 16)
                self.model.update_from_rgb(r, g, b, source=self)
            except ValueError:
                self.update_from_model()

    def update_from_model(self):
        self._is_internal_update = True
        h, s, v = self.model.get_hsv()
        hex_color = self.model.get_hex()
        
        self._update_cursor(h, s, v)
        self.value_var.set(v)
        self.preview.config(bg=hex_color)
        self.hex_var.set(hex_color)
        self._is_internal_update = False

    def update_widget_sizes(self):
        font = tkFont.nametofont("appDefaultFont") if "appDefaultFont" in tkFont.families() or True else tkFont.Font(family="Helvetica", size=12)
        char_px = max(4, font.measure('0'))

        width = self.winfo_width() or self.winfo_toplevel().winfo_width()
        if width <= 1:
            width = self.winfo_toplevel().winfo_screenwidth()

        target_px = max(80, int(width * 0.03))
        width_chars = max(6, int(target_px / char_px))
        self.hex_entry.config(width=width_chars)

        preview_px = max(60, min(200, int(width * 0.08)))
        self.preview.config(width=preview_px, height=preview_px)