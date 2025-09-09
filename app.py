
import streamlit as st
import DB_6
# импорт вашего основного кода

st.title("Название вашей программы")
# input_data = st.text_input("Введите данные:")
if st.button("Запустить"):
    result = DB_6.BiosensorGUI().run()
    # st.write(result)
