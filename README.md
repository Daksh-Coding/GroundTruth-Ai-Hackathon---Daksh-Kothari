# H-003 | AI Creative Studio

> **Trend Line:** An "Auto-Creative Engine" that instantly generates high-quality, brand-consistent marketing assets using Generative AI composites.

---

## 1. Problem Statement & Description

**Context:** Businesses and marketing teams waste weeks and significant budget manually designing variations of the same marketing assets for different platforms and campaigns. Small teams often lack the design skills to create high-quality, diverse ad creatives rapidly.

**The Goal:** Design an "Auto-Creative Engine" to automatically generate multiple high-quality variations of brand creatives. The system needs to take raw brand assets and output a fully packaged campaign without human design intervention.

---

## 2. Expected End Result

A UI with these functionalities

**Input (What we give):**
* **Product Image:** A transparent PNG of the product.
* **Brand Logo:** A transparent PNG of the company logo.
* **Product Description:** A short text string describing the product (e.g., "A futuristic energy drink").

**Action: Wait a while, processing in background, approximately 1 min**

**Output (What we get):**
* **A Downloadable ZIP File containing:**
    * 3+ High-resolution marketing images (Product perfectly placed in AI-generated scenes).
> [!Note]
> Limited to 5 currently due to credit limits, but can be extended by small modifications in code, just by increasing 'for' loop limit. But remember to use a api key which have higher limits.
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
* **GenAI (Image):** Stability AI API (Stable Diffusion Medium)

---

## 5. Challenges & Learnings

**Challenge 1: Generative Hallucinations (The "Text Problem")**
* **Issue:** Initially, we tried asking the Image AI to "Generate a can of soda with the Brand X logo." The results were disastrous—the AI consistently misspelled the brand name and distorted the logo.
* **Solution:** We pivoted to a **Composite Architecture**. We treat the AI strictly as a "Background Generator" and use deterministic Python code (`Pillow`) to overlay the actual high-res product assets. This guarantees 100% brand accuracy.

**Challenge 2: Managing API Latency**
* **Issue:** Calling two different AI models (Gemini for text, Stability for images) sequentially caused the UI to freeze, making the app feel broken.
* **Solution:** We implemented Streamlit's `st.status` and progress bars to give the user real-time feedback on exactly which step (Brainstorming -> Rendering -> Compositing) was happening at any given second.

---

## 6. Visual Proof
Please Check the Screenshot and Output folder

---

## 7. How to Reproduce

Follow these steps to run the application locally:<br>
1. **Create a Virtual Environment:** I recommend doing so to avoid inconsistencies between different library versions. Use the command `conda create -n meet_env python=3.10.18` to create a virtual env and use `conda activate meet_env` to activate it.
2. **Clone the repository:** Use  `git clone _link_` to clone it to your local machine. Move to the repo's directory.
3. **Install all Dependencies:** Use `conda install -r requirements.txt` to install libraries. And set the .env file accordingly.
4. **Run the Streamlit App:** Use `Streamlit run app.py` to run the app.
