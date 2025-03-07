import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import random
import json
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Simple Financial Assistant",
    page_icon="💰",
    layout="wide"
)

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Stock Lookup", "Personal Finance Calculator", "Financial News", "Chat Assistant"]
)

# Demo stock data for common stocks
DEMO_STOCKS = {
    "AAPL": {
        "name": "Apple Inc.",
        "price": 169.75,
        "change": 1.23,
        "percent_change": 0.73,
        "market_cap": "2.67T",
        "sector": "Technology",
        "pe_ratio": 28.12,
        "dividend_yield": 0.54,
        "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide."
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "price": 415.32,
        "change": 2.45,
        "percent_change": 0.59,
        "market_cap": "3.09T",
        "sector": "Technology",
        "pe_ratio": 35.67,
        "dividend_yield": 0.73,
        "description": "Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide."
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "price": 147.68,
        "change": -0.87,
        "percent_change": -0.59,
        "market_cap": "1.85T",
        "sector": "Technology",
        "pe_ratio": 25.34,
        "dividend_yield": 0.0,
        "description": "Alphabet Inc. provides various products and platforms in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America."
    },
    "AMZN": {
        "name": "Amazon.com, Inc.",
        "price": 178.75,
        "change": 1.05,
        "percent_change": 0.59,
        "market_cap": "1.86T",
        "sector": "Consumer Cyclical",
        "pe_ratio": 61.23,
        "dividend_yield": 0.0,
        "description": "Amazon.com, Inc. engages in the retail sale of consumer products and subscriptions in North America and internationally."
    },
    "TSLA": {
        "name": "Tesla, Inc.",
        "price": 176.75,
        "change": -3.25,
        "percent_change": -1.81,
        "market_cap": "562.5B",
        "sector": "Automotive",
        "pe_ratio": 50.12,
        "dividend_yield": 0.0,
        "description": "Tesla, Inc. designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems."
    }
}

# Function to get stock data with fallback to demo data
def get_stock_data(ticker, period="1mo"):
    ticker = ticker.upper()
    
    # Check if we have demo data for this ticker
    if ticker in DEMO_STOCKS:
        # Use demo data
        demo_data = DEMO_STOCKS[ticker]
        
        # Create a stock info dictionary
        info = {
            "longName": demo_data["name"],
            "regularMarketPrice": demo_data["price"],
            "previousClose": demo_data["price"] - demo_data["change"],
            "sector": demo_data["sector"],
            "trailingPE": demo_data["pe_ratio"],
            "dividendYield": demo_data["dividend_yield"] / 100 if demo_data["dividend_yield"] > 0 else None,
            "longBusinessSummary": demo_data["description"]
        }
        
        # Convert market cap string to number
        market_cap_str = demo_data["market_cap"]
        if market_cap_str.endswith("T"):
            info["marketCap"] = float(market_cap_str.replace("T", "")) * 1_000_000_000_000
        elif market_cap_str.endswith("B"):
            info["marketCap"] = float(market_cap_str.replace("B", "")) * 1_000_000_000
        elif market_cap_str.endswith("M"):
            info["marketCap"] = float(market_cap_str.replace("M", "")) * 1_000_000
        
        # Generate historical data
        end_date = datetime.now()
        
        if period == "1mo":
            start_date = end_date - timedelta(days=30)
        elif period == "3mo":
            start_date = end_date - timedelta(days=90)
        elif period == "6mo":
            start_date = end_date - timedelta(days=180)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        date_range = pd.date_range(start=start_date, end=end_date)
        
        # Generate price data with a slight upward or downward trend based on current change
        trend = 0.0002 if demo_data["percent_change"] > 0 else -0.0002
        
        # Start with the current price and work backwards
        current_price = demo_data["price"]
        prices = [current_price]
        
        # Generate random price movements with the trend
        random.seed(hash(ticker))  # Use ticker as seed for consistent randomness
        
        for i in range(1, len(date_range)):
            change = random.uniform(-0.02, 0.02) + trend  # Random daily change with trend
            new_price = prices[-1] / (1 + change)  # Work backwards
            prices.append(new_price)
        
        prices.reverse()  # Reverse to get chronological order
        
        # Create a DataFrame with the sample data
        hist = pd.DataFrame({
            'Open': prices,
            'High': [p * random.uniform(1, 1.02) for p in prices],
            'Low': [p * random.uniform(0.98, 1) for p in prices],
            'Close': prices,
            'Volume': [random.randint(1000000, 10000000) for _ in prices]
        }, index=date_range)
        
        return "demo", info, hist
    
    # If not in demo data, try to get real data
    try:
        # Try to use yfinance
        stock = yf.Ticker(ticker)
        
        try:
            info = stock.info
            if not info or len(info) < 5:  # If we got minimal or no data
                raise ValueError("Limited data available")
        except:
            # Create a fallback info dictionary
            info = {
                "longName": ticker,
                "regularMarketPrice": None,
                "previousClose": None,
                "marketCap": None,
                "sector": "Unknown",
                "trailingPE": None,
                "dividendYield": None,
                "longBusinessSummary": f"Information for {ticker} is currently unavailable."
            }
        
        # Try to get historical data
        try:
            hist = stock.history(period=period)
            if hist.empty:
                raise ValueError("No historical data")
        except:
            # Create sample historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            if period == "3mo":
                start_date = end_date - timedelta(days=90)
            elif period == "6mo":
                start_date = end_date - timedelta(days=180)
            elif period == "1y":
                start_date = end_date - timedelta(days=365)
            
            date_range = pd.date_range(start=start_date, end=end_date)
            
            # Generate random price movements
            base_price = 100  # Default base price
            
            prices = [base_price]
            for i in range(1, len(date_range)):
                change = random.uniform(-0.02, 0.02)
                new_price = prices[-1] * (1 + change)
                prices.append(new_price)
            
            hist = pd.DataFrame({
                'Open': prices,
                'High': [p * 1.01 for p in prices],
                'Low': [p * 0.99 for p in prices],
                'Close': prices,
                'Volume': [random.randint(1000000, 10000000) for _ in prices]
            }, index=date_range)
            
            st.info(f"Using simulated data for {ticker}. Real-time data is unavailable.")
        
        return stock, info, hist
    
    except Exception as e:
        st.error(f"Error retrieving data: {str(e)}")
        
        # Return empty data
        return None, {}, pd.DataFrame()

# Function to get financial news
def get_financial_news(query=None):
    try:
        # Base URL for Yahoo Finance
        base_url = "https://finance.yahoo.com"
        
        # If query is provided, search for specific news
        if query:
            search_url = f"{base_url}/search?q={query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(search_url, headers=headers)
        else:
            # Otherwise get the latest news from the main page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(base_url, headers=headers)
        
        # Check if the request was successful
        if response.status_code != 200:
            st.error(f"Failed to fetch news: HTTP {response.status_code}")
            return []
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find news articles
        articles = []
        
        # Look for different possible article containers
        news_items = soup.select('li.js-stream-content, div.Ov\(h\), div.Cf')
        
        if not news_items:
            # Try alternative selectors if the first ones don't work
            news_items = soup.select('div.NewsArticle, div.StretchedBox')
        
        # If still no results, try a more generic approach
        if not news_items:
            # Look for any div with a title and link that might be a news item
            for div in soup.find_all('div', class_=True):
                if div.find('a') and (div.find('h3') or div.find('h4')):
                    news_items.append(div)
        
        # Process found items
        for item in news_items[:10]:  # Limit to 10 articles
            # Try to extract title, link, and source
            title_tag = item.select_one('h3, h4, a.js-content-viewer')
            link_tag = item.select_one('a[href]')
            
            if title_tag and link_tag:
                title = title_tag.text.strip()
                link = link_tag.get('href')
                
                # Make sure link is absolute
                if link.startswith('/'):
                    link = base_url + link
                
                # Find source/publisher if available
                source_tag = item.select_one('span.provider-name')
                source = source_tag.text.strip() if source_tag else "Yahoo Finance"
                
                # Only add if we have a title and it's not a duplicate
                if title and not any(a.get('title') == title for a in articles):
                    articles.append({
                        'title': title,
                        'link': link,
                        'source': source
                    })
        
        # If we still don't have any articles, provide a fallback with demo articles
        if not articles:
            # Demo financial news articles
            articles = [
                {
                    "title": "Markets Rally as Fed Signals Potential Rate Cuts",
                    "link": "https://finance.yahoo.com/news/markets-rally-fed-signals-potential-rate-cuts",
                    "source": "Yahoo Finance"
                },
                {
                    "title": "Tech Stocks Lead Market Gains Amid AI Optimism",
                    "link": "https://finance.yahoo.com/news/tech-stocks-lead-market-gains-ai-optimism",
                    "source": "Reuters"
                },
                {
                    "title": "Oil Prices Stabilize After Recent Volatility",
                    "link": "https://finance.yahoo.com/news/oil-prices-stabilize-recent-volatility",
                    "source": "Bloomberg"
                },
                {
                    "title": "Retail Sales Exceed Expectations in Latest Report",
                    "link": "https://finance.yahoo.com/news/retail-sales-exceed-expectations-latest-report",
                    "source": "CNBC"
                },
                {
                    "title": "Housing Market Shows Signs of Cooling as Mortgage Rates Rise",
                    "link": "https://finance.yahoo.com/news/housing-market-shows-signs-cooling-mortgage-rates-rise",
                    "source": "Wall Street Journal"
                }
            ]
            st.info("Using demo financial news articles. Live data is currently unavailable.")
        
        return articles[:10]  # Return up to 10 articles
    
    except Exception as e:
        st.error(f"Error fetching financial news: {str(e)}")
        
        # Return demo articles as fallback
        return [
            {
                "title": "Markets Rally as Fed Signals Potential Rate Cuts",
                "link": "https://finance.yahoo.com/news/markets-rally-fed-signals-potential-rate-cuts",
                "source": "Yahoo Finance"
            },
            {
                "title": "Tech Stocks Lead Market Gains Amid AI Optimism",
                "link": "https://finance.yahoo.com/news/tech-stocks-lead-market-gains-ai-optimism",
                "source": "Reuters"
            },
            {
                "title": "Oil Prices Stabilize After Recent Volatility",
                "link": "https://finance.yahoo.com/news/oil-prices-stabilize-recent-volatility",
                "source": "Bloomberg"
            }
        ]

# Function for personal finance calculations
def calculate_savings(income, expenses):
    savings = income - expenses
    savings_rate = (savings / income) * 100 if income > 0 else 0
    return savings, savings_rate

# Function to generate chatbot responses
def generate_response(user_input):
    """Generate a response based on the user's input"""
    user_input = user_input.lower().strip()
    
    # Check for stock tickers (common ones)
    stock_tickers = {
        "aapl": "Apple Inc. (AAPL)",
        "msft": "Microsoft Corporation (MSFT)",
        "googl": "Alphabet Inc. (GOOGL)",
        "amzn": "Amazon.com Inc. (AMZN)",
        "tsla": "Tesla Inc. (TSLA)",
        "meta": "Meta Platforms Inc. (META)",
        "nvda": "NVIDIA Corporation (NVDA)",
        "nflx": "Netflix Inc. (NFLX)"
    }
    
    # Check if input is a stock ticker
    if user_input in stock_tickers:
        return f"Looking for information about {stock_tickers[user_input]}? Head to the Stock Lookup page and enter '{user_input.upper()}' to see current price, charts, and key metrics."
    
    # Dictionary of predefined responses for different types of queries
    responses = {
        "stock": [
            "To get stock information, go to the Stock Information page and enter a ticker symbol.",
            "I can help you find stock data. Try checking the Stock Information page and entering a ticker like 'AAPL' or 'MSFT'.",
            "Looking for stock data? Head to the Stock Information page and enter the ticker symbol you're interested in."
        ],
        "finance": [
            "For personal finance calculations, visit the Personal Finance page to track expenses and calculate savings.",
            "Need help with personal finance? Check out the Personal Finance page to manage your expenses and savings.",
            "Our Personal Finance tool can help you track expenses and calculate potential savings."
        ],
        "news": [
            "For the latest financial news, visit the Financial News page.",
            "Stay updated with financial news on our Financial News page. You can also search for specific topics.",
            "Check out the Financial News page for the latest updates on financial markets and trends."
        ],
        "hello": [
            "Hello! How can I help you with your financial questions today?",
            "Hi there! I'm your financial assistant. What would you like to know?",
            "Greetings! I'm here to help with your financial queries."
        ],
        "help": [
            "I can help you with stock information, personal finance calculations, and financial news. What would you like to know?",
            "Need help? You can ask me about stocks, personal finance, or financial news.",
            "I'm here to assist with your financial questions. Try asking about stocks, personal finance, or the latest news."
        ],
        "price": [
            "To check stock prices, go to the Stock Lookup page and enter a ticker symbol.",
            "You can find current stock prices on the Stock Lookup page. Just enter the ticker symbol you're interested in.",
            "Looking for stock prices? Head to the Stock Lookup page and enter a ticker like 'AAPL' or 'MSFT'."
        ],
        "invest": [
            "For investment information, check out our Stock Lookup page for current data and trends.",
            "Interested in investing? Our Stock Lookup page provides key metrics and price history for various stocks.",
            "Investment decisions should be based on thorough research. Our Stock Lookup page can help you get started with data."
        ],
        "budget": [
            "Need help with budgeting? Visit our Personal Finance page to track expenses and calculate savings.",
            "Budgeting is essential for financial health. Try our Personal Finance calculator to help manage your expenses.",
            "Our Personal Finance page can help you create a budget by tracking your income and expenses."
        ],
        "market": [
            "For market updates, check our Financial News page for the latest trends and information.",
            "Stay informed about market movements with our Financial News section.",
            "The market is always changing. Visit our Financial News page to stay updated."
        ]
    }
    
    # Check if any keywords match and return a response
    for keyword, reply_list in responses.items():
        if keyword in user_input.split():
            return random.choice(reply_list)
    
    # Check for partial matches in longer queries
    for keyword, reply_list in responses.items():
        if keyword in user_input:
            return random.choice(reply_list)
    
    # Default responses if no keywords match
    default_responses = [
        "I'm your financial assistant. Try asking about stocks, personal finance, or financial news.",
        "I can help with questions about stocks, personal finance, and financial news. What would you like to know?",
        "Not sure what you're asking. I can provide information about stocks, personal finance, and financial news.",
        "Try asking me about specific financial topics like stock prices, budgeting, or market news."
    ]
    
    return random.choice(default_responses)

# Home page
if page == "Home":
    st.title("💰 Simple Financial Assistant")
    st.write("Welcome to your financial assistant! This app helps you with:")
    
    # Create three columns for the main features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📈 Stock Information")
        st.write("Look up real-time stock data, charts, and key metrics.")
    
    with col2:
        st.markdown("### 💵 Personal Finance")
        st.write("Calculate savings, budget allocations, and financial goals.")
    
    with col3:
        st.markdown("### 📰 Financial News")
        st.write("Stay updated with the latest financial news and market trends.")
    
    # Quick stock check section
    st.subheader("Quick Stock Check")
    ticker = st.text_input("Enter a stock ticker (e.g., AAPL):", "").upper()
    
    if ticker:
        try:
            with st.spinner(f"Fetching data for {ticker}..."):
                stock, info, hist = get_stock_data(ticker)
                
                if stock is not None and info:
                    # Create two columns for basic info
                    quick_col1, quick_col2 = st.columns(2)
                    
                    with quick_col1:
                        st.metric(
                            label=f"{info.get('longName', ticker)}",
                            value=f"${info.get('regularMarketPrice', info.get('previousClose', 'N/A'))}"
                        )
                    
                    with quick_col2:
                        # Calculate daily change if possible
                        current = info.get('regularMarketPrice')
                        previous = info.get('previousClose')
                        
                        if current and previous and current != 'N/A' and previous != 'N/A':
                            change = current - previous
                            percent_change = (change / previous) * 100
                            st.metric(
                                label="Daily Change",
                                value=f"${change:.2f}",
                                delta=f"{percent_change:.2f}%"
                            )
                    
                    # Show a mini chart if we have historical data
                    if not hist.empty:
                        st.subheader("Recent Price History")
                        fig, ax = plt.subplots(figsize=(10, 4))
                        ax.plot(hist.index[-10:], hist['Close'][-10:])
                        ax.set_title(f"{ticker} Recent Price")
                        ax.grid(True)
                        st.pyplot(fig)
                        
                        # Add a button to go to detailed stock page
                        if st.button("View Detailed Stock Information"):
                            st.session_state.page = "Stock Lookup"
                            st.experimental_rerun()
                else:
                    st.error(f"Could not retrieve data for {ticker}. Please check the ticker symbol and try again.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please try another ticker symbol or check your internet connection.")

# Stock Lookup page
elif page == "Stock Lookup":
    def stock_information():
        st.header("📈 Stock Information")
        st.write("Look up real-time stock data, charts, and key metrics.")
        
        # User input for stock ticker
        ticker = st.text_input("Enter a stock ticker (e.g., AAPL):", "").upper()
        
        if ticker:
            with st.spinner(f"Fetching data for {ticker}..."):
                stock, info, hist = get_stock_data(ticker)
                
                if stock is not None and not hist.empty:
                    # Display basic stock information
                    st.subheader(f"{ticker} Stock Information")
                    
                    # Create columns for layout
                    col1, col2 = st.columns(2)
                    
                    # Display company name and sector if available
                    with col1:
                        if info.get('longName'):
                            st.write(f"**Company:** {info.get('longName', 'N/A')}")
                        if info.get('sector'):
                            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                    
                    # Display current price and market cap if available
                    with col2:
                        if 'regularMarketPrice' in info:
                            st.write(f"**Current Price:** ${info.get('regularMarketPrice', 'N/A'):.2f}")
                        elif not hist.empty:
                            st.write(f"**Last Close Price:** ${hist['Close'].iloc[-1]:.2f}")
                        
                        if 'marketCap' in info:
                            market_cap = info.get('marketCap', 0)
                            if market_cap > 1_000_000_000:
                                st.write(f"**Market Cap:** ${market_cap/1_000_000_000:.2f}B")
                            else:
                                st.write(f"**Market Cap:** ${market_cap/1_000_000:.2f}M")
                    
                    # Plot stock price history if we have data
                    if not hist.empty:
                        st.subheader("Price History")
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(hist.index, hist['Close'])
                        ax.set_title(f"{ticker} Stock Price")
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Price ($)")
                        ax.grid(True)
                        st.pyplot(fig)
                        
                        # Show additional metrics
                        st.subheader("Key Metrics")
                        metrics_col1, metrics_col2 = st.columns(2)
                        
                        with metrics_col1:
                            st.write(f"**52-Week High:** ${info.get('fiftyTwoWeekHigh', 'N/A')}")
                            st.write(f"**52-Week Low:** ${info.get('fiftyTwoWeekLow', 'N/A')}")
                            if 'dividendYield' in info and info['dividendYield'] is not None:
                                st.write(f"**Dividend Yield:** {info.get('dividendYield', 0) * 100:.2f}%")
                            else:
                                st.write("**Dividend Yield:** N/A")
                        
                        with metrics_col2:
                            st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
                            st.write(f"**Volume:** {info.get('volume', 'N/A')}")
                            st.write(f"**Avg Volume:** {info.get('averageVolume', 'N/A')}")
                    
                    # Show a brief business summary if available
                    if info.get('longBusinessSummary'):
                        st.subheader("Business Summary")
                        st.write(info.get('longBusinessSummary', 'No business summary available.'))
                else:
                    st.warning(f"Could not retrieve complete data for {ticker}. Please try another ticker or try again later.")
    
    stock_information()

# Personal Finance Calculator page
elif page == "Personal Finance Calculator":
    st.title("💰 Personal Finance Calculator")
    
    st.subheader("Monthly Budget Calculator")
    
    # Income inputs
    st.write("### Income")
    monthly_income = st.number_input("Monthly Income ($)", min_value=0.0, step=100.0)
    
    # Expense inputs
    st.write("### Expenses")
    col1, col2 = st.columns(2)
    
    with col1:
        housing = st.number_input("Housing/Rent ($)", min_value=0.0, step=10.0)
        utilities = st.number_input("Utilities ($)", min_value=0.0, step=10.0)
        food = st.number_input("Food/Groceries ($)", min_value=0.0, step=10.0)
        transportation = st.number_input("Transportation ($)", min_value=0.0, step=10.0)
    
    with col2:
        insurance = st.number_input("Insurance ($)", min_value=0.0, step=10.0)
        entertainment = st.number_input("Entertainment ($)", min_value=0.0, step=10.0)
        debt_payments = st.number_input("Debt Payments ($)", min_value=0.0, step=10.0)
        other = st.number_input("Other Expenses ($)", min_value=0.0, step=10.0)
    
    # Calculate total expenses
    total_expenses = housing + utilities + food + transportation + insurance + entertainment + debt_payments + other
    
    # Calculate savings
    if monthly_income > 0:
        savings, savings_rate = calculate_savings(monthly_income, total_expenses)
        
        st.subheader("Monthly Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"${monthly_income:.2f}")
        col2.metric("Total Expenses", f"${total_expenses:.2f}")
        col3.metric("Monthly Savings", f"${savings:.2f}")
        
        st.subheader("Savings Rate")
        st.progress(min(savings_rate/100, 1.0))
        st.write(f"Your savings rate is {savings_rate:.1f}%")
        
        if savings_rate < 10:
            st.warning("Your savings rate is low. Consider reducing expenses or increasing income.")
        elif savings_rate >= 20:
            st.success("Great job! You have a healthy savings rate.")
        
        # Expense breakdown chart
        st.subheader("Expense Breakdown")
        expense_data = {
            'Category': ['Housing', 'Utilities', 'Food', 'Transportation', 'Insurance', 'Entertainment', 'Debt', 'Other'],
            'Amount': [housing, utilities, food, transportation, insurance, entertainment, debt_payments, other]
        }
        expense_df = pd.DataFrame(expense_data)
        expense_df = expense_df[expense_df['Amount'] > 0]  # Only show categories with expenses
        
        if not expense_df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.pie(expense_df['Amount'], labels=expense_df['Category'], autopct='%1.1f%%')
            ax.axis('equal')
            st.pyplot(fig)
        
        # Investment projection
        st.subheader("Investment Projection")
        years = st.slider("Investment Timeline (Years)", 1, 40, 10)
        interest_rate = st.slider("Expected Annual Return (%)", 1.0, 15.0, 7.0)
        
        monthly_investment = savings
        future_value = 0
        
        for month in range(1, years * 12 + 1):
            future_value = future_value * (1 + interest_rate/100/12) + monthly_investment
        
        st.write(f"If you invest ${monthly_investment:.2f} monthly for {years} years at {interest_rate}% annual return:")
        st.write(f"Projected Future Value: **${future_value:,.2f}**")
        st.write(f"Total Contributions: **${monthly_investment * years * 12:,.2f}**")
        st.write(f"Investment Growth: **${future_value - (monthly_investment * years * 12):,.2f}**")

# Financial News page
elif page == "Financial News":
    st.title("📰 Financial News")
    st.write("Stay updated with the latest financial news and market trends.")
    
    # Allow user to search for specific news
    query = st.text_input("Search for specific financial news (leave empty for latest news):")
    
    if st.button("Get News") or not query:
        # Create demo news articles
        demo_articles = [
            {
                "title": "Markets Rally as Fed Signals Potential Rate Cuts",
                "link": "https://finance.yahoo.com/news/markets-rally-fed-signals-potential-rate-cuts",
                "source": "Yahoo Finance"
            },
            {
                "title": "Tech Stocks Lead Market Gains Amid AI Optimism",
                "link": "https://finance.yahoo.com/news/tech-stocks-lead-market-gains-ai-optimism",
                "source": "Reuters"
            },
            {
                "title": "Oil Prices Stabilize After Recent Volatility",
                "link": "https://finance.yahoo.com/news/oil-prices-stabilize-recent-volatility",
                "source": "Bloomberg"
            },
            {
                "title": "Retail Sales Exceed Expectations in Latest Report",
                "link": "https://finance.yahoo.com/news/retail-sales-exceed-expectations-latest-report",
                "source": "CNBC"
            },
            {
                "title": "Housing Market Shows Signs of Cooling as Mortgage Rates Rise",
                "link": "https://finance.yahoo.com/news/housing-market-shows-signs-cooling-mortgage-rates-rise",
                "source": "Wall Street Journal"
            }
        ]
        
        # Add search-specific articles if query is provided
        if query:
            # Create some demo articles related to the search query
            search_term = query.lower()
            
            if "crypto" in search_term or "bitcoin" in search_term:
                crypto_articles = [
                    {
                        "title": f"Bitcoin Surges Past $60,000 Amid Growing Institutional Interest",
                        "link": "https://finance.yahoo.com/news/bitcoin-surges-past-60000",
                        "source": "CoinDesk"
                    },
                    {
                        "title": f"Cryptocurrency Market Cap Exceeds $2 Trillion as Adoption Grows",
                        "link": "https://finance.yahoo.com/news/crypto-market-cap-exceeds-2-trillion",
                        "source": "Bloomberg"
                    },
                    {
                        "title": f"Regulators Consider New Framework for Cryptocurrency Oversight",
                        "link": "https://finance.yahoo.com/news/regulators-consider-new-framework-crypto",
                        "source": "Wall Street Journal"
                    }
                ]
                demo_articles = crypto_articles + demo_articles[:2]
            
            elif "stock" in search_term or "market" in search_term:
                stock_articles = [
                    {
                        "title": f"Stock Market Outlook: Analysts Predict Continued Growth Through Q4",
                        "link": "https://finance.yahoo.com/news/stock-market-outlook-q4",
                        "source": "Barron's"
                    },
                    {
                        "title": f"Market Volatility Increases as Earnings Season Approaches",
                        "link": "https://finance.yahoo.com/news/market-volatility-increases",
                        "source": "CNBC"
                    },
                    {
                        "title": f"Small-Cap Stocks Outperform as Economic Recovery Accelerates",
                        "link": "https://finance.yahoo.com/news/small-cap-stocks-outperform",
                        "source": "Motley Fool"
                    }
                ]
                demo_articles = stock_articles + demo_articles[:2]
            
            else:
                # Generic search results with the query term included
                custom_articles = [
                    {
                        "title": f"Latest Developments in {query.title()} Market Show Promising Trends",
                        "link": f"https://finance.yahoo.com/news/{query.lower().replace(' ', '-')}-market-trends",
                        "source": "Yahoo Finance"
                    },
                    {
                        "title": f"Investors Eye {query.title()} Sector for Growth Opportunities",
                        "link": f"https://finance.yahoo.com/news/investors-eye-{query.lower().replace(' ', '-')}-sector",
                        "source": "Reuters"
                    },
                    {
                        "title": f"Analysis: How {query.title()} Is Reshaping the Financial Landscape",
                        "link": f"https://finance.yahoo.com/news/analysis-{query.lower().replace(' ', '-')}-reshaping-finance",
                        "source": "Bloomberg"
                    }
                ]
                demo_articles = custom_articles + demo_articles[:2]
        
        st.info("Displaying demo financial news articles. Live data connection is currently unavailable.")
        
        # Display the articles
        st.success(f"Found {len(demo_articles)} articles" + (f" about '{query}'" if query else ""))
        
        # Display each article with a clickable link
        for i, article in enumerate(demo_articles, 1):
            with st.container():
                st.subheader(f"{i}. {article['title']}")
                st.write(f"**Source:** {article.get('source', 'Yahoo Finance')}")
                st.markdown(f"[Read full article]({article['link']})")
                st.divider()

# Chat Assistant page
elif page == "Chat Assistant":
    st.title("💬 Chat Assistant")
    st.write("Ask me anything about stocks, personal finance, or financial news.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Accept user input
    if prompt := st.chat_input("Ask a question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        response = generate_response(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
