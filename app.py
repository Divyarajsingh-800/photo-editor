import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
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

    # --- New Feature: Auto Enhance ---
    auto_enhance = st.sidebar.checkbox("Auto Enhance (Contrast + Brightness)")
    if auto_enhance:
        brightness = 1.2
        contrast = 1.3

    # --- New Feature: Crop ---
    with st.sidebar.expander("✂️ Crop Image"):
        crop_top = st.number_input("Top", min_value=0, max_value=image.height, value=0)
        crop_left = st.number_input("Left", min_value=0, max_value=image.width, value=0)
        crop_width = st.number_input("Width", min_value=1, max_value=image.width - crop_left, value=image.width - crop_left)
        crop_height = st.number_input("Height", min_value=1, max_value=image.height - crop_top, value=image.height - crop_top)

    image = image.crop((crop_left, crop_top, crop_left + crop_width, crop_top + crop_height))

    # --- New Feature: Rotate & Flip ---
    with st.sidebar.expander("🔄 Rotate & Flip"):
        rotate_angle = st.slider("Rotate", 0, 360, 0)
        flip_horizontal = st.checkbox("Flip Horizontally")
        flip_vertical = st.checkbox("Flip Vertically")

    image = image.rotate(-rotate_angle, expand=True)
    if flip_horizontal:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_vertical:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

    # --- New Feature: Resize ---
    with st.sidebar.expander("📏 Resize Image"):
        resize_width = st.number_input("New Width", min_value=1, max_value=2000, value=image.width)
        resize_height = st.number_input("New Height", min_value=1, max_value=2000, value=image.height)
        if st.button("Apply Resize"):
            image = image.resize((resize_width, resize_height))

    # --- New Feature: Text Overlay ---
    with st.sidebar.expander("✍️ Add Text"):
        add_text = st.checkbox("Add Text to Image")
        if add_text:
            custom_text = st.text_input("Text", "Hello World")
            font_size = st.slider("Font Size", 10, 100, 30)
            text_x = st.number_input("X Position", 0, image.width, 10)
            text_y = st.number_input("Y Position", 0, image.height, 10)

    # Add individual sliders for filters that support scaling
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

    # Convert to OpenCV format
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
        kernel = np.array([[0, -1, 0],
                           [-1, 5 + sharpness_strength, -1],
                           [0, -1, 0]])
        img = cv2.filter2D(img, -1, kernel)

    edited = Image.fromarray(img)
    edited = ImageEnhance.Brightness(edited).enhance(brightness)
    edited = ImageEnhance.Contrast(edited).enhance(contrast)

    if opacity < 1.0:
        background = Image.new("RGB", edited.size, (0, 0, 0))
        edited = Image.blend(background, edited, opacity)

    # Apply Text Overlay
    if add_text:
        draw = ImageDraw.Draw(edited)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        draw.text((text_x, text_y), custom_text, fill="white", font=font)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🟢 Original")
        st.image(original, use_container_width=True)
    with col2:
        st.subheader("🎨 Edited")
        st.image(edited, use_container_width=True)

    buffer = BytesIO()
    edited.save(buffer, format="PNG")
    st.download_button("Download Edited Image", data=buffer.getvalue(),
                       file_name="edited_image.png", mime="image/png")
