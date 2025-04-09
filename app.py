import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
import cv2
import numpy as np
from io import BytesIO

st.set_page_config(layout="centered", page_title="Photo Editor")
st.title("📸 Photo Editor and Comparison")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    original_img = img.copy()
    st.image(original_img, caption="Original Image", use_column_width=True)

    filter_type = st.selectbox("Choose a Filter", ["None", "Blur", "Sharpen", "Grayscale", "Invert"])
    brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
    contrast = st.slider("Contrast", 0.5, 2.0, 1.0, 0.1)
    opacity = st.slider("Opacity", 0.0, 1.0, 1.0, 0.05)

    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)

    img_np = np.array(img)

    if filter_type == "Grayscale":
        img = ImageOps.grayscale(img).convert("RGB")
    elif filter_type == "Invert":
        img = ImageOps.invert(img)
    elif filter_type == "Blur":
        img_np = cv2.GaussianBlur(img_np, (5, 5), 0)
        img = Image.fromarray(img_np)
    elif filter_type == "Sharpen":
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        img_np = cv2.filter2D(img_np, -1, kernel)
        img = Image.fromarray(img_np)

    if opacity < 1.0:
        transparent = Image.new("RGB", img.size, (0, 0, 0))
        img = Image.blend(transparent, img, opacity)

    st.image(img, caption="Filtered Image", use_column_width=True)

    if st.checkbox("Show Original"):
        st.image(original_img, caption="Original Image", use_column_width=True)

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    st.download_button("Download Edited Image", buffered.getvalue(), file_name="edited_image.png", mime="image/png")
