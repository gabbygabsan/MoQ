PAGE_START = "Start"
PAGE_CONFIG = "⚙️ Konfigurator"   # ganz normales Space-Zeichen

import streamlit as st

def init_router():
    if "seite" not in st.session_state:
        st.session_state["seite"] = PAGE_CONFIG

def navigate_to(seite: str):
    st.session_state["seite"] = seite

def current_page() -> str:
    return st.session_state.get("seite", PAGE_CONFIG)