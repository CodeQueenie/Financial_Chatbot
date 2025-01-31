import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Cache the CSV loading to optimize performance
@st.cache_data
def load_stock_data():
    """Loads the stock history data from CSV file."""
    try:
        df = pd.read_csv("Data/ticker_history.csv", delimiter=",")
        df["Features"] = df[["open", "high", "low", "close", "ticker"]].astype(str).agg(" ".join, axis=1)

        # Vectorize these features using TF-IDF
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(df["Features"])

        return df, tfidf_matrix
    except FileNotFoundError:
        st.error("⚠️ Error: Stock data file not found. Please check the file path.")
        return None, None

df, tfidf_matrix = load_stock_data()

def get_recommendations(date, ticker):
    """Finds recommended stock dates based on TF-IDF similarity."""
    if df is None or tfidf_matrix is None:
        return None

    # Find the first row where the date and ticker match
    filtered_df = df[(df["date"] == date) & (df["ticker"] == ticker)]

    if not filtered_df.empty:
        index = filtered_df.index[0]
        
        # Calculate similarity between items represented by their TF-IDF vectors
        similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)
        cosine_scores = similarities[index]
        
        # Get the 3 most similar stock data points
        indices = cosine_scores.argsort()[:-4:-1]
        
        # Return recommended dates
        return df["date"].iloc[indices].tolist()
    else:
        st.warning(f"⚠️ No data found for date {date} and ticker {ticker}")
        return None

def display_recommended_dates(recommendations, ticker):
    """Displays recommended stock data for given dates."""
    if recommendations:
        for rec_date in recommendations:
            st.subheader(f"📅 Recommended Date: {rec_date}")
            st.dataframe(df[(df["date"] == rec_date) & (df["ticker"] == ticker)])
    else:
        st.warning(f"⚠️ No data found for the recommendations.")

# Streamlit UI
def run_stock_recommendation_page():
    st.title("📈 Stock Recommendation System")
    st.write("Find similar stock dates based on historical trends.")

    # User input fields
    date = st.text_input("📅 Enter a Date (MM/DD/YYYY):", key="date_input")
    ticker = st.text_input("🏷️ Enter a Stock Ticker (e.g., AAPL, TSLA):", key="ticker_input").upper()

    if st.button("🔍 Get Recommendations"):
        if date and ticker:
            recommendations = get_recommendations(date, ticker)
            if recommendations:
                st.success(f"✅ Found recommendations for {ticker} on {date}!")
                display_recommended_dates(recommendations, ticker)
            else:
                st.error(f"⚠️ No recommendations found for {ticker} on {date}. Try another date.")
        else:
            st.warning("⚠️ Please enter both a date and a ticker symbol.")