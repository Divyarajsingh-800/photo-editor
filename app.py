import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from io import BytesIO

st.set_page_config(page_title="Photo Editor and Comparison", layout="centered")

st.markdown(
    """
    <style>
    body {
        background: radial-gradient(circle at top, #0f0c29, #302b63, #24243e);
    }
    .stApp {
        background: radial-gradient(circle at top, #0f0c29, #302b63, #24243e);
        color: white;
        text-align: center;
    }
    h1 {
        text-shadow: 0 0 15px #0ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📸 Photo Editor and Comparison")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    original = np.array(image)

    # Sidebar controls
    st.sidebar.header("🎛️ Filters and Adjustments")

    filter_type = st.sidebar.radio("Apply Filter", ["None", "Blur", "Sharpen", "Invert", "Grayscale"])

    brightness = st.sidebar.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
    contrast = st.sidebar.slider("Contrast", 0.5, 2.0, 1.0, 0.1)
    opacity = st.sidebar.slider("Opacity", 0.0, 1.0, 1.0, 0.05)

    # Convert to OpenCV format
    img = np.array(image).astype(np.uint8)

    if filter_type == "Grayscale":
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    elif filter_type == "Invert":
        img = cv2.bitwise_not(img)

    elif filter_type == "Blur":
        img = cv2.GaussianBlur(img, (7, 7), 0)

    elif filter_type == "Sharpen":
        kernel = np.array([[0, -1, 0],
                           [-1, 5,-1],
                           [0, -1, 0]])
        img = cv2.filter2D(img, -1, kernel)

    # PIL Enhancements
    edited = Image.fromarray(img)
    edited = ImageEnhance.Brightness(edited).enhance(brightness)
    edited = ImageEnhance.Contrast(edited).enhance(contrast)

    # Apply opacity
    if opacity < 1.0:
        background = Image.new("RGB", edited.size, (0, 0, 0))
        edited = Image.blend(background, edited, opacity)

    # Columns to display side-by-side
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🟢 Original")
        st.image(image, use_column_width=True)
    with col2:
        st.subheader("🎨 Edited")
        st.image(edited, use_column_width=True)

    # Download button
    buffer = BytesIO()
    edited.save(buffer, format="PNG")
    st.download_button("Download Edited Image", data=buffer.getvalue(),
                       file_name="edited_image.png", mime="image/png")
