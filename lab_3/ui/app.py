import tkinter as tk
from tkinter import ttk, messagebox
import math
import sys
import os

from ttkthemes import ThemedTk

from rasterization import RasterizationAlgorithms
from perfomance_test import PerformanceTester


class RasterizationApp(ThemedTk):
    def __init__(self):
        super().__init__()
        self.set_theme("arc")
        
        self.title("Лабораторная работа №3: Базовые растровые алгоритмы")
        self.geometry("1400x900")
        
        self.algorithms = RasterizationAlgorithms()
        self.current_pixels = []
        self.grid_size = 20
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        self._build_ui()
        
    def _build_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        ttk.Label(toolbar, text="Алгоритм:").pack(side=tk.LEFT, padx=5)
        
        self.algorithm_var = tk.StringVar(value="bresenham_line")
        algorithms = [
            ("Пошаговый", "step_by_step"),
            ("ЦДА", "dda"),
            ("Брезенхем (линия)", "bresenham_line"),
            ("Брезенхем (окружность)", "bresenham_circle"),
            ("Ву (сглаживание)", "wu_line"),
            ("Кастл-Питвей (сглаживание)", "castle_pitteway")
        ]
        
        for text, value in algorithms:
            ttk.Radiobutton(toolbar, text=text, variable=self.algorithm_var, 
                          value=value, command=self._on_algorithm_change).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(toolbar, text="Бенчмарк", command=self._show_benchmark).pack(side=tk.RIGHT, padx=5)
        ttk.Button(toolbar, text="Очистить", command=self._clear).pack(side=tk.RIGHT, padx=5)
        
        main_frame = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas_frame = ttk.Frame(main_frame)
        main_frame.add(canvas_frame, weight=1)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', cursor='crosshair')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.canvas.bind('<MouseWheel>', self._on_zoom)
        self.canvas.bind('<Button-4>', self._on_zoom)
        self.canvas.bind('<Button-5>', self._on_zoom)
        
        control_panel = ttk.Frame(main_frame, width=350)
        main_frame.add(control_panel, weight=0)
        
        coord_frame = ttk.LabelFrame(control_panel, text="Координаты", padding=10)
        coord_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(coord_frame, text="Точка 1 (x₀, y₀):").pack(anchor=tk.W)
        coord1_frame = ttk.Frame(coord_frame)
        coord1_frame.pack(fill=tk.X, pady=2)
        ttk.Label(coord1_frame, text="x:").pack(side=tk.LEFT)
        self.x0_var = tk.IntVar(value=10)
        ttk.Entry(coord1_frame, textvariable=self.x0_var, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(coord1_frame, text="y:").pack(side=tk.LEFT)
        self.y0_var = tk.IntVar(value=10)
        ttk.Entry(coord1_frame, textvariable=self.y0_var, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(coord_frame, text="Точка 2 (x₁, y₁) / Радиус:").pack(anchor=tk.W, pady=(10, 0))
        coord2_frame = ttk.Frame(coord_frame)
        coord2_frame.pack(fill=tk.X, pady=2)
        ttk.Label(coord2_frame, text="x/r:").pack(side=tk.LEFT)
        self.x1_var = tk.IntVar(value=50)
        ttk.Entry(coord2_frame, textvariable=self.x1_var, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(coord2_frame, text="y:").pack(side=tk.LEFT)
        self.y1_var = tk.IntVar(value=50)
        self.y1_entry = ttk.Entry(coord2_frame, textvariable=self.y1_var, width=8)
        self.y1_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(coord_frame, text="Нарисовать", command=self._draw).pack(pady=10, fill=tk.X)
        
        info_frame = ttk.LabelFrame(control_panel, text="Информация", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.info_text = tk.Text(info_frame, height=15, wrap=tk.WORD, font=("Courier", 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(info_frame, command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        
        view_frame = ttk.LabelFrame(control_panel, text="Настройки отображения", padding=10)
        view_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(view_frame, text="Размер ячейки сетки:").pack(anchor=tk.W)
        self.grid_var = tk.IntVar(value=20)
        ttk.Scale(view_frame, from_=10, to=50, variable=self.grid_var, 
                 orient=tk.HORIZONTAL, command=self._on_grid_change).pack(fill=tk.X)
        
        self.grid_label = ttk.Label(view_frame, text="20px")
        self.grid_label.pack(anchor=tk.W)
        
        self.show_grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(view_frame, text="Показать сетку", 
                       variable=self.show_grid_var, command=self._redraw).pack(anchor=tk.W, pady=5)
        
        self.show_coords_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(view_frame, text="Показать координаты", 
                       variable=self.show_coords_var, command=self._redraw).pack(anchor=tk.W)
        
        self.click_start = None
        self._redraw()
    
    def _on_algorithm_change(self):
        """Обработчик смены алгоритма"""
        algo = self.algorithm_var.get()
        if algo == "bresenham_circle":
            self.y1_entry.config(state='disabled')
        else:
            self.y1_entry.config(state='normal')
        self._update_info()
    
    def _on_grid_change(self, value):
        """Обработчик изменения размера сетки"""
        self.grid_size = int(float(value))
        self.grid_label.config(text=f"{self.grid_size}px")
        self._redraw()
    
    def _on_click(self, event):
        """Обработчик клика мыши"""
        self.click_start = (event.x, event.y)
        x0, y0 = self._canvas_to_grid(event.x, event.y)
        self.x0_var.set(x0)
        self.y0_var.set(y0)
    
    def _on_drag(self, event):
        """Обработчик перетаскивания мыши"""
        if self.click_start:
            x1, y1 = self._canvas_to_grid(event.x, event.y)
            algo = self.algorithm_var.get()
            
            if algo == "bresenham_circle":
                x0 = self.x0_var.get()
                y0 = self.y0_var.get()
                radius = int(math.sqrt((x1 - x0)**2 + (y1 - y0)**2))
                self.x1_var.set(radius)
            else:
                self.x1_var.set(x1)
                self.y1_var.set(y1)
            
            self._draw()
    
    def _on_release(self, event):
        """Обработчик отпускания кнопки мыши"""
        self.click_start = None
    
    def _on_zoom(self, event):
        """Обработчик зума колесом мыши"""
        if event.num == 4 or event.delta > 0:
            self.scale_factor *= 1.1
        elif event.num == 5 or event.delta < 0:
            self.scale_factor *= 0.9
        
        self.scale_factor = max(0.5, min(self.scale_factor, 3.0))
        self._redraw()
    
    def _canvas_to_grid(self, canvas_x, canvas_y):
        """Преобразование координат канваса в координаты сетки"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        grid_x = int((canvas_x - width/2 - self.offset_x) / (self.grid_size * self.scale_factor))
        grid_y = int((height/2 - canvas_y - self.offset_y) / (self.grid_size * self.scale_factor))
        
        return grid_x, grid_y
    
    def _grid_to_canvas(self, grid_x, grid_y):
        """Преобразование координат сетки в координаты канваса"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        canvas_x = width/2 + grid_x * self.grid_size * self.scale_factor + self.offset_x
        canvas_y = height/2 - grid_y * self.grid_size * self.scale_factor - self.offset_y
        
        return canvas_x, canvas_y
    
    def _redraw(self):
        """Перерисовка канваса"""
        self.canvas.delete("all")
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        if self.show_grid_var.get():
            self._draw_grid()
        
        self._draw_axes()
        
        self._draw_pixels()
    
    def _draw_grid(self):
        """Рисование сетки"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        step = self.grid_size * self.scale_factor
        
        x = width/2 + self.offset_x
        while x < width:
            self.canvas.create_line(x, 0, x, height, fill='#e0e0e0', width=1)
            x += step
        
        x = width/2 + self.offset_x
        while x > 0:
            self.canvas.create_line(x, 0, x, height, fill='#e0e0e0', width=1)
            x -= step
        
        y = height/2 - self.offset_y
        while y < height:
            self.canvas.create_line(0, y, width, y, fill='#e0e0e0', width=1)
            y += step
        
        y = height/2 - self.offset_y
        while y > 0:
            self.canvas.create_line(0, y, width, y, fill='#e0e0e0', width=1)
            y -= step
    
    def _draw_axes(self):
        """Рисование осей координат"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        y_axis = height/2 - self.offset_y
        self.canvas.create_line(0, y_axis, width, y_axis, fill='black', width=2, arrow=tk.LAST)
        self.canvas.create_text(width - 20, y_axis - 15, text='X', font=('Arial', 12, 'bold'))
        
        x_axis = width/2 + self.offset_x
        self.canvas.create_line(x_axis, height, x_axis, 0, fill='black', width=2, arrow=tk.LAST)
        self.canvas.create_text(x_axis + 15, 20, text='Y', font=('Arial', 12, 'bold'))
        
        if self.show_coords_var.get():
            step = self.grid_size * self.scale_factor
            
            for i in range(-20, 21):
                x_canvas, y_canvas = self._grid_to_canvas(i, 0)
                if 0 < x_canvas < width and i != 0:
                    self.canvas.create_text(x_canvas, y_axis + 15, text=str(i), 
                                          font=('Arial', 8), fill='blue')
            
            for i in range(-20, 21):
                x_canvas, y_canvas = self._grid_to_canvas(0, i)
                if 0 < y_canvas < height and i != 0:
                    self.canvas.create_text(x_axis - 15, y_canvas, text=str(i), 
                                          font=('Arial', 8), fill='blue')
    
    def _draw_pixels(self):
        """Рисование пикселей"""
        for pixel in self.current_pixels:
            if len(pixel) == 2:
                x, y = pixel
                intensity = 1.0
            else:
                x, y, intensity = pixel
            
            x_canvas, y_canvas = self._grid_to_canvas(x, y)
            size = self.grid_size * self.scale_factor
            
            color_val = int(255 * (1 - intensity))
            color = f'#{color_val:02x}{color_val:02x}{color_val:02x}'
            
            self.canvas.create_rectangle(
                x_canvas - size/2, y_canvas - size/2,
                x_canvas + size/2, y_canvas + size/2,
                fill=color, outline='', width=0
            )
    
    def _draw(self):
        """Выполнить растеризацию и отрисовку"""
        algo = self.algorithm_var.get()
        x0 = self.x0_var.get()
        y0 = self.y0_var.get()
        x1 = self.x1_var.get()
        y1 = self.y1_var.get()
        
        import time
        start = time.perf_counter()
        
        if algo == "step_by_step":
            self.current_pixels = self.algorithms.step_by_step(x0, y0, x1, y1)
        elif algo == "dda":
            self.current_pixels = self.algorithms.dda(x0, y0, x1, y1)
        elif algo == "bresenham_line":
            self.current_pixels = self.algorithms.bresenham_line(x0, y0, x1, y1)
        elif algo == "bresenham_circle":
            self.current_pixels = self.algorithms.bresenham_circle(x0, y0, x1)
        elif algo == "wu_line":
            self.current_pixels = self.algorithms.wu_line(x0, y0, x1, y1)
        elif algo == "castle_pitteway":
            self.current_pixels = self.algorithms.castle_pitteway(x0, y0, x1, y1)
        
        elapsed = (time.perf_counter() - start) * 1000000
        
        self._redraw()
        self._update_info(elapsed)
    
    def _update_info(self, elapsed_us=None):
        """Обновление информационной панели"""
        self.info_text.delete(1.0, tk.END)
        
        algo = self.algorithm_var.get()
        
        info = f"Алгоритм: {self._get_algo_name(algo)}\n\n"
        
        if algo == "bresenham_circle":
            info += f"Центр: ({self.x0_var.get()}, {self.y0_var.get()})\n"
            info += f"Радиус: {self.x1_var.get()}\n\n"
        else:
            info += f"Точка 1: ({self.x0_var.get()}, {self.y0_var.get()})\n"
            info += f"Точка 2: ({self.x1_var.get()}, {self.y1_var.get()})\n\n"
        
        if self.current_pixels:
            info += f"Количество пикселей: {len(self.current_pixels)}\n"
            
            if elapsed_us:
                info += f"Время выполнения: {elapsed_us:.2f} мкс\n\n"
            
            info += self._get_algo_description(algo)
            
            info += "\n\n=== Пример вычислений ===\n"
            info += self._get_algo_example(algo)
        
        self.info_text.insert(1.0, info)
    
    def _get_algo_name(self, algo):
        """Получить название алгоритма"""
        names = {
            "step_by_step": "Пошаговый алгоритм",
            "dda": "ЦДА (Digital Differential Analyzer)",
            "bresenham_line": "Алгоритм Брезенхема (линия)",
            "bresenham_circle": "Алгоритм Брезенхема (окружность)",
            "wu_line": "Алгоритм Ву (сглаживание)",
            "castle_pitteway": "Алгоритм Кастла-Питвея (сглаживание)"
        }
        return names.get(algo, algo)
    
    def _get_algo_description(self, algo):
        """Получить описание алгоритма"""
        descriptions = {
            "step_by_step": "Наивный алгоритм, использует\nуравнение прямой y = kx + b.\nВыполняет вычисления с плавающей\nточкой и округление для каждого\nпикселя.",
            "dda": "Использует приращения для\nвычисления координат. На каждом\nшаге добавляется фиксированное\nприращение dx/steps и dy/steps.",
            "bresenham_line": "Использует только целочисленную\nарифметику. Основан на анализе\nошибки отклонения от идеальной\nлинии. Очень эффективен.",
            "bresenham_circle": "Использует симметрию окружности\n(8 октантов). Вычисляет только\n1/8 часть, остальное получает\nотражением. Только целые числа.",
            "wu_line": "Алгоритм сглаживания (anti-aliasing).\nИспользует дробную часть координат\nдля вычисления интенсивности\nпикселей. Создает плавные линии.",
            "castle_pitteway": "Алгоритм сглаживания, использует\nрасстояние от идеальной линии для\nвычисления интенсивности пикселей.\nАльтернатива алгоритму Ву."
        }
        return descriptions.get(algo, "")
    
    def _get_algo_example(self, algo):
        """Получить пример вычислений"""
        x0 = self.x0_var.get()
        y0 = self.y0_var.get()
        x1 = self.x1_var.get()
        y1 = self.y1_var.get()
        
        if algo == "step_by_step":
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            if dx != 0:
                k = (y1 - y0) / (x1 - x0)
                b = y0 - k * x0
                example = f"dx = {dx}, dy = {dy}\n"
                example += f"k = (y1-y0)/(x1-x0) = {k:.4f}\n"
                example += f"b = y0 - k*x0 = {b:.4f}\n"
                example += f"Для x={x0}: y = {k:.4f}*{x0} + {b:.4f} = {k*x0+b:.4f} ≈ {round(k*x0+b)}"
                return example
        
        elif algo == "dda":
            dx = x1 - x0
            dy = y1 - y0
            steps = max(abs(dx), abs(dy))
            if steps > 0:
                x_inc = dx / steps
                y_inc = dy / steps
                example = f"dx = {dx}, dy = {dy}\n"
                example += f"steps = max(|dx|, |dy|) = {steps}\n"
                example += f"x_inc = dx/steps = {x_inc:.4f}\n"
                example += f"y_inc = dy/steps = {y_inc:.4f}\n"
                example += f"Шаг 0: ({x0}, {y0})\n"
                example += f"Шаг 1: ({x0+x_inc:.2f}, {y0+y_inc:.2f}) ≈ ({round(x0+x_inc)}, {round(y0+y_inc)})"
                return example
        
        elif algo == "bresenham_line":
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            err = dx - dy
            example = f"dx = {dx}, dy = {dy}\n"
            example += f"err = dx - dy = {err}\n"
            example += f"На каждом шаге:\n"
            example += f"  если 2*err > -dy: x += sx, err -= dy\n"
            example += f"  если 2*err < dx: y += sy, err += dx"
            return example
        
        elif algo == "bresenham_circle":
            r = x1
            example = f"Радиус r = {r}\n"
            example = f"Начальные значения:\n"
            example += f"  x = 0, y = r\n"
            example += f"  d = 3 - 2*r = {3 - 2*r}\n"
            example += f"На каждом шаге:\n"
            example += f"  если d < 0: d += 4*x + 6\n"
            example += f"  иначе: d += 4*(x-y) + 10, y--"
            return example
        
        elif algo == "wu_line":
            example = "Алгоритм Ву использует дробные\n"
            example += "части координат для вычисления\n"
            example += "интенсивности соседних пикселей.\n"
            example += "Интенсивность = 1 - frac(coord)"
            return example
        
        return "Нет данных"
    
    def _clear(self):
        """Очистка канваса"""
        self.current_pixels = []
        self._redraw()
        self.info_text.delete(1.0, tk.END)
    
    def _show_benchmark(self):
        """Показать результаты тестирования производительности"""
        dialog = tk.Toplevel(self)
        dialog.title("Результаты бенчмарка")
        dialog.geometry("600x400")
        
        ttk.Label(dialog, text="Тестирование производительности алгоритмов", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        text = tk.Text(dialog, wrap=tk.WORD, font=('Courier', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(dialog, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)
        
        text.insert(tk.END, "Выполняется тестирование...\n")
        dialog.update()
        
        results = PerformanceTester.benchmark_all(0, 0, 100, 100, 50)
        
        text.delete(1.0, tk.END)
        text.insert(tk.END, "Тестовые данные:\n")
        text.insert(tk.END, "  Линия: (0,0) -> (100,100)\n")
        text.insert(tk.END, "  Окружность: центр (0,0), радиус 50\n")
        text.insert(tk.END, "  Итераций: 1000\n\n")
        text.insert(tk.END, "=" * 60 + "\n\n")
        
        for name, data in results.items():
            text.insert(tk.END, f"{name}:\n")
            text.insert(tk.END, f"  Время: {data['time_us']:.2f} мкс\n")
            text.insert(tk.END, f"  Пикселей: {data['pixels']}\n\n")
        
        ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack(pady=10)


if __name__ == "__main__":
    app = RasterizationApp()
    app.mainloop()