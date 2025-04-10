import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import pytesseract
import os

# Streamlit UI
st.title("Image Brightness Adjustment and Text Extraction")

# Sidebar options
st.sidebar.header("Options")
brightness = st.sidebar.slider("Brightness", 0.1, 3.0, 1.0, 0.1)
watermark_enabled = st.sidebar.checkbox("Apply Text Watermark")
watermark_text = ""
if watermark_enabled:
    watermark_text = st.sidebar.text_input("Watermark Text", "Sample Watermark")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Original Image", use_column_width=True)

    # Adjust brightness
    enhancer = ImageEnhance.Brightness(image)
    bright_image = enhancer.enhance(brightness)

    # Apply watermark if enabled
    if watermark_enabled and watermark_text:
        draw = ImageDraw.Draw(bright_image)
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Common font path on Linux
        try:
            font = ImageFont.truetype(font_path, 20)
        except:
            font = ImageFont.load_default()
        text_width, text_height = draw.textsize(watermark_text, font=font)
        position = (bright_image.width - text_width - 10, bright_image.height - text_height - 10)
        draw.text(position, watermark_text, (255, 255, 255), font=font, stroke_width=1, stroke_fill=(0, 0, 0))

    st.image(bright_image, caption="Processed Image", use_column_width=True)

    # OCR Text Extraction
    extracted_text = pytesseract.image_to_string(bright_image)
    st.subheader("Extracted Text")
    st.text_area("", extracted_text, height=200)
