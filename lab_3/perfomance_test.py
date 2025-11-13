import numpy as np
from typing import List, Tuple
import time
from rasterization import RasterizationAlgorithms

class PerformanceTester:
    """Класс для тестирования производительности алгоритмов"""

    @staticmethod
    def measure_time(algorithm, *args, iterations=1000):
        """Измеряет время выполнения алгоритма"""
        start = time.perf_counter()
        for _ in range(iterations):
            algorithm(*args)
        end = time.perf_counter()
        return (end - start) / iterations * 1000000  # в микросекундах
    
    @staticmethod
    def benchmark_all(x0=0, y0=0, x1=100, y1=100, radius=50):
        """Тестирует все алгоритмы"""
        results = {}

        algos = {
            'Пошаговый': lambda: RasterizationAlgorithms.step_by_step(x0, y0, x1, y1),
            'ЦДА': lambda: RasterizationAlgorithms.dda(x0, y0, x1, y1),
            'Брезенхем (линия)': lambda: RasterizationAlgorithms.bresenham_line(x0, y0, x1, y1),
            'Брезенхем (окружность)': lambda: RasterizationAlgorithms.bresenham_circle(x0, y0, radius),
            'Ву (сглаживание)': lambda: RasterizationAlgorithms.wu_line(x0, y0, x1, y1),
            'Кастл-Питвей (сглаживание)': lambda: RasterizationAlgorithms.castle_pitteway(x0, y0, x1, y1),
        }


        for name, algo in algos.items():
            time_us = PerformanceTester.measure_time(algo)
            pixels = algo()
            results[name] = {
                'time_us': time_us,
                'pixels': len(pixels)
            }
        
        return results