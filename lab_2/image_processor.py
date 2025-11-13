from PIL import Image
from histogram import HistogramProcessor
from segmentation import SegmentationProcessor

class ImageProcessor:
    def __init__(self):
        self.histogram_processor = HistogramProcessor()
        self.segmentation_processor = SegmentationProcessor()
    
    def process_histogram_equalize_rgb(self, image):
        return self.histogram_processor.equalize_histogram_rgb(image)
    
    def process_histogram_equalize_hsv(self, image):
        return self.histogram_processor.equalize_histogram_hsv(image)
    
    def process_linear_contrast(self, image):
        return self.histogram_processor.linear_contrast_stretch(image)
    
    def process_point_detection(self, image, threshold=50):
        return self.segmentation_processor.point_detection(image, threshold)
    
    def process_line_detection(self, image, direction='horizontal', threshold=100):
        return self.segmentation_processor.line_detection(image, direction, threshold)
    
    def process_edge_detection(self, image, method='sobel', threshold=100):
        return self.segmentation_processor.edge_detection(image, method, threshold)
    
    def process_combined_edges(self, image, threshold=100):
        return self.segmentation_processor.combined_edge_detection(image, threshold)
    
    def get_histogram(self, image, downsample_for_display=False):
        return self.histogram_processor.compute_histogram(image, downsample_for_display)
