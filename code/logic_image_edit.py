"""
Image Processing Module - Handles image compositing using Pillow.
"""

from PIL import Image, ImageEnhance
import os


def create_composite(background: Image.Image, product: Image.Image, logo: Image.Image, 
                    product_size_ratio: float = 0.4, logo_size_ratio: float = 0.15) -> Image.Image:
    """
    Composite product and logo onto the AI-generated background.
    
    Args:
        background: PIL Image of the generated background
        product: PIL Image of the product (should have transparent background)
        logo: PIL Image of the logo (should have transparent background)
        product_size_ratio: Ratio of product height to background height (default: 0.4 = 40%)
        logo_size_ratio: Ratio of logo width to background width (default: 0.15 = 15%)
    
    Returns:
        PIL Image of the final composite
    """
    # Convert background to RGBA if needed
    if background.mode != 'RGBA':
        background = background.convert('RGBA')
    
    # Create a copy of the background to work with
    composite = background.copy()
    
    # Process product image
    product = _prepare_image(product, 'RGBA')
    
    # Calculate product dimensions (maintain aspect ratio)
    bg_width, bg_height = composite.size
    product_target_height = int(bg_height * product_size_ratio)
    
    # Resize product maintaining aspect ratio
    product_aspect = product.width / product.height
    product_target_width = int(product_target_height * product_aspect)
    
    # Ensure product doesn't exceed background width
    if product_target_width > bg_width * 0.9:
        product_target_width = int(bg_width * 0.9)
        product_target_height = int(product_target_width / product_aspect)
    
    product_resized = product.resize((product_target_width, product_target_height), Image.Resampling.LANCZOS)
    
    # Position product at center-bottom
    product_x = (bg_width - product_target_width) // 2
    product_y = bg_height - product_target_height - int(bg_height * 0.05)  # 5% margin from bottom
    
    # Paste product onto background with alpha blending
    composite = _paste_with_alpha(composite, product_resized, (product_x, product_y))
    
    # Process logo image
    logo = _prepare_image(logo, 'RGBA')
    
    # Calculate logo dimensions (maintain aspect ratio)
    logo_target_width = int(bg_width * logo_size_ratio)
    logo_aspect = logo.width / logo.height
    logo_target_height = int(logo_target_width / logo_aspect)
    
    logo_resized = logo.resize((logo_target_width, logo_target_height), Image.Resampling.LANCZOS)
    
    # Position logo at top-right with margin
    logo_margin = int(bg_width * 0.02)  # 2% margin
    logo_x = bg_width - logo_target_width - logo_margin
    logo_y = logo_margin
    
    # Paste logo onto background with alpha blending
    composite = _paste_with_alpha(composite, logo_resized, (logo_x, logo_y))
    
    return composite


def _prepare_image(image: Image.Image, mode: str = 'RGBA') -> Image.Image:
    """
    Prepare an image for compositing by ensuring it's in the correct mode.
    
    Args:
        image: PIL Image to prepare
        mode: Target color mode (default: 'RGBA')
    
    Returns:
        Prepared PIL Image
    """
    if image.mode != mode:
        if mode == 'RGBA' and image.mode == 'RGB':
            # Convert RGB to RGBA
            image = image.convert('RGBA')
        else:
            image = image.convert(mode)
    
    return image


def _paste_with_alpha(base: Image.Image, overlay: Image.Image, position: tuple) -> Image.Image:
    """
    Paste an image with alpha transparency onto a base image.
    
    Args:
        base: Base PIL Image
        overlay: Overlay PIL Image with alpha channel
        position: (x, y) tuple for paste position
    
    Returns:
        Composite PIL Image
    """
    # Create a temporary image for alpha compositing
    temp = Image.new('RGBA', base.size, (0, 0, 0, 0))
    temp.paste(overlay, position, overlay)
    
    # Composite onto base
    result = Image.alpha_composite(base, temp)
    return result


def enhance_image(image: Image.Image, brightness: float = 1.0, contrast: float = 1.0) -> Image.Image:
    """
    Enhance image brightness and contrast (optional utility function).
    
    Args:
        image: PIL Image to enhance
        brightness: Brightness multiplier (1.0 = no change)
        contrast: Contrast multiplier (1.0 = no change)
    
    Returns:
        Enhanced PIL Image
    """
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)
    
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
    
    return image

