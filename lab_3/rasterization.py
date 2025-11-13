import numpy as np
from typing import List, Tuple
import time
from skimage.draw import line, line_aa, circle_perimeter


class RasterizationAlgorithms:
    """Базовые алгоритмы растеризации"""
    
    @staticmethod
    def step_by_step(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        """
        Пошаговый алгоритм (наивный)
        """
        pixels = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        
        if dx == 0 and dy == 0:
            return [(x0, y0)]
        
        steps = max(dx, dy)
        x_step = (x1 - x0) / steps
        y_step = (y1 - y0) / steps
        
        for i in range(steps + 1):
            x = round(x0 + i * x_step)
            y = round(y0 + i * y_step)
            pixels.append((x, y))
        
        return pixels
    
    @staticmethod
    def dda(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        """
        Алгоритм ЦДА
        """
        rr, cc = line(y0, x0, y1, x1)
        return list(zip(cc, rr))
    
    @staticmethod
    def bresenham_line(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        """
        Алгоритм Брезенхема для линий
        """
        rr, cc = line(y0, x0, y1, x1)
        return list(zip(cc, rr))
    
    @staticmethod
    def bresenham_circle(xc: int, yc: int, radius: int) -> List[Tuple[int, int]]:
        """
        Алгоритм Брезенхема для окружности
        """
        rr, cc = circle_perimeter(yc, xc, radius)
        return list(zip(cc, rr))
    
    @staticmethod
    def wu_line(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        """
        Алгоритм Ву (антиалиасинг)
        """
        rr, cc, val = line_aa(y0, x0, y1, x1)
        return list(zip(cc, rr, val))
    
    @staticmethod
    def castle_pitteway(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        pixels = []
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        
        if dx == 0 and dy == 0:
            return [(x0, y0, 1.0)]
        
        steep = dy > dx
        
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
            dx, dy = dy, dx
        
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        
        gradient = (y1 - y0) / (x1 - x0) if (x1 - x0) != 0 else 0
        y_step = 1 if y0 < y1 else -1
        
        y = y0
        y_float = float(y0)
        
        for x in range(x0, x1 + 1):
            ideal_y = y0 + gradient * (x - x0)
            
            distance = abs(y - ideal_y)
            
            intensity1 = max(0, 1 - distance)
            intensity2 = max(0, distance) if distance < 1 else 0
            
            if steep:
                pixels.append((y, x, intensity1))
                if intensity2 > 0.01:
                    pixels.append((y + y_step, x, intensity2))
            else:
                pixels.append((x, y, intensity1))
                if intensity2 > 0.01:
                    pixels.append((x, y + y_step, intensity2))
            
            y_float += gradient
            new_y = round(y_float)
            
            if new_y != y:
                y = new_y
        
        return pixels
