import streamlit as st
from DB_6 import BiosensorGUI

@st.cache_resource
def initialize_app():
    """Инициализирует приложение один раз и сохраняет в кэш."""
    return BiosensorGUI()

if __name__ == "__main__":
    app = initialize_app()
    app.run()