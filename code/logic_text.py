"""
Text Logic Module - Handles all Gemini API calls for prompt and caption generation.
"""

import os
import re
from dotenv import load_dotenv
import requests
import json
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL_NAME = os.getenv('GEMINI_MODEL_NAME', 'gemini-2.5-pro')
GEMINI_API_BASE = os.getenv('GEMINI_API_BASE', 'https://generativelanguage.googleapis.com/v1')


def _call_gemini(prompt: str) -> str:
    """
    Call the Gemini generateContent endpoint and return the response text.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    # DEBUG: show env & cwd
    print("DEBUG cwd:", os.getcwd())
    print("DEBUG GEMINI_MODEL_NAME:", os.getenv('GEMINI_MODEL_NAME'))
    print("DEBUG GEMINI_API_BASE:", os.getenv('GEMINI_API_BASE'))

    url = f"{GEMINI_API_BASE}/models/{GEMINI_MODEL_NAME}:generateContent"
    print("DEBUG generateContent URL ->", url)

    # DEBUG: call ListModels to see what's available from the API/key
    try:
        lm_resp = requests.get(f"{GEMINI_API_BASE}/models", params={"key": GEMINI_API_KEY}, timeout=10)
        print("DEBUG ListModels status:", lm_resp.status_code)
        try:
            print("DEBUG ListModels JSON (truncated):", json.dumps(lm_resp.json(), indent=2)[:2000])
        except Exception:
            print("DEBUG ListModels text:", lm_resp.text[:2000])
    except Exception as e:
        print("DEBUG ListModels error:", str(e))
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(
            url,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if "candidates" not in data or len(data["candidates"]) == 0:
            raise ValueError("No candidates returned from Gemini API")

        candidate = data["candidates"][0]
        parts = candidate.get("content", {}).get("parts", [])
        if not parts:
            raise ValueError("No content parts in Gemini response")

        return parts[0].get("text", "").strip()

    except requests.exceptions.HTTPError as http_err:
        raise RuntimeError(f"Gemini HTTP error: {http_err.response.status_code} {http_err.response.text}") from http_err
    except requests.exceptions.RequestException as req_err:
        raise RuntimeError(f"Gemini network error: {str(req_err)}") from req_err
    except Exception as err:
        raise RuntimeError(f"Gemini processing error: {str(err)}") from err


def generate_prompts(product_description: str, num_prompts: int = 5) -> list:
    """
    Generate visual prompts for Stable Diffusion based on product description.
    
    Args:
        product_description: Text description of the product
        num_prompts: Number of distinct prompts to generate (default: 5)
    
    Returns:
        List of image generation prompts for Stable Diffusion
    """
    try:
        prompt = f"""You are a creative director for advertising. Based on this product description: "{product_description}"

Generate {num_prompts} distinct, visually appealing background scene prompts for Stable Diffusion. Each prompt should:
1. Describe a unique environment/scene suitable for showcasing this product
2. Be vivid and detailed (e.g., "A sunlit modern kitchen with marble countertops and natural lighting")
3. NOT include the product itself or any text/logos
4. Focus on atmosphere, mood, and setting
5. Be suitable for placing a product image in the foreground

Return ONLY a numbered list of {num_prompts} prompts, one per line, without any additional text or explanation.
Example format:
1. A minimalist white studio with soft natural lighting
2. A vibrant urban street scene at golden hour
3. A luxurious spa setting with marble and plants
"""
        response_text = _call_gemini(prompt)

        if response_text:
            # Parse the response into a list of prompts
            prompts = []
            lines = response_text.strip().split('\n')
            
            for line in lines:
                cleaned = line.strip()
                if not cleaned:
                    continue
                
                # Remove numbering patterns (e.g., "1. ", "2.", "- ", "* ", etc.)
                cleaned = re.sub(r'^[\d\-\*\•]\s*\.?\s*', '', cleaned)
                
                # Remove markdown formatting if present
                cleaned = re.sub(r'^\*\*|^\*|^#+\s*', '', cleaned)
                
                if cleaned and len(cleaned) > 10:  # Minimum length check
                    prompts.append(cleaned.strip())
            
            # Ensure we have at least num_prompts
            if len(prompts) < num_prompts:
                # If we got fewer prompts, create variations
                base_prompts = prompts.copy() if prompts else [
                    f"A professional setting showcasing {product_description}",
                    f"A modern environment featuring {product_description}",
                    f"An elegant backdrop for {product_description}"
                ]
                while len(prompts) < num_prompts:
                    idx = len(prompts) % len(base_prompts)
                    variation = base_prompts[idx]
                    if len(prompts) >= len(base_prompts):
                        variation += f", variation {len(prompts) - len(base_prompts) + 1}"
                    prompts.append(variation)
            
            return prompts[:num_prompts]
        
        return []
    
    except Exception as e:
        print(f"Error generating prompts: {e}")
        # Fallback prompts
        return [
            f"A modern minimalist studio with soft lighting, perfect for showcasing {product_description}",
            f"A vibrant contemporary setting with natural elements, ideal for {product_description}",
            f"A luxurious elegant environment with sophisticated lighting, showcasing {product_description}",
            f"A dynamic urban backdrop with modern aesthetics, featuring {product_description}",
            f"A serene natural setting with professional lighting, highlighting {product_description}"
        ]


def generate_captions(product_description: str, num_captions: int = 5) -> list:
    """
    Generate marketing captions/ad copy for the product.
    
    Args:
        product_description: Text description of the product
        num_captions: Number of captions to generate (default: 5)
    
    Returns:
        List of marketing captions
    """
    try:
        prompt = f"""You are a professional copywriter. Based on this product description: "{product_description}"

Generate {num_captions} catchy, engaging marketing captions for social media ads. Each caption should:
1. Be concise (under 100 characters)
2. Be attention-grabbing and compelling
3. Include relevant hashtags (2-3 per caption)
4. Highlight key benefits or features
5. Be suitable for Instagram/Facebook ads

Return ONLY a numbered list of {num_captions} captions, one per line, without any additional text or explanation.
Example format:
1. Transform your space with premium quality! #PremiumDesign #HomeDecor
2. Elevate your lifestyle today. #ModernLiving #QualityFirst
3. Discover the difference. #Innovation #Style
"""
        response_text = _call_gemini(prompt)

        if response_text:
            # Parse the response into a list of captions
            captions = []
            lines = response_text.strip().split('\n')
            
            for line in lines:
                cleaned = line.strip()
                if not cleaned:
                    continue
                
                # Remove numbering patterns
                cleaned = re.sub(r'^[\d\-\*\•]\s*\.?\s*', '', cleaned)
                
                # Remove markdown formatting if present
                cleaned = re.sub(r'^\*\*|^\*|^#+\s*', '', cleaned)
                
                if cleaned and len(cleaned) > 5:  # Minimum length check
                    captions.append(cleaned.strip())
            
            # Ensure we have at least num_captions
            if len(captions) < num_captions:
                base_captions = captions.copy() if captions else [
                    f"Discover {product_description}! #Quality #Innovation",
                    f"Elevate your experience. {product_description} #Premium #Style"
                ]
                while len(captions) < num_captions:
                    idx = len(captions) % len(base_captions)
                    variation = base_captions[idx]
                    if len(captions) >= len(base_captions):
                        variation = variation.replace("#", "#New")  # Slight variation
                    captions.append(variation)
            
            return captions[:num_captions]
        
        return []
    
    except Exception as e:
        print(f"Error generating captions: {e}")
        # Fallback captions
        return [
            f"Discover {product_description}! #Quality #Innovation",
            f"Elevate your experience with {product_description}. #Premium #Style",
            f"Transform your world. {product_description} #Modern #Design",
            f"Experience the difference. {product_description} #Excellence #Luxury",
            f"Your new favorite. {product_description} #Trending #MustHave"
        ]

