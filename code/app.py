import streamlit as st
import zipfile
from io import BytesIO
from PIL import Image
import os
import time

from logic_text import generate_prompts, generate_captions
from logic_image_gen import generate_background
from logic_image_edit import create_composite

# Page configuration
st.set_page_config(
    page_title="AI Creative Studio",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🎨 AI Creative Studio</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Auto-Creative Engine | Generate Multiple Ad Variations Instantly</p>', unsafe_allow_html=True)

# Sidebar for inputs
st.sidebar.header("📤 Upload Assets")

# File uploaders
product_image_file = st.sidebar.file_uploader(
    "Product Image (PNG with transparent background)",
    type=['png', 'jpg', 'jpeg'],
    help="Upload your product image. PNG with transparent background works best."
)

logo_image_file = st.sidebar.file_uploader(
    "Logo Image (PNG with transparent background)",
    type=['png', 'jpg', 'jpeg'],
    help="Upload your brand logo. PNG with transparent background works best."
)

# Product description input
product_description = st.sidebar.text_area(
    "Product Description",
    height=100,
    help="Describe your product. This will be used to generate backgrounds and captions.",
    placeholder="e.g., Premium wireless headphones with noise cancellation..."
)

# Number of variations slider
num_variations = st.sidebar.slider(
    "Number of Variations",
    min_value=5,
    max_value=10,
    value=5,
    help="Generate 5-10 unique ad variations"
)

# Generate button
generate_button = st.sidebar.button("🚀 Generate Campaign", type="primary")

# Main content area
if generate_button:
    # Validation
    if not product_image_file:
        st.sidebar.error("❌ Please upload a product image")
        st.stop()
    
    if not logo_image_file:
        st.sidebar.error("❌ Please upload a logo image")
        st.stop()
    
    if not product_description or len(product_description.strip()) < 10:
        st.sidebar.error("❌ Please provide a detailed product description (at least 10 characters)")
        st.stop()
    
    # Check API keys
    if not os.getenv('GEMINI_API_KEY'):
        st.sidebar.error("❌ GEMINI_API_KEY not found. Please set it in your .env file")
        st.stop()
    
    if not os.getenv('STABILITY_API_KEY'):
        st.sidebar.error("❌ STABILITY_API_KEY not found. Please set it in your .env file")
        st.stop()
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Load images
        status_text.text("📥 Loading images...")
        progress_bar.progress(10)
        
        product_image = Image.open(product_image_file)
        logo_image = Image.open(logo_image_file)
        
        # Ensure images have alpha channel
        if product_image.mode != 'RGBA':
            product_image = product_image.convert('RGBA')
        if logo_image.mode != 'RGBA':
            logo_image = logo_image.convert('RGBA')
        
        # Step 1: Generate prompts
        status_text.text("🤖 Generating creative prompts with AI...")
        progress_bar.progress(20)
        
        prompts = generate_prompts(product_description, num_prompts=num_variations)
        
        if not prompts:
            st.error("Failed to generate prompts. Please try again.")
            st.stop()
        
        # Step 2: Generate captions
        status_text.text("✍️ Generating ad captions...")
        progress_bar.progress(30)
        
        captions = generate_captions(product_description, num_captions=num_variations)
        
        if not captions:
            st.error("Failed to generate captions. Please try again.")
            st.stop()
        
        # Step 3: Generate backgrounds and create composites
        status_text.text("🎨 Generating backgrounds and creating composites...")
        progress_bar.progress(40)
        
        composites = []
        failed_generations = []
        
        for i, prompt in enumerate(prompts):
            try:
                # Update progress
                progress = 40 + int((i / len(prompts)) * 50)
                progress_bar.progress(progress)
                status_text.text(f"🎨 Generating variation {i+1}/{len(prompts)}...")
                
                # Generate background
                background, error_message = generate_background(prompt, width=1024, height=1024)
                
                if background is None:
                    failed_generations.append(i + 1)
                    if error_message:
                        # Check if it's a credits error
                        if "credits" in error_message.lower() or "not accessible" in error_message.lower():
                            st.error(f"❌ {error_message}")
                            st.stop()
                        else:
                            st.warning(f"⚠️ Variation {i+1}: {error_message}")
                    else:
                        st.warning(f"⚠️ Failed to generate background for variation {i+1}. Skipping...")
                    continue
                
                # Create composite
                composite = create_composite(background, product_image, logo_image)
                
                # Store composite with caption
                composites.append({
                    'image': composite,
                    'caption': captions[i] if i < len(captions) else captions[-1],
                    'variation_num': i + 1
                })
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
            
            except Exception as e:
                st.warning(f"⚠️ Error generating variation {i+1}: {str(e)}")
                failed_generations.append(i + 1)
                continue
        
        progress_bar.progress(100)
        status_text.text("✅ Generation complete!")
        
        if not composites:
            st.error("❌ Failed to generate any variations. Please check your API keys and try again.")
            st.stop()
        
        # Display results
        st.success(f"✅ Successfully generated {len(composites)} ad variations!")
        
        if failed_generations:
            st.warning(f"⚠️ Note: {len(failed_generations)} variation(s) failed to generate: {failed_generations}")
        
        # Display images in a grid
        st.header("📸 Generated Ad Variations")
        
        cols_per_row = 2
        for idx in range(0, len(composites), cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx, col in enumerate(cols):
                if idx + col_idx < len(composites):
                    composite_data = composites[idx + col_idx]
                    with col:
                        st.image(
                            composite_data['image'],
                            caption=f"Variation {composite_data['variation_num']}: {composite_data['caption'][:50]}...",
                            use_container_width=True
                        )
                        st.caption(composite_data['caption'])
        
        # Create ZIP file for download
        status_text.text("📦 Packaging files for download...")
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add images
            for composite_data in composites:
                img_buffer = BytesIO()
                composite_data['image'].save(img_buffer, format='PNG', quality=95)
                zip_file.writestr(
                    f"ad_variation_{composite_data['variation_num']}.png",
                    img_buffer.getvalue()
                )
            
            # Add captions file
            captions_text = "\n\n".join([
                f"Variation {comp['variation_num']}:\n{comp['caption']}"
                for comp in composites
            ])
            zip_file.writestr("captions.txt", captions_text.encode('utf-8'))
        
        zip_buffer.seek(0)
        
        # Download button
        st.download_button(
            label=f"📥 Download All Variations ({len(composites)} images + captions)",
            data=zip_buffer.getvalue(),
            file_name="ad_creatives.zip",
            mime="application/zip",
            type="primary"
        )
        
        status_text.empty()
        progress_bar.empty()
    
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.exception(e)

else:
    # Show instructions when not generating
    st.info("👈 **Get Started:** Upload your product image, logo, and enter a product description in the sidebar, then click 'Generate Campaign'.")
    
    st.markdown("""
    ### How It Works:
    
    1. **Upload Assets**: Upload your product image (PNG with transparent background) and logo
    2. **Describe Product**: Enter a detailed description of your product
    3. **Generate**: Click the button and watch AI create multiple ad variations
    4. **Download**: Get all variations in a ZIP file with high-resolution images and captions
    
    ### Features:
    - ✨ AI-generated backgrounds using Stable Diffusion
    - 🎨 Automatic product compositing
    - 📝 AI-generated marketing captions
    - 📦 Download-ready ZIP package
    - 🚀 Fast parallel processing
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**H-003: AI Creative Studio**")
st.sidebar.markdown("Track: Generative AI & Marketing Tech")

