import requests
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch
from transformers import BertForQuestionAnswering, BertTokenizer
import streamlit as st

# Load BERT model and tokenizer once to improve performance
@st.cache_resource
def load_bert_model():
    model = BertForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
    tokenizer = BertTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
    return model, tokenizer

model, tokenizer = load_bert_model()

# Fetch Yahoo Finance articles
@st.cache_data
def get_yahoo_finance_articles(base_url, count=10):
    """Fetches Yahoo Finance articles from the given URL."""
    response = requests.get(base_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("li", class_="js-stream-content")

        result = []
        for i, article in enumerate(articles[:count]):
            try:
                title = article.find("h3").get_text(strip=True)
                link = article.find("a")["href"]
                if not link.startswith("http"):
                    link = "https://finance.yahoo.com" + link
                result.append({"title": title, "link": link})
            except AttributeError:
                continue  # Skip articles that don't have the required structure

        return result
    else:
        return None

def display_articles(articles):
    """Displays articles in a Streamlit-friendly format."""
    if articles:
        for i, article in enumerate(articles):
            st.subheader(f"📌 Article {i+1}")
            st.write(f"**Title:** {article['title']}")
            st.write(f"[Read more]({article['link']})")
            st.write("---")
    else:
        st.write("⚠️ No articles found. Try again later.")

def extract_text_from_article(link):
    """Extracts article content from Yahoo Finance."""
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    return " ".join([p.text for p in paragraphs])

def parse_all_articles(links):
    """Parses all Yahoo Finance articles and extracts text."""
    return [extract_text_from_article(link) for link in links]

def preprocess_articles(bdd):
    """Preprocesses articles using lemmatization and tokenization."""
    lemmatizer = WordNetLemmatizer()
    preprocessed_bdd = []
    for doc in bdd:
        tokens = sent_tokenize(doc)
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
        preprocessed_bdd.append(" ".join(lemmatized_tokens))
    return preprocessed_bdd

def find_best_article(user_input, preprocessed_bdd):
    """Finds the most relevant article based on user input."""
    preprocessed_bdd.append(user_input)

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(preprocessed_bdd)

    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    most_similar_index = np.argmax(cosine_sim)

    if 0.1 < cosine_sim[0][most_similar_index] < 1:
        return preprocessed_bdd[most_similar_index]
    else:
        return "I am sorry, I could not find a relevant article."

def get_best_context(question, articles):
    """Finds the best matching article context for a given question."""
    articles.append(question)
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(articles)

    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    best_index = similarities.argmax()

    articles.pop()

    return articles[best_index]

def generate_answer_bert(question, context):
    """Generates an answer using the BERT model."""
    inputs = tokenizer(question, context, return_tensors="pt", max_length=512, truncation=True)
    outputs = model(**inputs)

    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))

    return answer.replace("[CLS]", "").replace("[SEP]", "").strip()

def get_final_answer(question, bdd):
    """Finds the best article and generates an answer using BERT."""
    best_context = get_best_context(question, bdd)
    return generate_answer_bert(question, best_context)

# Streamlit Function to Display Yahoo Finance Articles
def run_yahoo_articles_page():
    st.title("📢 Yahoo Finance Articles")
    st.write("Fetch and analyze recent Yahoo Finance articles.")

    # Fetch articles
    with st.spinner("Fetching articles..."):
        articles = (
            get_yahoo_finance_articles("https://finance.yahoo.com/topic/personal-finance-news/")
            + get_yahoo_finance_articles("https://finance.yahoo.com/")
            + get_yahoo_finance_articles("https://finance.yahoo.com/calendar/")
            + get_yahoo_finance_articles("https://finance.yahoo.com/topic/stock-market-news/")
        )

    # Display articles
    display_articles(articles)

    # Load and process articles for NLP
    urls = [article["link"] for article in articles]
    bdd = parse_all_articles(urls)
    preprocessed_bdd = preprocess_articles(bdd)

    # Interactive Chatbot for Yahoo Articles
    st.subheader("💬 Chat with Yahoo Finance Articles")
    user_query = st.text_input("Ask about stock trends, finance news, or market insights:", key="query")

    if user_query:
        best_article = find_best_article(user_query, preprocessed_bdd)
        answer = get_final_answer(user_query, bdd)
        st.write(f"🤖 Chatbot: {answer}")