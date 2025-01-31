import random
from App.stocks_consulting_logic import *
from App.yahoo_articles_logic import *
from App.personal_finance_logic import *
from App.stock_recommendation_logic import *
import streamlit as st
import nltk
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

from string import punctuation
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

responses = {
    "hello": [
        "Hello! How can I assist you today?",
        "Hi there! How can I help you?",
        "Good morning! How can I help you start your day?",
    ],
    "hi": [
        "Hello! How can I assist you today?",
        "Hi there! How can I help you?",
        "Good morning! How can I help you start your day?",
    ],
    "good morning": [
        "Hello! How can I assist you today?",
        "Hi there! How can I help you?",
        "Good morning! How can I help you start your day?",
    ],
    "how are you": [
        "I'm just a program, but thanks for asking!",
        "I'm here and ready to help. What can I do for you today?",
    ],
    "who are you": [
        "I am your Financial Advisor Bot, designed to provide information and assistance on personal finance.",
        "I am a virtual assistant focused on helping you with financial advice.",
    ],
    "what can you do": [
        "I can provide guidance on budgeting, investments, retirement planning, and more. Feel free to ask me any questions related to personal finance!",
        "You can ask me about budgeting strategies, investment tips, and retirement planning. How can I assist you today?",
    ],
    "stocks consulting": ["http://localhost:8501/Stocks_consulting"],
    "personal finance": ["http://localhost:8501/2_Personal-Finance"],
    "stock recommendation": ["http://localhost:8501/Yahoo-articles"],
    "yahoo advice articles": ["http://localhost:8501/Stock-Recommentation"],
    "default": "I don't understand. Can you rephrase your question?",
}

def clean_text(text):
    """
    Cleans text by removing bracketed content and extra spaces.
    """
    # Remove text inside square brackets
    text = re.sub(r'\[.*?\]', ' ', text)
    # Replace multiple spaces/newlines with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_text(text):
    # First pass: basic cleanup
    text = clean_text(text)

    # Build a stoplist of English stopwords + punctuation
    stoplist = set(stopwords.words('english') + list(punctuation))

    # Tokenize the text
    tokens = word_tokenize(text.lower())

    # Filter out stopwords and non-alphanumeric tokens
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stoplist]

    # Lemmatize each token
    lemmatizer = WordNetLemmatizer()
    filtered_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]

    # Return the reconstructed string
    return ' '.join(filtered_tokens)
 
def generate_response(user_input):
    preprocessed_input = preprocess_text(user_input)

    # Create TF-IDF vectors for each key in responses + user input
    vectorizer = TfidfVectorizer()
    key_vectors = [preprocess_text(key) for key in responses.keys()]
    key_vectors.append(preprocessed_input)

    # Build the TF-IDF matrix and compute similarity
    tfidf_matrix = vectorizer.fit_transform(key_vectors)
    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

    # Identify the best match
    best_match_index = similarity_scores.argmax()
    matched_key = list(responses.keys())[best_match_index % len(responses)]

    # If similarity is good, pick a matching response; otherwise default
    if similarity_scores[best_match_index] > 0.1:
        response = responses[matched_key]
        if callable(response):
            response()  # If it were a function, call it (not used here)
        else:
            response = random.choice(responses[matched_key]) \
                       if isinstance(response, list) else response
    else:
        response = responses["default"]
    return response

def start_chat():
    st.write(
        "\nChatbot: Hello, I am your Financial Advisor Bot. "
        "Feel free to ask me any questions related to personal finance:"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Prompt for user input
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Check for exit commands
        if prompt.lower() in ["exit", "bye", "quit"]:
            farewell = "Goodbye! Until next time."
            with st.chat_message("assistant"):
                st.markdown(farewell)
            st.session_state.messages.append({"role": "assistant", "content": farewell})
            return  # Exit the function to stop further processing

        # Generate chatbot response
        bot_response = generate_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})