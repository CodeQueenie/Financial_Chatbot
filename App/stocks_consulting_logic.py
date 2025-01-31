import streamlit as st
from datetime import date, timedelta
import pandas as pd
import warnings
from yahoofinancials import YahooFinancials

warnings.simplefilter(action='ignore', category=FutureWarning)

def get_previous_day():
    """Returns the previous day's date."""
    return str(date.today() - timedelta(days=1))

def request_data(ticker):
    """Fetch financial data from YahooFinancials API."""
    try:
        yf = YahooFinancials(ticker)
        data_income = yf.get_financial_stmts('annual', 'income')['incomeStatementHistory'].get(ticker, None)
        data_cash = yf.get_financial_stmts('annual', 'cash')['cashflowStatementHistory'].get(ticker, None)
        data_balance = yf.get_financial_stmts('annual', 'balance')['balanceSheetHistory'].get(ticker, None)
        stock_history = yf.get_historical_price_data(
            start_date=get_previous_day(),
            end_date=str(date.today()),
            time_interval="daily"
        ).get(ticker, None)

        if not data_income or not data_cash or not data_balance or not stock_history:
            raise ValueError("Invalid ticker or missing data.")

        return data_income, data_cash, data_balance, stock_history
    except Exception:
        return None, None, None, None

def get_most_recent_report(data):
    """Retrieve the most recent financial report available."""
    if not data:
        return None
    try:
        all_dates = [key for dico in data for key in dico.keys()]
        max_date = max(all_dates)
        return next((entry[max_date] for entry in data if max_date in entry), None)
    except Exception:
        return None

def fetch_financial_data(ticker):
    """Fetch stock data and store in Streamlit session state."""
    data_income, data_cash, data_balance, stock_history = request_data(ticker.strip())

    if data_income and data_cash and data_balance and stock_history:
        st.session_state["data_income"] = data_income
        st.session_state["data_cash"] = data_cash
        st.session_state["data_balance"] = data_balance
        st.session_state["stock_history"] = stock_history
        return True
    return False

def get_safe_value(key, category):
    """Safely retrieve a financial metric to prevent errors from missing data."""
    try:
        return get_most_recent_report(st.session_state[category])[key]
    except (TypeError, KeyError, IndexError):
        return "N/A"

def get_today_stock():
    """Retrieve today's stock price."""
    try:
        return f"{st.session_state['stock_history']['prices'][0]['close']:.2f} $"
    except (TypeError, KeyError, IndexError):
        return "N/A"

# The main function for the Stocks Consulting page
def run_stocks_consulting_page():
    st.title("📈 Stocks Consulting")
    st.write("Welcome to the Stocks Consulting page! Enter a stock ticker to see financial indicators.")

    # Get Ticker from the User
    ticker = st.text_input("Enter a Ticker Symbol (e.g., AAPL, MSFT, GOOGL):", key="ticker_input").upper()

    if ticker:
        if fetch_financial_data(ticker):
            st.write("## Available Indicators")
            indicators = [
                "Change ticker", "Stock price", "Turnover", "Net Turnover", "Gross margin",
                "Net margin", "Operating margin", "ROE (Return on Equity)", "ROA (Return on Assets)",
                "Payout Ratio", "PER (Price Earnings Ratio)", "Free Cash-Flow", "Ratio Equity/Debt",
                "All of the above"
            ]

            selected_indicator = st.selectbox("Select an indicator to retrieve:", indicators, index=1)

            # Display the Selected Indicator
            if selected_indicator == "Change ticker":
                st.warning("Please enter a new ticker above.")
            elif selected_indicator == "Stock price":
                st.info(f"Stock Price: {get_today_stock()}")
            elif selected_indicator == "Turnover":
                st.info(f"Turnover: {get_safe_value('totalRevenue', 'data_income')} $")
            elif selected_indicator == "Net Turnover":
                st.info(f"Net Turnover: {get_safe_value('netIncome', 'data_income')} $")
            elif selected_indicator == "Gross margin":
                st.info(f"Gross Margin: {get_safe_value('grossProfit', 'data_income')} %")
            elif selected_indicator == "Net margin":
                st.info(f"Net Margin: {get_safe_value('netIncome', 'data_income')} %")
            elif selected_indicator == "Operating margin":
                st.info(f"Operating Margin: {get_safe_value('ebit', 'data_income')} %")
            elif selected_indicator == "ROE (Return on Equity)":
                st.info(f"ROE: {get_safe_value('stockholdersEquity', 'data_balance')} %")
            elif selected_indicator == "ROA (Return on Assets)":
                st.info(f"ROA: {get_safe_value('totalAssets', 'data_balance')} %")
            elif selected_indicator == "Payout Ratio":
                st.info(f"Payout Ratio: {get_safe_value('cashDividendsPaid', 'data_cash')} %")
            elif selected_indicator == "PER (Price Earnings Ratio)":
                st.info(f"PER: {get_safe_value('totalCapitalization', 'data_balance')} %")
            elif selected_indicator == "Free Cash-Flow":
                st.info(f"Free Cash-Flow: {get_safe_value('freeCashFlow', 'data_cash')} $")
            elif selected_indicator == "Ratio Equity/Debt":
                st.info(f"Ratio Equity/Debt: {get_safe_value('longTermDebt', 'data_balance')} %")
            elif selected_indicator == "All of the above":
                df = pd.DataFrame({
                    "Stock of the day": [get_today_stock()],
                    "Gross turnover": [get_safe_value('totalRevenue', 'data_income')],
                    "Net turnover": [get_safe_value('netIncome', 'data_income')],
                    "Gross margin": [get_safe_value('grossProfit', 'data_income')],
                    "Net margin": [get_safe_value('netIncome', 'data_income')],
                    "Operating margin": [get_safe_value('ebit', 'data_income')],
                    "ROE (Return on Equity)": [get_safe_value('stockholdersEquity', 'data_balance')],
                    "ROA (Return on Assets)": [get_safe_value('totalAssets', 'data_balance')],
                    "Payout Ratio": [get_safe_value('cashDividendsPaid', 'data_cash')],
                    "PER (Price Earnings Ratio)": [get_safe_value('totalCapitalization', 'data_balance')],
                    "Free Cash-Flow": [get_safe_value('freeCashFlow', 'data_cash')],
                    "Ratio Debt/Equity": [get_safe_value('longTermDebt', 'data_balance')]
                })
                st.table(df)

        else:
            st.error(f"Couldn't retrieve data for ticker '{ticker}'. Please check spelling or try another.")

    else:
        st.info("Please enter a ticker symbol above to retrieve stock data.")