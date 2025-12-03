
"""
Image Generation Module - Handles Stable Diffusion 3.5 Medium API calls for background generation.
Uses image-to-image mode for better control and quality.
"""

import requests
import os
import random
import base64
from typing import Tuple, Optional
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image, ImageDraw

load_dotenv()

STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
STABILITY_API_HOST = "https://api.stability.ai"


def _create_base_image(width: int = 1024, height: int = 1024) -> Image.Image:
    """
    Create a base gradient image to use as starting point for image-to-image generation.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
    
    Returns:
        PIL Image object with gradient background
    """
    # Create a gradient base image
    base = Image.new('RGB', (width, height), color=(240, 240, 245))
    draw = ImageDraw.Draw(base)
    
    # Create a subtle gradient effect
    for y in range(height):
        # Subtle gradient from light to slightly darker
        r = int(240 - (y / height) * 20)
        g = int(240 - (y / height) * 20)
        b = int(245 - (y / height) * 15)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return base


def generate_background(prompt: str, width: int = 1024, height: int = 1024, 
                       strength: float = 0.75) -> Tuple[Optional[Image.Image], Optional[str]]:
    """
    Generate a background image using Stable Diffusion 3.5 Medium with image-to-image mode.
    
    Args:
        prompt: Text prompt describing the desired background scene
        width: Image width in pixels (default: 1024)
        height: Image height in pixels (default: 1024)
        strength: Controls how much influence the base image has (0.0-1.0, default: 0.75)
                  Lower values = more influence from prompt, higher = more from base image
    
    Returns:
        Tuple of (PIL Image object of the generated background, error_message)
        Returns (None, error_message) if generation fails
        Returns (Image, None) if successful
    """
    if not STABILITY_API_KEY:
        return None, "STABILITY_API_KEY not found in environment variables"
    
    try:
        # Create base image for image-to-image
        base_image = _create_base_image(width, height)
        
        # Convert base image to bytes for upload
        img_buffer = BytesIO()
        base_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Use Stable Diffusion 3.5 Medium with image-to-image mode
        url = f"{STABILITY_API_HOST}/v1/generation/image-to-image"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {STABILITY_API_KEY}"
        }
        
        # Prepare multipart form data
        files = {
            'image': ('base.png', img_buffer, 'image/png'),
        }
        
        data = {
            'prompt': prompt,
            'mode': 'image-to-image',
            'model': 'SD 3.5 Medium',
            'strength': str(strength),
            'seed': str(random.randint(0, 4294967295)),
            'negative_prompt': 'blurry, low quality, distorted, watermark, text, logo, product, person, human',
            'cfg_scale': '7',
            'output_format': 'png'
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract base64 image from response
            if 'artifacts' in result and len(result['artifacts']) > 0:
                image_data = result['artifacts'][0]['base64']
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
                return image, None
            else:
                return None, "No artifacts in API response"
        
        elif response.status_code == 402:
            # Payment required / credits exhausted
            return None, "Stable Diffusion 3.5 Medium model is not accessible. Your credits may have ended. Please check your Stability AI account balance."
        
        elif response.status_code == 401:
            return None, "Invalid API key. Please check your STABILITY_API_KEY in the .env file."
        
        elif response.status_code == 429:
            return None, "Rate limit exceeded. Please wait a moment and try again."
        
        else:
            error_text = response.text
            try:
                error_json = response.json()
                if 'message' in error_json:
                    error_text = error_json['message']
            except:
                pass
            return None, f"API Error ({response.status_code}): {error_text}"
    
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"
    except Exception as e:
        return None, f"Error generating background: {str(e)}"

