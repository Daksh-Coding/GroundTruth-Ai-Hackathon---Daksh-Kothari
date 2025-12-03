# H-003 | AI Creative Studio

> **Trend Line:** An "Auto-Creative Engine" that instantly generates high-quality, brand-consistent marketing assets using Generative AI composites.

---

## 1. Problem Statement & Description

**Context:** Businesses and marketing teams waste weeks and significant budget manually designing variations of the same marketing assets for different platforms and campaigns. Small teams often lack the design skills to create high-quality, diverse ad creatives rapidly.

**The Goal:** Design an "Auto-Creative Engine" to automatically generate multiple high-quality variations of brand creatives. The system needs to take raw brand assets and output a fully packaged campaign without human design intervention.

---

## 2. Input & Output

**Input (What we give):**
* **Product Image:** A transparent PNG of the product.
* **Brand Logo:** A transparent PNG of the company logo.
* **Product Description:** A short text string describing the product (e.g., "A futuristic energy drink").

**Output (What we get):**
* **A Downloadable ZIP File containing:**
    * 3+ High-resolution marketing images (Product perfectly placed in AI-generated scenes).
    * A text file containing matching AI-generated ad copy (Captions & Hashtags).

---

## 3. Approach & Solution

We moved beyond simple "text-to-image" generation, which often hallucinates logos or distorts products. Instead, we built a **Composite AI Pipeline**:

1.  **Ideation:** We use an LLM (Gemini) to brainstorm distinct visual settings based on the product description.
2.  **Scene Generation:** We use Stable Diffusion to generate high-quality background scenes *without* the product.
3.  **Smart Compositing:** Using Python's image processing capabilities, we programmatically resize and overlay the user's *actual* product image and logo onto the AI background. This ensures the product looks 100% real.
4.  **Copywriting:** The LLM generates relevant captions that match the visual mood of the generated scenes.

---

## 4. Tech Stack

* **Language:** Python (Version 3.10+)
* **Frontend:** Streamlit
* **Image Processing:** Pillow (PIL)
* **GenAI (Text):** Google Gemini API
* **GenAI (Image):** Stability AI API (Stable Diffusion)

---

## 5. How to Reproduce

Follow these steps to run the application locally:

**Step 1: Clone the Repository**
```bash
git clone [https://github.com/your-username/ai-creative-studio.git](https://github.com/your-username/ai-creative-studio.git)
cd ai-creative-studio
