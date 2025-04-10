import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont
from io import BytesIO
import matplotlib.pyplot as plt
import base64
import os

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

    st.sidebar.header("🎛️ Filters and Adjustments")

    filter_type = st.sidebar.radio("Apply Filter", ["None", "Blur", "Sharpen", "Invert", "Grayscale"])

    brightness = st.sidebar.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
    contrast = st.sidebar.slider("Contrast", 0.5, 2.0, 1.0, 0.1)
    opacity = st.sidebar.slider("Opacity", 0.0, 1.0, 1.0, 0.05)

    if filter_type == "Blur":
        blur_strength = st.sidebar.slider("Blur Strength", 1, 25, 7, 2)
        if blur_strength % 2 == 0:
            blur_strength += 1
    elif filter_type == "Sharpen":
        sharpness_strength = st.sidebar.slider("Sharpen Strength", 0.0, 5.0, 1.0, 0.1)
    elif filter_type == "Invert":
        invert_strength = st.sidebar.slider("Invert Strength", 0.0, 1.0, 1.0, 0.05)
    elif filter_type == "Grayscale":
        grayscale_strength = st.sidebar.slider("Grayscale Mix", 0.0, 1.0, 1.0, 0.05)

    img = np.array(image).astype(np.uint8)

    if filter_type == "Grayscale":
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        img = cv2.addWeighted(img, 1 - grayscale_strength, gray_rgb, grayscale_strength, 0)
    elif filter_type == "Invert":
        inverted = cv2.bitwise_not(img)
        img = cv2.addWeighted(img, 1 - invert_strength, inverted, invert_strength, 0)
    elif filter_type == "Blur":
        img = cv2.GaussianBlur(img, (blur_strength, blur_strength), 0)
    elif filter_type == "Sharpen":
        kernel = np.array([[0, -1, 0], [-1, 5 + sharpness_strength, -1], [0, -1, 0]])
        img = cv2.filter2D(img, -1, kernel)

    edited = Image.fromarray(img)
    edited = ImageEnhance.Brightness(edited).enhance(brightness)
    edited = ImageEnhance.Contrast(edited).enhance(contrast)

    if opacity < 1.0:
        background = Image.new("RGB", edited.size, (0, 0, 0))
        edited = Image.blend(background, edited, opacity)

    # Instagram-style Filters
    st.subheader("🎨 Instagram-style Filters")
    filter_choice = st.selectbox("Choose Style Filter", ["None", "Sepia", "Vintage", "Cool", "Warm", "Polaroid"])

    def apply_filter(pil_img, choice):
        img = np.array(pil_img).astype(np.float32)
        if choice == "Sepia":
            kernel = np.array([[0.272, 0.534, 0.131],
                               [0.349, 0.686, 0.168],
                               [0.393, 0.769, 0.189]])
            img = img @ kernel.T
        elif choice == "Vintage":
            img = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2BGR)
            img = cv2.applyColorMap(img, cv2.COLORMAP_PINK)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif choice == "Cool":
            img[:,:,0] *= 1.2
            img[:,:,2] *= 0.8
        elif choice == "Warm":
            img[:,:,0] *= 0.8
            img[:,:,2] *= 1.2
        elif choice == "Polaroid":
            img[:,:,1] *= 1.1
            img[:,:,2] *= 1.2
        img = np.clip(img, 0, 255).astype(np.uint8)
        return Image.fromarray(img)

    if filter_choice != "None":
        edited = apply_filter(edited, filter_choice)

    # Stickers / Emojis
    st.subheader("😀 Add Stickers / Emojis")
    emoji_text = st.text_input("Type Emoji or Character to Add")
    emoji_x = st.slider("Emoji X Position", 0, edited.width, edited.width//2)
    emoji_y = st.slider("Emoji Y Position", 0, edited.height, edited.height//2)
    emoji_size = st.slider("Emoji Font Size", 20, 300, 150)
    if emoji_text:
        draw = ImageDraw.Draw(edited)
        try:
            font = ImageFont.truetype("arial.ttf", emoji_size)
        except:
            font = ImageFont.load_default()
        draw.text((emoji_x, emoji_y), emoji_text, font=font, fill=(255, 255, 255))

    # Frames / Borders
    st.subheader("🖼️ Add Frame / Border")
    border_thickness = st.slider("Border Thickness", 0, 100, 10)
    border_color = st.color_picker("Border Color", "#ffffff")
    if border_thickness > 0:
        edited = ImageOps.expand(edited, border=border_thickness, fill=border_color)

    # Histogram Viewer
    st.subheader("📊 Histogram Viewer")
    def show_histogram(pil_img):
        img_np = np.array(pil_img)
        fig, ax = plt.subplots()
        for i, color in enumerate(['r', 'g', 'b']):
            hist = cv2.calcHist([img_np], [i], None, [256], [0, 256])
            ax.plot(hist, color=color)
        st.pyplot(fig)

    show_histogram(edited)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🟢 Original")
        st.image(image, use_container_width=True)
    with col2:
        st.subheader("🎨 Edited")
        st.image(edited, use_container_width=True)

    buffer = BytesIO()
    edited.save(buffer, format="PNG")
    st.download_button("Download Edited Image", data=buffer.getvalue(),
                       file_name="edited_image.png", mime="image/png")
