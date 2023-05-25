import sys
sys.dont_write_bytecode = True

import streamlit as st

from user_interface import UserInterface
from feature_package.text_image_generator import TextImageGenerator


st.set_page_config(
    page_title="MKWii Text Generator",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "https://github.com/NOKKY726/mkwii-text-generator",
    },
)

if "color" not in st.session_state:
    st.session_state.color = "#ff0000"
    st.session_state.colors = ["#ffffff" for _ in range(10**4)]
    st.session_state.top_color = "#00ff00"
    st.session_state.btm_color = "#0000ff"
    st.session_state.index = {"orientation": 0, "mode": 0}

user_interface = UserInterface()

text_generator = TextImageGenerator(user_interface)
MKWii_text = text_generator.generate_image()

if not user_interface.mobile:
    st.image(MKWii_text)
else:
    st.sidebar.image(MKWii_text)