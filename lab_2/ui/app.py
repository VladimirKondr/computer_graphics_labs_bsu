import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os

from image_processor import ImageProcessor
from ttkthemes import ThemedTk

class ImageProcessorApp(ThemedTk):
    def __init__(self):
        super().__init__()
        self.set_theme("arc")
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        style = ttk.Style(self)
        
        font_normal = ("Lato", 10)
        font_bold = ("Lato", 11, "bold")

        style.configure(".", font=font_normal)
        style.configure("TLabelframe.Label", font=font_bold)
        style.configure("TButton", padding=5)
        style.configure("Header.TLabel", font=font_bold) 
        
        self.title("Лабораторная работа №2: Обработка изображений")
        self.geometry("1400x800")
        
        self.processor = ImageProcessor()
        self.original_image = None
        self.processed_image = None
        self._debounce_timer = None
        self._realtime_preview = tk.BooleanVar(value=True)
        
        self.status_var = tk.StringVar(value="Готов")
        
        self._build_ui()
    
    def _build_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Выбрать из test_images", command=self._browse_test_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Загрузить изображение", command=self._load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Сохранить результат", command=self._save_image).pack(side=tk.LEFT, padx=5)
        
        main_frame = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_panel = ttk.Frame(main_frame)
        main_frame.add(left_panel, weight=1)
        
        control_panel = ttk.Frame(main_frame, width=300)
        main_frame.add(control_panel, weight=0)
        
        ttk.Label(left_panel, text="Исходное изображение").pack()
        self.original_canvas = tk.Canvas(left_panel, bg='gray', width=400, height=300)
        self.original_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(left_panel, text="Обработанное изображение").pack()
        self.processed_canvas = tk.Canvas(left_panel, bg='gray', width=400, height=300)
        self.processed_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(control_panel, text="Метод обработки", style="Header.TLabel").pack(pady=10)
        
        self.method_var = tk.StringVar(value='equalize_rgb')
        
        methods_frame = ttk.LabelFrame(control_panel, text="Гистограммы", padding=10)
        methods_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(methods_frame, text="Эквализация RGB", variable=self.method_var, 
                       value='equalize_rgb', command=self._on_method_change).pack(anchor=tk.W)
        ttk.Radiobutton(methods_frame, text="Эквализация HSV (V)", variable=self.method_var, 
                       value='equalize_hsv', command=self._on_method_change).pack(anchor=tk.W)
        ttk.Radiobutton(methods_frame, text="Линейное контрастирование", variable=self.method_var, 
                       value='linear_contrast', command=self._on_method_change).pack(anchor=tk.W)
        
        seg_frame = ttk.LabelFrame(control_panel, text="Сегментация", padding=10)
        seg_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(seg_frame, text="Обнаружение точек", variable=self.method_var, 
                       value='point_detection', command=self._on_method_change).pack(anchor=tk.W)
        ttk.Radiobutton(seg_frame, text="Линии: горизонтальные", variable=self.method_var, 
                       value='line_h', command=self._on_method_change).pack(anchor=tk.W)
        ttk.Radiobutton(seg_frame, text="Линии: вертикальные", variable=self.method_var, 
                       value='line_v', command=self._on_method_change).pack(anchor=tk.W)
        ttk.Radiobutton(seg_frame, text="Линии: диагональ 45°", variable=self.method_var, 
                       value='line_d45', command=self._on_method_change).pack(anchor=tk.W)
        ttk.Radiobutton(seg_frame, text="Линии: диагональ 135°", variable=self.method_var, 
                       value='line_d135', command=self._on_method_change).pack(anchor=tk.W)
        
        edge_frame = ttk.LabelFrame(control_panel, text="Границы", padding=10)
        edge_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(edge_frame, text="Sobel", variable=self.method_var, 
                       value='edge_sobel', command=self._on_method_change).pack(anchor=tk.W)
        ttk.Radiobutton(edge_frame, text="Prewitt", variable=self.method_var, 
                       value='edge_prewitt', command=self._on_method_change).pack(anchor=tk.W)
        ttk.Radiobutton(edge_frame, text="Roberts", variable=self.method_var, 
                       value='edge_roberts', command=self._on_method_change).pack(anchor=tk.W)
        ttk.Radiobutton(edge_frame, text="Комбинированное", variable=self.method_var, 
                       value='edge_combined', command=self._on_method_change).pack(anchor=tk.W)
        
        params_frame = ttk.LabelFrame(control_panel, text="Параметры", padding=10)
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(params_frame, text="Порог:").pack(anchor=tk.W)
        self.threshold_var = tk.IntVar(value=100)
        self.threshold_scale = ttk.Scale(params_frame, from_=0, to=255, orient=tk.HORIZONTAL,
                                        variable=self.threshold_var, command=self._on_threshold_change)
        self.threshold_scale.pack(fill=tk.X)
        self.threshold_label = ttk.Label(params_frame, text="100")
        self.threshold_label.pack(anchor=tk.W)
        
        self.threshold_info = ttk.Label(params_frame, text="", foreground="gray")
        self.threshold_info.pack(anchor=tk.W, pady=(5, 0))
        
        self.realtime_check = ttk.Checkbutton(params_frame, text="Real-time preview", 
                                              variable=self._realtime_preview)
        self.realtime_check.pack(anchor=tk.W, pady=(5, 0))
        
        ttk.Button(control_panel, text="Применить", command=self._apply_processing).pack(pady=10)
        ttk.Button(control_panel, text="Показать гистограмму", command=self._show_histogram).pack(pady=5)
        
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self._on_method_change()
    
    def _on_method_change(self):
        method = self.method_var.get()
        needs_threshold = method in ['point_detection', 'line_h', 'line_v', 'line_d45', 'line_d135',
                                     'edge_sobel', 'edge_prewitt', 'edge_roberts', 'edge_combined']
        
        if needs_threshold:
            self.threshold_scale.config(state='normal')
            self.threshold_info.config(text="")
        else:
            self.threshold_scale.config(state='disabled')
            self.threshold_info.config(text="(порог не используется)")
        
        if self._realtime_preview.get() and self.original_image is not None:
            self._apply_processing()

    
    def _on_threshold_change(self, value):
        self.threshold_label.config(text=str(int(float(value))))
        
        if not self._realtime_preview.get() or self.original_image is None:
            return
        
        method = self.method_var.get()
        needs_threshold = method in ['point_detection', 'line_h', 'line_v', 'line_d45', 'line_d135',
                                     'edge_sobel', 'edge_prewitt', 'edge_roberts', 'edge_combined']
        
        if not needs_threshold:
            return
        
        if self._debounce_timer is not None:
            self.after_cancel(self._debounce_timer)
        
        self._debounce_timer = self.after(150, self._apply_processing_debounced)
    
    def _browse_test_images(self):
        test_images_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_images')
        
        if not os.path.exists(test_images_path):
            messagebox.showerror("Ошибка", f"Папка test_images не найдена: {test_images_path}")
            return
        
        browser = ImageBrowser(self, test_images_path)
        self.wait_window(browser)
        
        if browser.selected_image:
            try:
                self.original_image = Image.open(browser.selected_image)
                self._display_image(self.original_image, self.original_canvas)
                self.processed_image = None
                self.processed_canvas.delete('all')
                self.status_var.set(f"Загружено: {os.path.basename(browser.selected_image)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{e}")
    
    def _load_image(self):
        filepath = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("Все файлы", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            self.original_image = Image.open(filepath)
            self._display_image(self.original_image, self.original_canvas)
            self.processed_image = None
            self.processed_canvas.delete('all')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{e}")
    
    def _save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Предупреждение", "Нет обработанного изображения для сохранения")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Сохранить результат",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Все файлы", "*.*")]
        )
        
        if filepath:
            try:
                self.processed_image.save(filepath)
                messagebox.showinfo("Успех", "Изображение сохранено")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить изображение:\n{e}")
    
    def _apply_processing(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return
        
        method = self.method_var.get()
        threshold = self.threshold_var.get()
        
        
        self.config(cursor="watch")
        self.update()
        
        try:
            if method == 'equalize_rgb':
                self.processed_image = self.processor.process_histogram_equalize_rgb(self.original_image)
            elif method == 'equalize_hsv':
                self.processed_image = self.processor.process_histogram_equalize_hsv(self.original_image)
            elif method == 'linear_contrast':
                self.processed_image = self.processor.process_linear_contrast(self.original_image)
            elif method == 'point_detection':
                self.processed_image = self.processor.process_point_detection(self.original_image, threshold)
            elif method == 'line_h':
                self.processed_image = self.processor.process_line_detection(self.original_image, 'horizontal', threshold)
            elif method == 'line_v':
                self.processed_image = self.processor.process_line_detection(self.original_image, 'vertical', threshold)
            elif method == 'line_d45':
                self.processed_image = self.processor.process_line_detection(self.original_image, 'diagonal_45', threshold)
            elif method == 'line_d135':
                self.processed_image = self.processor.process_line_detection(self.original_image, 'diagonal_135', threshold)
            elif method == 'edge_sobel':
                self.processed_image = self.processor.process_edge_detection(self.original_image, 'sobel', threshold)
            elif method == 'edge_prewitt':
                self.processed_image = self.processor.process_edge_detection(self.original_image, 'prewitt', threshold)
            elif method == 'edge_roberts':
                self.processed_image = self.processor.process_edge_detection(self.original_image, 'roberts', threshold)
            elif method == 'edge_combined':
                self.processed_image = self.processor.process_combined_edges(self.original_image, threshold)
            
            self._display_image(self.processed_image, self.processed_canvas)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Ошибка обработки", f"Произошла ошибка:\n{e}")
        finally:
            self.config(cursor="")
    
    def _apply_processing_debounced(self):
        """Debounced версия для real-time preview"""
        self._debounce_timer = None
        try:
            self.status_var.set("Обработка...")
            self.update_idletasks()
            self._apply_processing()
            self.status_var.set("Готов")
        except Exception as e:
            self.status_var.set("Ошибка")
            print(f"Error in debounced processing: {e}")
    
    def _display_image(self, image, canvas):
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 300
        
        img_copy = image.copy()
        img_copy.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_copy)
        
        canvas.delete('all')
        canvas.create_image(canvas_width//2, canvas_height//2, image=photo, anchor=tk.CENTER)
        canvas.image = photo
    
    def _show_histogram(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return
        
        hist_window = tk.Toplevel(self)
        hist_window.title("Гистограммы")
        hist_window.geometry("1200x800")
        
        def on_hist_close():
            plt.close(fig)
            hist_window.destroy()
        
        hist_window.protocol("WM_DELETE_WINDOW", on_hist_close)
        
        has_processed = self.processed_image is not None
        rows = 2 if has_processed else 1
        
        fig, axes = plt.subplots(rows, 3, figsize=(12, 4*rows))
        if rows == 1:
            axes = axes.reshape(1, -1)
        fig.tight_layout(pad=3.0)
        
        orig_hist = self.processor.get_histogram(self.original_image, downsample_for_display=True)
        
        if isinstance(orig_hist, tuple):
            hist_r, hist_g, hist_b = orig_hist
            
            axes[0, 0].bar(range(256), hist_r, color='red', alpha=0.8, width=1)
            axes[0, 0].set_title('Исходное: Red канал', fontsize=10)
            axes[0, 0].set_xlim([0, 255])
            axes[0, 0].grid(alpha=0.3)
            
            axes[0, 1].bar(range(256), hist_g, color='green', alpha=0.8, width=1)
            axes[0, 1].set_title('Исходное: Green канал', fontsize=10)
            axes[0, 1].set_xlim([0, 255])
            axes[0, 1].grid(alpha=0.3)
            
            axes[0, 2].bar(range(256), hist_b, color='blue', alpha=0.8, width=1)
            axes[0, 2].set_title('Исходное: Blue канал', fontsize=10)
            axes[0, 2].set_xlim([0, 255])
            axes[0, 2].grid(alpha=0.3)
        else:
            
            if np.count_nonzero(orig_hist) <= 10:
                nonzero_indices = np.nonzero(orig_hist)[0]
                nonzero_values = orig_hist[nonzero_indices]
                
                axes[0, 0].bar(nonzero_indices, nonzero_values, color='black', alpha=0.8, width=3)
                axes[0, 0].set_title(f'Исходное (Grayscale, {len(nonzero_indices)} unique values)', fontsize=10)
                axes[0, 0].set_xlabel('Intensity')
                axes[0, 0].set_ylabel('Count')
                
                for idx, val in zip(nonzero_indices, nonzero_values):
                    axes[0, 0].text(idx, val, f'{int(val)}', ha='center', va='bottom', fontsize=8)
            else:
                axes[0, 0].bar(range(256), orig_hist, color='black', alpha=0.8, width=1)
                axes[0, 0].set_title('Исходное (Grayscale)', fontsize=10)
            
            axes[0, 0].set_xlim([0, 255])
            axes[0, 0].grid(alpha=0.3)
            axes[0, 1].axis('off')
            axes[0, 2].axis('off')
        
        if has_processed:
            proc_hist = self.processor.get_histogram(self.processed_image, downsample_for_display=True)
            
            if isinstance(proc_hist, tuple):
                hist_r, hist_g, hist_b = proc_hist
                
                axes[1, 0].bar(range(256), hist_r, color='red', alpha=0.8, width=1)
                axes[1, 0].set_title('Обработанное: Red канал', fontsize=10)
                axes[1, 0].set_xlim([0, 255])
                axes[1, 0].grid(alpha=0.3)
                
                axes[1, 1].bar(range(256), hist_g, color='green', alpha=0.8, width=1)
                axes[1, 1].set_title('Обработанное: Green канал', fontsize=10)
                axes[1, 1].set_xlim([0, 255])
                axes[1, 1].grid(alpha=0.3)
                
                axes[1, 2].bar(range(256), hist_b, color='blue', alpha=0.8, width=1)
                axes[1, 2].set_title('Обработанное: Blue канал', fontsize=10)
                axes[1, 2].set_xlim([0, 255])
                axes[1, 2].grid(alpha=0.3)
            else:
                
                if np.count_nonzero(proc_hist) <= 10:
                    nonzero_indices = np.nonzero(proc_hist)[0]
                    nonzero_values = proc_hist[nonzero_indices]
                    
                    axes[1, 0].bar(nonzero_indices, nonzero_values, color='black', alpha=0.8, width=3)
                    axes[1, 0].set_title(f'Обработанное (Grayscale, {len(nonzero_indices)} unique values)', fontsize=10)
                    axes[1, 0].set_xlabel('Intensity')
                    axes[1, 0].set_ylabel('Count')
                    
                    for idx, val in zip(nonzero_indices, nonzero_values):
                        axes[1, 0].text(idx, val, f'{int(val)}', ha='center', va='bottom', fontsize=8)
                else:
                    axes[1, 0].bar(range(256), proc_hist, color='black', alpha=0.8, width=1)
                    axes[1, 0].set_title('Обработанное (Grayscale)', fontsize=10)
                
                axes[1, 0].set_xlim([0, 255])
                axes[1, 0].grid(alpha=0.3)
                axes[1, 1].axis('off')
                axes[1, 2].axis('off')
        
        canvas = FigureCanvasTkAgg(fig, master=hist_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _on_closing(self):
        plt.close('all')
        self.quit()
        self.destroy()


class ImageBrowser(tk.Toplevel):
    def __init__(self, parent, test_images_path):
        super().__init__(parent)
        self.title("Выбор изображения из test_images")
        self.geometry("1000x700")
        self.resizable(True, True)
        
        self.test_images_path = test_images_path
        self.selected_image = None
        self.thumbnails = {}
        
        self._build_ui()
        self._scan_images()
    
    def _build_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text="Папка:", font=("Lato", 10, "bold")).pack(side=tk.LEFT)
        self.folder_var = tk.StringVar()
        self.folder_combo = ttk.Combobox(top_frame, textvariable=self.folder_var, state='readonly', width=30)
        self.folder_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.folder_combo.bind('<<ComboboxSelected>>', self._on_folder_change)
        
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas_frame = ttk.Frame(main_container)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.images_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.images_frame, anchor='nw')
        
        self.images_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Отмена", command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _scan_images(self):
        self.image_data = {}
        
        for root, dirs, files in os.walk(self.test_images_path):
            rel_path = os.path.relpath(root, self.test_images_path)
            if rel_path == '.':
                rel_path = 'root'
            
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
            
            if image_files:
                self.image_data[rel_path] = {
                    'path': root,
                    'files': sorted(image_files)
                }
        
        folders = sorted(self.image_data.keys())
        self.folder_combo['values'] = folders
        
        if folders:
            self.folder_combo.current(0)
            self._on_folder_change()
    
    def _on_folder_change(self, event=None):
        folder = self.folder_var.get()
        
        if not folder or folder not in self.image_data:
            return
        
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        
        self.thumbnails.clear()
        
        data = self.image_data[folder]
        folder_path = data['path']
        files = data['files']
        
        cols = 4
        row = 0
        col = 0
        
        for filename in files:
            filepath = os.path.join(folder_path, filename)
            
            frame = ttk.Frame(self.images_frame, relief=tk.RIDGE, borderwidth=2)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            try:
                img = Image.open(filepath)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.thumbnails[filepath] = photo
                
                img_label = tk.Label(frame, image=photo, cursor='hand2')
                img_label.pack(padx=5, pady=5)
                img_label.bind('<Button-1>', lambda e, path=filepath: self._select_image(path))
                
                info_frame = ttk.Frame(frame)
                info_frame.pack(fill=tk.X, padx=5, pady=5)
                
                name_label = ttk.Label(info_frame, text=filename, wraplength=180, justify=tk.CENTER, font=("Lato", 9))
                name_label.pack()
                
                orig_img = Image.open(filepath)
                size_label = ttk.Label(info_frame, text=f"{orig_img.size[0]}×{orig_img.size[1]} | {orig_img.mode}", 
                                      font=("Lato", 8), foreground='gray')
                size_label.pack()
                
            except Exception as e:
                error_label = ttk.Label(frame, text=f"Ошибка:\n{filename}", foreground='red')
                error_label.pack(padx=5, pady=5)
            
            col += 1
            if col >= cols:
                col = 0
                row += 1
        
        for i in range(cols):
            self.images_frame.columnconfigure(i, weight=1)
        
        self.canvas.yview_moveto(0)
    
    def _select_image(self, filepath):
        self.selected_image = filepath
        self.destroy()
