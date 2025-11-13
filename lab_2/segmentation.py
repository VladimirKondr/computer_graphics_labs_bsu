import numpy as np
from PIL import Image


def convolve2d(image, kernel):
    """Оптимизированная свертка 2D с использованием векторизации numpy."""
    k_height, k_width = kernel.shape
    img_height, img_width = image.shape
    
    pad_h = k_height // 2
    pad_w = k_width // 2
    
    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
    result = np.zeros_like(image, dtype=np.float32)
    
    for i in range(k_height):
        for j in range(k_width):
            result += kernel[i, j] * padded[i:i+img_height, j:j+img_width]
    
    return result


class SegmentationProcessor:
    @staticmethod
    def point_detection(image, threshold=50):
        img_gray = image.convert('L')
        img_array = np.array(img_gray, dtype=np.float32)
        
        kernel = np.array([[-1, -1, -1],
                          [-1,  8, -1],
                          [-1, -1, -1]])
        
        filtered = convolve2d(img_array, kernel)
        result = np.abs(filtered)
        result = np.where(result > threshold, 255, 0).astype(np.uint8)
        
        return Image.fromarray(result)

    @staticmethod
    def line_detection(image, direction='horizontal', threshold=100):
        img_gray = image.convert('L')
        img_array = np.array(img_gray, dtype=np.float32)
        
        kernels = {
            'horizontal': np.array([[-1, -1, -1],
                                   [ 2,  2,  2],
                                   [-1, -1, -1]]),
            'vertical': np.array([[-1, 2, -1],
                                 [-1, 2, -1],
                                 [-1, 2, -1]]),
            'diagonal_45': np.array([[-1, -1, 2],
                                    [-1,  2, -1],
                                    [ 2, -1, -1]]),
            'diagonal_135': np.array([[ 2, -1, -1],
                                     [-1,  2, -1],
                                     [-1, -1,  2]])
        }
        
        kernel = kernels.get(direction, kernels['horizontal'])
        filtered = convolve2d(img_array, kernel)
        result = np.abs(filtered)
        result = np.where(result > threshold, 255, 0).astype(np.uint8)
        
        return Image.fromarray(result)

    @staticmethod
    def edge_detection(image, method='sobel', threshold=100):
        img_gray = image.convert('L')
        img_array = np.array(img_gray, dtype=np.float32)
        
        if method == 'sobel':
            kernel_x = np.array([[-1, 0, 1],
                                [-2, 0, 2],
                                [-1, 0, 1]])
            kernel_y = np.array([[-1, -2, -1],
                                [ 0,  0,  0],
                                [ 1,  2,  1]])
        elif method == 'prewitt':
            kernel_x = np.array([[-1, 0, 1],
                                [-1, 0, 1],
                                [-1, 0, 1]])
            kernel_y = np.array([[-1, -1, -1],
                                [ 0,  0,  0],
                                [ 1,  1,  1]])
        elif method == 'roberts':
            kernel_x = np.array([[1, 0],
                                [0, -1]])
            kernel_y = np.array([[0, 1],
                                [-1, 0]])
            
            gx = convolve2d(img_array, kernel_x)
            gy = convolve2d(img_array, kernel_y)
            magnitude = np.sqrt(gx**2 + gy**2)
            result = np.where(magnitude > threshold, 255, 0).astype(np.uint8)
            return Image.fromarray(result)
        else:
            kernel_x = np.array([[-1, 0, 1],
                                [-2, 0, 2],
                                [-1, 0, 1]])
            kernel_y = np.array([[-1, -2, -1],
                                [ 0,  0,  0],
                                [ 1,  2,  1]])
        
        gx = convolve2d(img_array, kernel_x)
        gy = convolve2d(img_array, kernel_y)
        magnitude = np.sqrt(gx**2 + gy**2)
        
        result = np.where(magnitude > threshold, 255, 0).astype(np.uint8)
        
        return Image.fromarray(result)

    @staticmethod
    def combined_edge_detection(image, threshold=100):
        img_gray = image.convert('L')
        img_array = np.array(img_gray, dtype=np.float32)
        
        kernels = [
            np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]]),
            np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]]),
            np.array([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]]),
            np.array([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]])
        ]
        
        results = []
        for kernel in kernels:
            filtered = convolve2d(img_array, kernel)
            results.append(np.abs(filtered))
        
        combined = np.maximum.reduce(results)
        result = np.where(combined > threshold, 255, 0).astype(np.uint8)
        
        return Image.fromarray(result)
