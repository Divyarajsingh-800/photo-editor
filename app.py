import streamlit as st
from PIL import Image
import numpy as np
import cv2
import os
import base64

def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_string.decode()}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local('C:/Users/Dell/Downloads/202308244_163009.jpg')  # Change to your own image path

st.title("🖼️ Photo Editor")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Original Image", use_column_width=True)

    filter_type = st.sidebar.selectbox("Choose a filter", [
        "None", "Grayscale", "Blur", "Sharpen", "Invert",
        "Sepia", "Vintage", "Cool", "Warm", "Polaroid"
    ])

    # Convert PIL image to OpenCV format
    img = np.array(image).astype(np.uint8)

    def blend(original_img, filtered_img, alpha):
        return cv2.addWeighted(original_img, 1 - alpha, filtered_img, alpha, 0)

    if filter_type == "Grayscale":
        alpha = st.sidebar.slider("Filter Strength", 0.0, 1.0, 1.0, 0.05)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        img = blend(img, gray_rgb, alpha)

    elif filter_type == "Blur":
        blur_strength = st.sidebar.slider("Blur Kernel Size", 1, 25, 7, 2)
        if blur_strength % 2 == 0:
            blur_strength += 1
        blurred = cv2.GaussianBlur(img, (blur_strength, blur_strength), 0)
        alpha = st.sidebar.slider("Filter Strength", 0.0, 1.0, 1.0, 0.05)
        img = blend(img, blurred, alpha)

    elif filter_type == "Sharpen":
        sharp_strength = st.sidebar.slider("Sharpen Intensity", 0.0, 5.0, 1.0, 0.1)
        kernel = np.array([[0, -1, 0], [-1, 5 + sharp_strength, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(img, -1, kernel)
        alpha = st.sidebar.slider("Filter Strength", 0.0, 1.0, 1.0, 0.05)
        img = blend(img, sharpened, alpha)

    elif filter_type == "Invert":
        inverted = cv2.bitwise_not(img)
        alpha = st.sidebar.slider("Filter Strength", 0.0, 1.0, 1.0, 0.05)
        img = blend(img, inverted, alpha)

    elif filter_type == "Sepia":
        alpha = st.sidebar.slider("Filter Strength", 0.0, 1.0, 1.0, 0.05)
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        sepia = cv2.transform(img, kernel)
        sepia = np.clip(sepia, 0, 255).astype(np.uint8)
        img = blend(img, sepia, alpha)

    elif filter_type == "Vintage":
        alpha = st.sidebar.slider("Filter Strength", 0.0, 1.0, 1.0, 0.05)
        rows, cols = img.shape[:2]
        mask = np.zeros((rows, cols, 3), dtype=np.uint8)
        for i in range(rows):
            for j in range(cols):
                mask[i, j] = (i * 255 // rows, j * 255 // cols, 128)
        vintage = cv2.addWeighted(img, 0.5, mask, 0.5, 0)
        img = blend(img, vintage, alpha)

    elif filter_type == "Cool":
        alpha = st.sidebar.slider("Filter Strength", 0.0, 1.0, 1.0, 0.05)
        increase = np.array([0, 0, 50], dtype=np.uint8)
        cool = cv2.add(img, increase)
        img = blend(img, cool, alpha)

    elif filter_type == "Warm":
        alpha = st.sidebar.slider("Filter Strength", 0.0, 1.0, 1.0, 0.05)
        increase = np.array([30, 30, 0], dtype=np.uint8)
        warm = cv2.add(img, increase)
        img = blend(img, warm, alpha)

    elif filter_type == "Polaroid":
        alpha = st.sidebar.slider("Filter Strength", 0.0, 1.0, 1.0, 0.05)
        polaroid = cv2.applyColorMap(img, cv2.COLORMAP_PINK)
        img = blend(img, polaroid, alpha)

    # Convert back to PIL for display
    final_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    st.image(final_image, caption="Edited Image", use_column_width=True)
