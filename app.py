import streamlit as st
from App.main_app import start_chat

st.write("Welcome to the main page! In the future, this chatbot will bring together all the features from the other pages.")
st.write("For now, you can visit each page independently, but our goal is to unify all chatbot functionality here.")
st.write("--------------------------------------------------------")

start_chat()