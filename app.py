import streamlit as st
from PIL import Image, ImageOps
import io

# Page config
st.set_page_config(page_title="Image Editor", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    body {
        background-color: #1f1f2e;
    }
    .stApp {
        background-color: #1f1f2e;
        color: white;
    }
    h2, h4 {
        text-align: center;
        color: white;
    }
    .original-title {
        font-size: 26px;
        color: lime;
        font-weight: bold;
        text-align: center;
    }
    .edited-title {
        font-size: 26px;
        color: pink;
        font-weight: bold;
        text-align: center;
    }
    .button-style button {
        background-color: #0d0d26;
        color: white;
        font-size: 16px;
        padding: 0.5em 2em;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 Image Comparison App")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Load the image
    image = Image.open(uploaded_file)

    # Edited image (grayscale)
    edited_image = ImageOps.grayscale(image)

    # Layout columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="original-title">🟢 Original</div>', unsafe_allow_html=True)
        st.image(image, caption="Original Image", use_container_width=True)

    with col2:
        st.markdown('<div class="edited-title">🎨 Edited</div>', unsafe_allow_html=True)
        st.image(edited_image, caption="Edited Image (Grayscale)", use_container_width=True)

    # Convert edited image to bytes
    img_bytes = io.BytesIO()
    edited_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Download button
    st.markdown('<div style="text-align:center;" class="button-style">', unsafe_allow_html=True)
    st.download_button(
        label="Download Edited Image",
        data=img_bytes,
        file_name="edited_image.png",
        mime="image/png"
    )
    st.markdown('</div>', unsafe_allow_html=True)
