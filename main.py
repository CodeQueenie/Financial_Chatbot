import random
from stocks_consulting import *
from yahoo_articles import *
from personal_finance import *
from stock_recommendation import *
import nltk
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
nltk.download('stopwords')

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
    "personal finance": get_personal_finance,
    "stock recommendation": get_stock_recommendation,
    "yahoo advice articles": get_financial_advices,
    "default": "I don't understand. Can you rephrase your question?",
}

def clean_text(text):
    """
    Cleans text by:
      1) Removing non-alphabetic characters.
      2) Removing bracketed content [ ... ] (if any).
      3) Converting multiple spaces into a single space.
    """
    # 1) Remove any characters that are not letters
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    # 2) Remove bracketed content (and brackets themselves)
    text = re.sub(r'\[.*?\]', ' ', text)
    # 3) Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_text(text):
    # Basic cleaning
    text = clean_text(text)

    # Build a stoplist of English stopwords + punctuation
    stoplist = set(stopwords.words('english') + list(punctuation))

    # Tokenize
    tokens = word_tokenize(text.lower())

    # Filter out stopwords and non-alphanumeric tokens
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stoplist]

    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    filtered_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]

    # Return the cleaned text
    return ' '.join(filtered_tokens)

def generate_response(user_input):
    preprocessed_input = preprocess_text(user_input)

    # Vectorize all keys + the user input
    vectorizer = TfidfVectorizer()
    key_vectors = [preprocess_text(key) for key in responses.keys()]
    key_vectors.append(preprocessed_input)

    # Build TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(key_vectors)
    # Similarity of user input (last item) vs. all keys (the rest)
    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

    # Find best match
    best_match_index = similarity_scores.argmax()
    matched_key = list(responses.keys())[best_match_index % len(responses)]

    # Decide if match is good enough
    if similarity_scores[best_match_index] > 0.1:
        response = responses[matched_key]
        # If the response is a function, call it
        if callable(response):
            response()  # This runs the function
            # You can define how you want to handle the function’s return, if any
            response = "Function called."
        else:
            # If it's a list, pick a random item; if a string, use as-is
            if isinstance(response, list):
                response = random.choice(response)
    else:
        response = responses["default"]

    return response

def start_chat():
    print(
        "\nChatbot: Hello, I am your Financial Advisor Bot. "
        "Feel free to ask me any questions related to personal finance:"
    )

    while True:
        user_input = input("\nUser: ").lower()

        # Exit conditions
        if user_input in ["exit", "bye", "quit"]:
            print("\nChatbot: Goodbye! Until next time.")
            break

        # Generate response
        bot_response = generate_response(user_input)
        print("Chatbot:", bot_response)

# Start the console chat
start_chat()