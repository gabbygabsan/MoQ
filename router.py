# router.py

import streamlit as st

def init_router():
    if "seite" not in st.session_state:
        st.session_state["seite"] = "⚙️ Konfigurator"

def navigate_to(seite: str):
    st.session_state["seite"] = seite

def current_page():
    return st.session_state.get("seite", "⚙️ Konfigurator")