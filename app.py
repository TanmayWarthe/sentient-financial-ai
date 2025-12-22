#
# StockSense AI - Streamlit App
# A simple and elegant stock analysis tool.
# Built with Streamlit, yfinance, and Plotly.
# Provides stock analysis and visualization
#

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
import configparser
import argparse
import smtplib
from email.mime.text import MIMEText
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')
log_level = config.get('DEFAULT', 'log_level', fallback='INFO')
logging.getLogger().setLevel(log_level)

# --- Portfolio Tracker ---
class Portfolio:
    def __init__(self):
        self.stocks = {}

    def add_stock(self, symbol, shares):
        symbol = symbol.upper()
        self.stocks[symbol] = self.stocks.get(symbol, 0) + shares

    def remove_stock(self, symbol, shares):
        symbol = symbol.upper()
        if symbol in self.stocks:
            self.stocks[symbol] = max(0, self.stocks[symbol] - shares)
            if self.stocks[symbol] == 0:
                del self.stocks[symbol]

    def get_value(self):
        total = 0
        for symbol, shares in self.stocks.items():
            try:
                price = yf.Ticker(symbol).info.get('currentPrice', 0)
                total += price * shares
            except Exception:
                continue
        return total

    def get_holdings(self):
        return self.stocks.copy()

# --- News & Sentiment Analysis ---
def fetch_news(symbol):
    # Example: Use NewsAPI or similar (replace with your API key)
    api_key = config.get('NEWS', 'api_key', fallback=None)
    if not api_key:
        return []
    url = f'https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key}&language=en'
    try:
        resp = requests.get(url)
        articles = resp.json().get('articles', [])
        return articles[:5]
    except Exception:
        return []

def simple_sentiment(text):
    # Very basic sentiment: positive if 'up', negative if 'down', neutral otherwise
    text = text.lower()
    if 'up' in text or 'gain' in text:
        return 'Positive'
    if 'down' in text or 'loss' in text:
        return 'Negative'
    return 'Neutral'

# --- Email Alerts ---
def send_email_alert(to_email, subject, body):
    smtp_server = config.get('EMAIL', 'smtp_server', fallback=None)
    smtp_port = config.getint('EMAIL', 'smtp_port', fallback=587)
    smtp_user = config.get('EMAIL', 'smtp_user', fallback=None)
    smtp_pass = config.get('EMAIL', 'smtp_pass', fallback=None)
    if not all([smtp_server, smtp_user, smtp_pass, to_email]):
        return False
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        return True
    except Exception:
        return False

# --- Technical Indicators ---
def add_technical_indicators(df):
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

# CLI support
def run_cli() -> None:
    """Run the CLI interface for StockSense AI."""
    parser = argparse.ArgumentParser(description="StockSense AI CLI")
    parser.add_argument('--symbol', type=str, help='Stock symbol, e.g. AAPL')
    parser.add_argument('--period', type=str, default='1mo', help='Time period, e.g. 1d, 1mo, 1y')
    parser.add_argument('--portfolio', action='store_true', help='Show portfolio tracker')
    args = parser.parse_args()

    if args.portfolio:
        print("Portfolio tracker is available in the Streamlit app.")
        return
    if not args.symbol:
        print("Please provide a stock symbol with --symbol")
        return
    stock_symbol: str = args.symbol.upper()
    period: str = args.period
    print(f"Fetching {stock_symbol} data for {period}...")
    try:
        stock = yf.Ticker(stock_symbol)
        info = stock.info
        print(f"Current Price: ${info.get('currentPrice', 'N/A')}")
        print(f"Market Cap: ${info.get('marketCap', 'N/A')}")
        print(f"PE Ratio: {info.get('trailingPE', 'N/A')}")
        hist_data = stock.history(period=period)
        if not hist_data.empty:
            hist_data = add_technical_indicators(hist_data)
            print(hist_data.tail(5)[['Open', 'High', 'Low', 'Close', 'Volume', 'MA20', 'MA50', 'RSI']])
        else:
            print("No historical data found.")
    except Exception as e:
        print(f"Error: {e}")

# --- Streamlit App Logic ---
def run_streamlit_app():
    st.set_page_config(
        page_title="StockSense AI",
        page_icon="📈",
        layout="wide"
    )
    st.title("StockSense AI: Autonomous Financial Analyst")
    st.markdown("""
        **Features:**
        - Portfolio tracker
        - News & sentiment analysis
        - Email alerts
        - Technical indicators (MA, RSI)
    """)

    # Portfolio tracker (session state)
    if 'portfolio' not in st.session_state:
        st.session_state['portfolio'] = Portfolio()
    portfolio = st.session_state['portfolio']

    st.sidebar.header("Portfolio Tracker")
    with st.sidebar.form("add_stock_form"):
        symbol = st.text_input("Stock Symbol", "AAPL")
        shares = st.number_input("Shares", min_value=1, value=1)
        add = st.form_submit_button("Add to Portfolio")
        if add:
            portfolio.add_stock(symbol, shares)
            st.success(f"Added {shares} shares of {symbol.upper()} to portfolio.")
    if portfolio.get_holdings():
        st.sidebar.write("### Holdings:")
        for sym, sh in portfolio.get_holdings().items():
            st.sidebar.write(f"{sym}: {sh} shares")
        st.sidebar.write(f"**Total Value:** ${portfolio.get_value():,.2f}")
    else:
        st.sidebar.write("No holdings yet.")

    # Main stock analysis
    st.header("Stock Analysis")
    stock_symbol = st.text_input("Enter Stock Symbol", "AAPL")
    period = st.selectbox("Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"], index=2)
    show = st.button("Analyze")
    if show:
        try:
            stock = yf.Ticker(stock_symbol)
            info = stock.info
            st.write(f"### {stock_symbol} - {info.get('shortName', '')}")
            st.write(f"Current Price: ${info.get('currentPrice', 'N/A')}")
            st.write(f"Market Cap: ${info.get('marketCap', 'N/A')}")
            st.write(f"PE Ratio: {info.get('trailingPE', 'N/A')}")
            hist_data = stock.history(period=period)
            if not hist_data.empty:
                hist_data = add_technical_indicators(hist_data)
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=hist_data.index, open=hist_data['Open'], high=hist_data['High'], low=hist_data['Low'], close=hist_data['Close'], name='Price'))
                fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA20'], mode='lines', name='MA20'))
                fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA50'], mode='lines', name='MA50'))
                st.plotly_chart(fig, use_container_width=True)
                st.line_chart(hist_data['RSI'], use_container_width=True)
            else:
                st.warning("No historical data found.")
        except Exception as e:
            st.error(f"Error: {e}")

        # News & Sentiment
        st.subheader("Latest News & Sentiment")
        news = fetch_news(stock_symbol)
        if news:
            for article in news:
                sentiment = simple_sentiment(article.get('title', ''))
                st.write(f"- [{article.get('title')}]({article.get('url')}) ({sentiment})")
        else:
            st.info("No news found or NewsAPI key missing.")

        # Email alert
        st.subheader("Set Price Alert (Email)")
        alert_email = st.text_input("Your Email", "")
        alert_price = st.number_input("Alert me if price goes above:", min_value=0.0, value=0.0)
        if st.button("Set Alert") and alert_email and info.get('currentPrice') and alert_price > 0:
            if info.get('currentPrice') > alert_price:
                sent = send_email_alert(alert_email, f"{stock_symbol} Price Alert", f"{stock_symbol} is now at ${info.get('currentPrice')}")
                if sent:
                    st.success("Alert sent!")
                else:
                    st.error("Failed to send alert. Check email config.")
            else:
                st.info(f"Current price (${info.get('currentPrice')}) is below alert threshold.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_cli()
    else:
        run_streamlit_app()

    # Title
    st.title("📈 StockSense AI")
    st.markdown("**Simple stock analysis tool**")

    # Sidebar for inputs
    with st.sidebar:
        st.header("Settings")
        # Stock input
        stock_symbol = st.text_input(
            "Stock Symbol",
            value="AAPL",
            help="Enter like: AAPL, TSLA, GOOGL, RELIANCE.NS"
        ).upper()
        # Time period
        period = st.selectbox(
            "Time Period",
            ["1d", "5d", "1mo", "3mo", "6mo", "1y"],
            index=2
        )
        # Analyze button
        analyze_btn = st.button("🚀 Analyze Stock", type="primary")

    # Main content
    if analyze_btn or stock_symbol:
        # Show loading
        with st.spinner(f"Fetching {stock_symbol} data..."):
            try:
                # Get stock data
                stock = yf.Ticker(stock_symbol)
                info = stock.info
                # Create columns for layout
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        label="Current Price",
                        value=f"${info.get('currentPrice', 'N/A')}",
                        delta=f"{info.get('regularMarketChangePercent', 0):.2f}%"
                    )
                with col2:
                    st.metric(
                        label="Market Cap",
                        value=f"${info.get('marketCap', 0)/1e9:.1f}B" if info.get('marketCap') else "N/A"
                    )
                with col3:
                    st.metric(
                        label="PE Ratio",
                        value=f"{info.get('trailingPE', 'N/A')}"
                    )
                # Price chart
                st.subheader("📊 Price Chart")
                hist_data = stock.history(period=period)
                if not hist_data.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['Close'],
                        mode='lines',
                        name='Price',
                        line=dict(color='green')
                    ))
                    fig.update_layout(
                        title=f"{stock_symbol} Price History",
                        xaxis_title="Date",
                        yaxis_title="Price ($)",
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                # Company info
                st.subheader("🏢 Company Information")
                col4, col5 = st.columns(2)
                with col4:
                    st.write(f"**Name:** {info.get('longName', stock_symbol)}")
                    st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                    st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                with col5:
                    st.write(f"**52W High:** ${info.get('fiftyTwoWeekHigh', 'N/A')}")
                    st.write(f"**52W Low:** ${info.get('fiftyTwoWeekLow', 'N/A')}")
                    st.write(f"**Volume:** {info.get('volume', 'N/A'):,}")
                # Data table
                st.subheader("📋 Historical Data")
                st.dataframe(
                    hist_data.tail(10)[['Open', 'High', 'Low', 'Close', 'Volume']],
                    use_container_width=True
                )
            except Exception as e:
                logging.error(f"Error fetching data for {stock_symbol}: {e}")
                st.error(f"An error occurred while fetching data for {stock_symbol}. Please check the stock symbol and your internet connection.")
                st.info("Example symbols: AAPL, TSLA, GOOGL, RELIANCE.NS")
    # If no button clicked yet
    else:
        st.info("👈 Enter stock symbol in sidebar and click 'Analyze Stock'")
        # Sample stocks
        st.subheader("Try these stocks:")
        cols = st.columns(4)
        sample_stocks = ["AAPL", "TSLA", "GOOGL", "MSFT"]
        for col, stock in zip(cols, sample_stocks):
            with col:
                if st.button(stock):
                    st.session_state.stock_symbol = stock
                    st.rerun()
    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_cli()
    else:
        run_streamlit_app()