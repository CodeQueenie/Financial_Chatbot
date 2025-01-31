import streamlit as st
from transformers import pipeline
import random
from App.yahoo_articles_logic import run_yahoo_articles_page
run_yahoo_articles_page()


st.title("Yahoo articles")
st.write("Welcome to the Personal Yahoo articles page!")
st.write("This page consist of giving an answer or informations on the question that you want")
st.write("--------------------------------------------------------")

get_financial_advices()