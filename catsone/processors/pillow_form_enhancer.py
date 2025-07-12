#!/usr/bin/env python3
"""
Advanced Pillow-based form enhancement for better checkbox and radio button detection
"""

import os
import logging
from typing import Dict, Tuple, Optional
from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageDraw
import numpy as np

logger = logging.getLogger(__name__)

class PillowFormEnhancer:
    """Enhance form images to improve checkbox and radio button detection"""
    
    def __init__(self):
        # Threshold values tuned for Dayforce forms
        self.checkbox_threshold = 180
        self.radio_threshold = 200
        self.edge_threshold = 128
        
    def enhance_for_checkboxes(self, image: Image.Image) -> Tuple[Image.Image, Image.Image]:
        """Enhance image specifically for checkbox detection"""
        
        # Convert to grayscale
        gray = ImageOps.grayscale(image)
        
        # Apply threshold to make checkmarks stand out
        # Checkmarks are usually dark, so we want to make them black (0)
        binary = gray.point(lambda x: 0 if x < self.checkbox_threshold else 255, 'L')
        
        # Find edges to highlight checkbox boundaries
        edges = binary.filter(ImageFilter.FIND_EDGES)
        
        # Enhance the edges
        edge_enhancer = ImageEnhance.Contrast(edges)
        enhanced_edges = edge_enhancer.enhance(2.0)
        
        logger.info("Enhanced image for checkbox detection")
        return binary, enhanced_edges
    
    def enhance_for_radio_buttons(self, image: Image.Image) -> Image.Image:
        """Enhance image specifically for radio button detection"""
        
        # Radio buttons often have subtle fills, so we need aggressive enhancement
        # First, increase contrast dramatically
        enhancer = ImageEnhance.Contrast(image)
        high_contrast = enhancer.enhance(3.0)
        
        # Convert to grayscale
        gray = ImageOps.grayscale(high_contrast)
        
        # Apply adaptive thresholding for radio buttons
        # Radio button fills are often lighter than checkmarks
        binary = gray.point(lambda x: 0 if x < self.radio_threshold else 255, 'L')
        
        # Apply morphological operations to connect dots in radio buttons
        # This helps when the fill is slightly broken
        binary_array = np.array(binary)
        
        # Simple dilation to connect nearby pixels
        from scipy import ndimage
        dilated = ndimage.binary_dilation(binary_array == 0, iterations=1)
        result = Image.fromarray((~dilated * 255).astype(np.uint8))
        
        logger.info("Enhanced image for radio button detection")
        return result
    
    def combined_enhancement(self, image: Image.Image) -> Image.Image:
        """Apply combined enhancements for general form detection"""
        
        # Start with contrast enhancement
        contrast = ImageEnhance.Contrast(image)
        enhanced = contrast.enhance(2.0)
        
        # Sharpen
        sharpness = ImageEnhance.Sharpness(enhanced)
        enhanced = sharpness.enhance(2.5)
        
        # Convert to grayscale
        gray = ImageOps.grayscale(enhanced)
        
        # Apply edge detection
        edges = gray.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        # Combine original and edges
        blended = Image.blend(gray, edges, 0.3)
        
        logger.info("Applied combined enhancement")
        return blended
    
    def detect_form_regions(self, image: Image.Image) -> Dict[str, list]:
        """Detect regions that likely contain checkboxes or radio buttons"""
        
        # Convert to grayscale
        gray = ImageOps.grayscale(image)
        
        # Apply edge detection
        edges = gray.filter(ImageFilter.FIND_EDGES)
        
        # Look for rectangular (checkbox) and circular (radio) patterns
        # This is a simplified version - could be enhanced with OpenCV
        regions = {
            'checkbox_regions': [],
            'radio_regions': []
        }
        
        # For now, we'll process the entire image
        # In a more advanced version, we could use contour detection
        # to identify specific regions
        
        return regions
    
    def create_enhanced_versions(self, image_path: str) -> Dict[str, Image.Image]:
        """Create multiple enhanced versions of the image"""
        
        try:
            # Load image
            img = Image.open(image_path)
            
            # Create multiple enhanced versions
            checkbox_binary, checkbox_edges = self.enhance_for_checkboxes(img)
            
            versions = {
                'original': img,
                'checkbox_binary': checkbox_binary,
                'checkbox_edges': checkbox_edges,
                'radio_enhanced': self.enhance_for_radio_buttons(img),
                'combined': self.combined_enhancement(img),
                'high_contrast': self._high_contrast_version(img),
                'inverted': self._inverted_version(img)
            }
            
            logger.info(f"Created {len(versions)} enhanced versions of {image_path}")
            return versions
            
        except Exception as e:
            logger.error(f"Error creating enhanced versions: {e}")
            return {'original': Image.open(image_path)}
    
    def _high_contrast_version(self, image: Image.Image) -> Image.Image:
        """Create ultra-high contrast version"""
        
        # Convert to grayscale
        gray = ImageOps.grayscale(image)
        
        # Apply extreme contrast
        enhancer = ImageEnhance.Contrast(gray)
        high_contrast = enhancer.enhance(5.0)
        
        # Binary threshold
        threshold = 150
        binary = high_contrast.point(lambda x: 0 if x < threshold else 255, 'L')
        
        return binary
    
    def _inverted_version(self, image: Image.Image) -> Image.Image:
        """Create inverted version (sometimes helps with light fills)"""
        
        # Convert to grayscale
        gray = ImageOps.grayscale(image)
        
        # Invert
        inverted = ImageOps.invert(gray)
        
        # Enhance contrast on inverted image
        enhancer = ImageEnhance.Contrast(inverted)
        enhanced = enhancer.enhance(2.0)
        
        return enhanced
    
    def save_enhanced_versions(self, image_path: str, output_dir: str) -> Dict[str, str]:
        """Save all enhanced versions to disk"""
        
        versions = self.create_enhanced_versions(image_path)
        saved_paths = {}
        
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Get base filename
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Save each version
        for version_name, img in versions.items():
            output_path = os.path.join(output_dir, f"{base_name}_{version_name}.png")
            img.save(output_path, 'PNG', quality=100)
            saved_paths[version_name] = output_path
            logger.info(f"Saved {version_name} version to {output_path}")
        
        return saved_paths
    
    def analyze_fill_patterns(self, image: Image.Image, region: Tuple[int, int, int, int]) -> Dict[str, float]:
        """Analyze a region to determine if it contains a fill pattern"""
        
        # Crop to region
        cropped = image.crop(region)
        
        # Convert to grayscale
        gray = ImageOps.grayscale(cropped)
        
        # Calculate statistics
        pixels = list(gray.getdata())
        avg_brightness = sum(pixels) / len(pixels)
        
        # Count dark pixels (potential fill)
        dark_pixels = sum(1 for p in pixels if p < 128)
        fill_ratio = dark_pixels / len(pixels)
        
        # Check for patterns
        has_center_fill = self._check_center_fill(gray)
        
        return {
            'avg_brightness': avg_brightness,
            'fill_ratio': fill_ratio,
            'has_center_fill': has_center_fill,
            'likely_selected': fill_ratio > 0.2 or has_center_fill
        }
    
    def _check_center_fill(self, image: Image.Image) -> bool:
        """Check if the center of the image is filled (for radio buttons)"""
        
        width, height = image.size
        center_x, center_y = width // 2, height // 2
        
        # Sample center region
        center_region = image.crop((
            center_x - width // 4,
            center_y - height // 4,
            center_x + width // 4,
            center_y + height // 4
        ))
        
        # Check if center is dark
        pixels = list(center_region.getdata())
        avg = sum(pixels) / len(pixels) if pixels else 255
        
        return avg < 128  # Dark center indicates filled radio button


def test_enhancer():
    """Test the enhancer with a sample image"""
    
    enhancer = PillowFormEnhancer()
    
    # Test with a sample questionnaire page
    test_image = "/tmp/questionnaire_debug/page_1.png"
    
    if os.path.exists(test_image):
        output_dir = "/tmp/enhanced_questionnaires"
        saved = enhancer.save_enhanced_versions(test_image, output_dir)
        
        print(f"Saved enhanced versions to {output_dir}")
        for version, path in saved.items():
            print(f"  - {version}: {path}")
    else:
        print(f"Test image not found: {test_image}")


if __name__ == "__main__":
    test_enhancer()