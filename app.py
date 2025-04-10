import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from io import BytesIO
import matplotlib.pyplot as plt

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

emoji_options = ["😀", "😍", "🔥", "👍", "💯", "🎉", "🚀", "😂"]

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    original = np.array(image)

    st.sidebar.header("🎛️ Filters and Adjustments")
    filter_type = st.sidebar.radio("Apply Filter", ["None", "Blur", "Sharpen", "Invert", "Grayscale", "Sepia", "Vintage", "Cool", "Warm", "Polaroid"])
    brightness = st.sidebar.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
    contrast = st.sidebar.slider("Contrast", 0.5, 2.0, 1.0, 0.1)
    opacity = st.sidebar.slider("Opacity", 0.0, 1.0, 1.0, 0.05)

    # Extra filter controls
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
    elif filter_type == "Sepia":
        sepia_strength = st.sidebar.slider("Sepia Strength", 0.0, 1.0, 1.0, 0.05)
    elif filter_type == "Vintage":
        vintage_strength = st.sidebar.slider("Vintage Strength", 0.0, 1.0, 1.0, 0.05)
    elif filter_type == "Cool":
        cool_strength = st.sidebar.slider("Cool Strength", 0.0, 1.0, 1.0, 0.05)
    elif filter_type == "Warm":
        warm_strength = st.sidebar.slider("Warm Strength", 0.0, 1.0, 1.0, 0.05)
    elif filter_type == "Polaroid":
        polaroid_strength = st.sidebar.slider("Polaroid Strength", 0.0, 1.0, 1.0, 0.05)

    # Crop Tool with Reset
    st.sidebar.header("✂️ Crop Tool")
    if 'crop_reset' not in st.session_state:
        st.session_state.crop_top = 0
        st.session_state.crop_left = 0
        st.session_state.crop_width = image.width
        st.session_state.crop_height = image.height

    def reset_crop():
        st.session_state.crop_top = 0
        st.session_state.crop_left = 0
        st.session_state.crop_width = image.width
        st.session_state.crop_height = image.height

    if st.sidebar.button("🔄 Reset Crop"):
        reset_crop()

    crop_top = st.sidebar.number_input("Top", min_value=0, value=st.session_state.crop_top, key="crop_top")
    crop_left = st.sidebar.number_input("Left", min_value=0, value=st.session_state.crop_left, key="crop_left")
    crop_width = st.sidebar.number_input("Width", min_value=1, value=st.session_state.crop_width, key="crop_width")
    crop_height = st.sidebar.number_input("Height", min_value=1, value=st.session_state.crop_height, key="crop_height")

    # Rotate & Flip
    st.sidebar.header("🔁 Rotate & Flip")
    rotate_angle = st.sidebar.slider("Rotate (°)", 0, 360, 0, 1)
    flip_horizontal = st.sidebar.checkbox("Flip Horizontally")
    flip_vertical = st.sidebar.checkbox("Flip Vertically")

    # Resize
    st.sidebar.header("📏 Resize")
    resize_width = st.sidebar.number_input("New Width", min_value=1, value=image.width)
    resize_height = st.sidebar.number_input("New Height", min_value=1, value=image.height)

    # Text Overlay
    st.sidebar.header("📝 Text Overlay")
    text_input = st.sidebar.text_input("Enter Text")
    font_size = st.sidebar.slider("Font Size", 10, 100, 30)
    text_x = st.sidebar.number_input("Text X Position", min_value=0, value=10)
    text_y = st.sidebar.number_input("Text Y Position", min_value=0, value=10)

    # Emoji/Sticker Overlay
    st.sidebar.header("😎 Emoji Sticker")
    emoji_input = st.sidebar.selectbox("Choose Emoji", ["None"] + emoji_options)
    emoji_x = st.sidebar.number_input("Emoji X Position", min_value=0, value=50)
    emoji_y = st.sidebar.number_input("Emoji Y Position", min_value=0, value=50)

    # Border
    st.sidebar.header("🎨 Image Border")
    border_color = st.sidebar.color_picker("Border Color", "#FF5733")
    border_thickness = st.sidebar.slider("Border Thickness", 0, 50, 10)

    # Auto Enhance
    st.sidebar.header("⚡ Auto Enhance")
    auto_enhance = st.sidebar.button("Auto Enhance (Brightness + Contrast)")

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
    elif filter_type == "Sepia":
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                 [0.349, 0.686, 0.168],
                                 [0.393, 0.769, 0.189]])
        sepia_img = np.dot(img, sepia_filter.T)
        img = cv2.addWeighted(img, 1 - sepia_strength, np.clip(sepia_img, 0, 255).astype(np.uint8), sepia_strength, 0)
    elif filter_type == "Vintage":
        vintage_img = cv2.applyColorMap(img, cv2.COLORMAP_PINK)
        img = cv2.addWeighted(img, 1 - vintage_strength, vintage_img, vintage_strength, 0)
    elif filter_type == "Cool":
        cool_filter = np.array([0, 50, 100], dtype=np.uint8)
        img = cv2.addWeighted(img, 1 - cool_strength, cv2.add(img, cool_filter), cool_strength, 0)
    elif filter_type == "Warm":
        warm_filter = np.array([50, 25, 0], dtype=np.uint8)
        img = cv2.addWeighted(img, 1 - warm_strength, cv2.add(img, warm_filter), warm_strength, 0)
    elif filter_type == "Polaroid":
        polaroid_img = cv2.applyColorMap(img, cv2.COLORMAP_OCEAN)
        img = cv2.addWeighted(img, 1 - polaroid_strength, polaroid_img, polaroid_strength, 0)

    edited = Image.fromarray(img)

    if auto_enhance:
        edited = ImageEnhance.Brightness(edited).enhance(1.2)
        edited = ImageEnhance.Contrast(edited).enhance(1.2)
    else:
        edited = ImageEnhance.Brightness(edited).enhance(brightness)
        edited = ImageEnhance.Contrast(edited).enhance(contrast)

    edited = edited.resize((resize_width, resize_height))

    right = crop_left + crop_width
    bottom = crop_top + crop_height
    edited = edited.crop((crop_left, crop_top, right, bottom))

    if rotate_angle != 0:
        edited = edited.rotate(rotate_angle, expand=True)

    if flip_horizontal:
        edited = edited.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_vertical:
        edited = edited.transpose(Image.FLIP_TOP_BOTTOM)

    if opacity < 1.0:
        background = Image.new("RGB", edited.size, (0, 0, 0))
        edited = Image.blend(background, edited, opacity)

    if border_thickness > 0:
        border_color_rgb = tuple(int(border_color.lstrip("#")[i:i+2], 16) for i in (0, 2 ,4))
        new_w, new_h = edited.size[0] + border_thickness * 2, edited.size[1] + border_thickness * 2
        bordered = Image.new("RGB", (new_w, new_h), border_color_rgb)
        bordered.paste(edited, (border_thickness, border_thickness))
        edited = bordered

    draw = ImageDraw.Draw(edited)
    if text_input:
        try:
            font = ImageFont.truetype("arial.ttf", font_size * 3)
        except:
            font = ImageFont.load_default()
        draw.text((text_x, text_y), text_input, font=font, fill=(255, 255, 255))

    if emoji_input and emoji_input != "None":
        try:
            font = ImageFont.truetype("arial.ttf", font_size * 3)
        except:
            font = ImageFont.load_default()
        draw.text((emoji_x, emoji_y), emoji_input, font=font, fill=(255, 255, 255))
