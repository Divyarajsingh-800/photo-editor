import streamlit as st
from PIL import Image, ImageOps
import io

st.set_page_config(layout="centered", page_title="Image Editor")

st.markdown(
    """
    <style>
    .main {
        background-color: #1f1f2e;
        color: white;
    }
    .stButton > button {
        background-color: #1a1a2e;
        color: white;
        padding: 0.5em 2em;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🖼️ Image Comparison App")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    # Convert the image to grayscale as an "edit"
    edited = ImageOps.grayscale(image)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🟢 Original")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("🎨 Edited")
        st.image(edited, use_container_width=True)

    # Button to download the edited image
    buf = io.BytesIO()
    edited.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Download Edited Image",
        data=byte_im,
        file_name="edited_image.png",
        mime="image/png"
    )
