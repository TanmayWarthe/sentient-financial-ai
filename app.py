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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')
log_level = config.get('DEFAULT', 'log_level', fallback='INFO')
logging.getLogger().setLevel(log_level)

# CLI support
def run_cli() -> None:
    """Run the CLI interface for StockSense AI."""
    parser = argparse.ArgumentParser(description="StockSense AI CLI")
    parser.add_argument('--symbol', type=str, help='Stock symbol, e.g. AAPL')
    parser.add_argument('--period', type=str, default='1mo', help='Time period, e.g. 1d, 1mo, 1y')
    args = parser.parse_args()

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
            print(hist_data.tail(5)[['Open', 'High', 'Low', 'Close', 'Volume']])
        else:
            print("No historical data found.")
    except Exception as e:
        print(f"Error: {e}")

# --- Streamlit App Logic ---
def run_streamlit_app():
    # Page setup
    st.set_page_config(
        page_title="StockSense AI",
        page_icon="📈",
        layout="wide"
    )

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