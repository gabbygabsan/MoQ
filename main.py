import streamlit as st
from router import init_router, current_page
from ui.navigation import render_config

st.set_page_config(page_title="MoQ Werkzeug Assistent", layout="wide")
init_router()

page = current_page()

if page == "⚙️ Konfigurator":
    render_config()