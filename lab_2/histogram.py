import numpy as np
from PIL import Image


class HistogramProcessor:
    @staticmethod
    def compute_histogram(image, downsample_for_display=False):
        img_array = np.array(image)
        
        if downsample_for_display and img_array.size > 1000000:
            step = int(np.sqrt(img_array.size / 500000))
            if len(img_array.shape) == 2:
                img_array = img_array[::step, ::step]
            else:
                img_array = img_array[::step, ::step, :]
        
        if len(img_array.shape) == 2:
            hist, _ = np.histogram(img_array.flatten(), bins=256, range=(0, 256))
            return hist
        else:
            hist_r, _ = np.histogram(img_array[:,:,0].flatten(), bins=256, range=(0, 256))
            hist_g, _ = np.histogram(img_array[:,:,1].flatten(), bins=256, range=(0, 256))
            hist_b, _ = np.histogram(img_array[:,:,2].flatten(), bins=256, range=(0, 256))
            return hist_r, hist_g, hist_b

    @staticmethod
    def equalize_histogram_rgb(image):
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        img_array = np.array(image)
        
        if len(img_array.shape) == 2:
            equalized = HistogramProcessor._equalize_channel(img_array)
            return Image.fromarray(equalized.astype(np.uint8))
        
        result = np.zeros_like(img_array)
        for i in range(3):
            result[:,:,i] = HistogramProcessor._equalize_channel(img_array[:,:,i])
        
        return Image.fromarray(result.astype(np.uint8))

    @staticmethod
    def equalize_histogram_hsv(image):
        """Эквализация только V-компоненты в HSV пространстве."""
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        img_hsv = image.convert('HSV')
        h, s, v = img_hsv.split()
        
        v_array = np.array(v)
        v_equalized = HistogramProcessor._equalize_channel(v_array)
        
        v_eq = Image.fromarray(v_equalized.astype(np.uint8))
        result_hsv = Image.merge('HSV', (h, s, v_eq))
        
        return result_hsv.convert('RGB')

    @staticmethod
    def _equalize_channel(channel):
        hist, _ = np.histogram(channel.flatten(), 256, [0, 256])
        
        cdf = hist.cumsum()
        cdf_min = cdf[cdf > 0].min()
        
        cdf_normalized = ((cdf - cdf_min) * 255 / (cdf[-1] - cdf_min)).astype(np.uint8)
        
        equalized = cdf_normalized[channel.astype(np.uint8)]
        
        return equalized

    @staticmethod
    def linear_contrast_stretch(image, min_out=0, max_out=255):
        """Линейное контрастирование."""
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        img_array = np.array(image, dtype=np.float32)
        
        min_in = img_array.min()
        max_in = img_array.max()
        
        if max_in == min_in:
            return image
        
        stretched = (img_array - min_in) * (max_out - min_out) / (max_in - min_in) + min_out
        stretched = np.clip(stretched, 0, 255).astype(np.uint8)
        
        if len(img_array.shape) == 2:
            return Image.fromarray(stretched)
        else:
            return Image.fromarray(stretched)
