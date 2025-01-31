import streamlit as st
from App.stocks_consulting_logic import run_stocks_consulting_page
run_stocks_consulting_page()

st.title("Stocks Consulting")
st.write("Welcome to the Stocks Consulting page!")
st.write("This page provides indicators and information about a company's stock performance.")
st.write("--------------------------------------------------------")

# Run the Streamlit-friendly stocks consulting page function
run_stocks_consulting_page()