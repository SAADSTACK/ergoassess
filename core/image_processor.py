"""
Image Processor - Preprocessing pipeline for pose detection

Handles image loading, validation, normalization, and enhancement
for optimal pose detection accuracy.
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from PIL import Image
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import IMAGE_PROCESSING


class ImageProcessor:
    """
    Image preprocessing pipeline for ergonomic analysis.
    
    Ensures consistent image format and quality for reliable
    pose detection across different input sources.
    """
    
    SUPPORTED_FORMATS = {'JPEG', 'JPG', 'PNG', 'BMP', 'WEBP'}
    
    def __init__(self):
        """Initialize image processor with configured settings."""
        self.max_width = IMAGE_PROCESSING['max_width']
        self.max_height = IMAGE_PROCESSING['max_height']
        self.normalize_lighting = IMAGE_PROCESSING['normalize_lighting']
        self.enhance_contrast = IMAGE_PROCESSING['enhance_contrast']
    
    def load_image(self, source) -> np.ndarray:
        """
        Load image from various sources.
        
        Args:
            source: File path (str), file-like object, or bytes
            
        Returns:
            Image as RGB numpy array
        """
        if isinstance(source, str):
            # Load from file path
            image = cv2.imread(source)
            if image is None:
                raise ValueError(f"Could not load image from path: {source}")
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        elif isinstance(source, bytes):
            # Load from bytes
            nparr = np.frombuffer(source, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Could not decode image from bytes")
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        elif hasattr(source, 'read'):
            # Load from file-like object
            content = source.read()
            if isinstance(content, str):
                content = content.encode()
            nparr = np.frombuffer(content, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Could not decode image from file object")
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        elif isinstance(source, np.ndarray):
            # Already a numpy array
            image = source.copy()
            # Check if BGR and convert
            if len(image.shape) == 3 and image.shape[2] == 3:
                # Assume BGR if from OpenCV
                pass  # Keep as is, assume RGB
        
        else:
            raise TypeError(f"Unsupported image source type: {type(source)}")
        
        return image
    
    def validate_format(self, image: np.ndarray) -> bool:
        """
        Validate image format is suitable for processing.
        
        Args:
            image: Image as numpy array
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(image, np.ndarray):
            return False
        
        if len(image.shape) != 3:
            return False
        
        if image.shape[2] != 3:
            return False
        
        if image.dtype != np.uint8:
            return False
        
        return True
    
    def resize_if_needed(self, image: np.ndarray) -> np.ndarray:
        """
        Resize image if it exceeds maximum dimensions.
        
        Maintains aspect ratio while fitting within max dimensions.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Resized image (or original if no resize needed)
        """
        height, width = image.shape[:2]
        
        if width <= self.max_width and height <= self.max_height:
            return image
        
        # Calculate scaling factor
        scale_w = self.max_width / width
        scale_h = self.max_height / height
        scale = min(scale_w, scale_h)
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return resized
    
    def normalize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Apply lighting normalization using CLAHE.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Normalized image
        """
        if not self.normalize_lighting:
            return image
        
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # Convert back to RGB
        normalized = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        return normalized
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """
        Apply contrast enhancement.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Enhanced image
        """
        if not self.enhance_contrast:
            return image
        
        # Simple contrast enhancement
        alpha = 1.1  # Contrast control
        beta = 5      # Brightness control
        
        enhanced = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return enhanced
    
    def preprocess(self, source) -> np.ndarray:
        """
        Complete preprocessing pipeline.
        
        Args:
            source: Image source (path, bytes, file object, or array)
            
        Returns:
            Preprocessed RGB image ready for pose detection
        """
        # Load image
        image = self.load_image(source)
        
        # Validate format
        if not self.validate_format(image):
            raise ValueError("Invalid image format after loading")
        
        # Resize if needed
        image = self.resize_if_needed(image)
        
        # Apply normalization
        image = self.normalize_image(image)
        
        # Apply enhancement
        image = self.enhance_image(image)
        
        return image
    
    def get_image_info(self, image: np.ndarray) -> dict:
        """
        Get information about an image.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Dictionary with image information
        """
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        
        return {
            'width': width,
            'height': height,
            'channels': channels,
            'dtype': str(image.dtype),
            'size_bytes': image.nbytes,
            'aspect_ratio': round(width / height, 2)
        }
    
    def to_base64(self, image: np.ndarray, format: str = 'JPEG') -> str:
        """
        Convert image to base64 string for web display.
        
        Args:
            image: RGB image as numpy array
            format: Output format ('JPEG' or 'PNG')
            
        Returns:
            Base64 encoded string
        """
        import base64
        
        # Convert RGB to BGR for OpenCV encoding
        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Encode to bytes
        if format.upper() == 'PNG':
            _, buffer = cv2.imencode('.png', bgr_image)
        else:
            _, buffer = cv2.imencode('.jpg', bgr_image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        
        # Convert to base64
        b64_string = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/{format.lower()};base64,{b64_string}"
    
    @staticmethod
    def draw_text_with_background(
        image: np.ndarray,
        text: str,
        position: Tuple[int, int],
        font_scale: float = 0.6,
        color: Tuple[int, int, int] = (255, 255, 255),
        bg_color: Tuple[int, int, int] = (0, 0, 0)
    ) -> np.ndarray:
        """
        Draw text with a background rectangle for visibility.
        
        Args:
            image: Image as numpy array
            text: Text to draw
            position: (x, y) position for text
            font_scale: Font scale factor
            color: Text color (RGB)
            bg_color: Background color (RGB)
            
        Returns:
            Image with text drawn
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 2
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Draw background rectangle
        x, y = position
        padding = 5
        cv2.rectangle(
            image,
            (x - padding, y - text_height - padding),
            (x + text_width + padding, y + baseline + padding),
            bg_color,
            -1
        )
        
        # Draw text
        cv2.putText(image, text, position, font, font_scale, color, thickness)
        
        return image
