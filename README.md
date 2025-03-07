# Financial Chatbot

A streamlined financial application that provides essential financial tools in a user-friendly interface.

## Features

- **Stock Information**: Look up stock data, price charts, and key metrics
- **Personal Finance Calculator**: Track expenses, visualize spending, and calculate savings
- **Financial News**: Browse the latest financial news and market trends

## Key Benefits

- **Reliability**: Uses demo data for common stocks (AAPL, MSFT, GOOGL, AMZN, TSLA) to ensure consistent results
- **Simplicity**: Clean, intuitive interface with straightforward navigation
- **Offline Functionality**: Works even when external data sources are unavailable

## Important Notes

- This application uses demo data for several common stocks to ensure reliability
- For other stocks, it attempts to fetch real-time data but falls back to simulated data if needed
- The financial news section displays curated demo articles that are relevant to your search terms

## Setup Instructions

1. Create a virtual environment:
   ```
   python -m venv finance_env
   ```

2. Activate the virtual environment:
   ```
   .\finance_env\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   streamlit run app.py
   ```

## Development Status

This project is under active development. Future enhancements may include:
- User authentication for saving personal finance data
- Portfolio tracking functionality
- More advanced stock analysis tools
- Integration with additional financial data sources
- Enhanced chatbot functionality with financial advice