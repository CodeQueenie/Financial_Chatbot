import pandas as pd
from yahoo_fin.stock_info import get_data

def load_ticker_list():
    """Loads the list of stock tickers from Excel."""
    try:
        df_tickers = pd.read_excel("Data/nasdaq_ticker.xlsx")
        return df_tickers["Symbol"].tolist()
    except FileNotFoundError:
        print("⚠️ Error: 'nasdaq_ticker.xlsx' not found in Data folder.")
        return None

def get_ticker_history(ticker, start_date):
    """Fetches historical stock data from Yahoo Finance."""
    try:
        df_data = get_data(ticker)
        df_data.reset_index(inplace=True)

        # Filter data from the start date
        df_data = df_data[df_data["index"] >= start_date]
        return df_data
    except Exception as e:
        print(f"⚠️ Error retrieving data for {ticker}: {e}")
        return None

def generate_ticker_history():
    """Generates and saves historical stock data for all tickers."""
    tickers = load_ticker_list()
    if tickers is None:
        return

    start_date = "2023-12-08"
    df = pd.DataFrame()

    for ticker in tickers:
        stock_data = get_ticker_history(ticker, start_date)
        if stock_data is not None:
            df = pd.concat([df, stock_data], axis=0, ignore_index=True)

    # Save to CSV
    if not df.empty:
        df.rename(columns={"index": "date"}, inplace=True)
        df.to_csv("Data/ticker_history.csv", index=False)
        print("✅ Stock history updated successfully!")

# Run only if the script is executed directly
if __name__ == "__main__":
    generate_ticker_history()