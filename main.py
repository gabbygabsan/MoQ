import streamlit as st
from router import init_router, current_page, PAGE_CONFIG
from ui.navigation import render_config

st.set_page_config(page_title="MoQ Werkzeug Assistent", layout="wide")

init_router()
if current_page() == PAGE_CONFIG:
    render_config()