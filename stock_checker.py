import yfinance as yf
import pandas as pd
from datetime import datetime

print("=" * 50)
print("STOCK PRICE CHECKER - By YourName")
print("=" * 50)

# User se stock symbol poocho
stock_symbol = input("\nStock ka symbol daalo (jaise AAPL, TSLA, GOOGL): ").upper()

# User se comparison ke liye dusra stock poocho
compare_with = input(f"\n{stock_symbol} ko kis stock se compare karna hai? (Enter chhod do agar nahi karna): ").upper() or None

print(f"\n📡 {stock_symbol} ka data fetch kar raha hu...")

try:
    # Stock data lo
    stock = yf.Ticker(stock_symbol)
    
    # Basic info
    info = stock.info
    
    # Current price
    current_price = info.get('currentPrice', 'N/A')
    
    # Previous close
    prev_close = info.get('regularMarketPreviousClose', 'N/A')
    
    # Day change calculate karo
    if current_price != 'N/A' and prev_close != 'N/A':
        change = current_price - prev_close
        change_percent = (change / prev_close) * 100
    else:
        change = 'N/A'
        change_percent = 'N/A'
    
    # Company name
    company_name = info.get('longName', stock_symbol)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Kya stock symbol sahi hai? (AAPL, TSLA, MSFT, etc.)")
    exit()


    print("\n" + "=" * 50)
print(f"📊 ANALYSIS: {company_name} ({stock_symbol})")
print("=" * 50)

print(f"\n💰 Current Price: ${current_price:.2f}" if current_price != 'N/A' else f"\n💰 Current Price: {current_price}")
print(f"📅 Previous Close: ${prev_close:.2f}" if prev_close != 'N/A' else f"📅 Previous Close: {prev_close}")

if change != 'N/A':
    # Color coding
    if change > 0:
        print(f"📈 Today's Change: +${change:.2f} ({change_percent:+.2f}%)")
    elif change < 0:
        print(f"📉 Today's Change: -${abs(change):.2f} ({change_percent:.2f}%)")
    else:
        print(f"➡️  Today's Change: ${change:.2f} ({change_percent:.2f}%)")

# Additional info
print(f"\n📈 52-Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}")
print(f"📉 52-Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}")
print(f"🏢 Market Cap: ${info.get('marketCap', 'N/A'):,}")
print(f"📊 PE Ratio: {info.get('trailingPE', 'N/A')}")

# Simple recommendation
print("\n" + "-" * 30)
print("💡 SIMPLE ANALYSIS:")
if current_price != 'N/A' and prev_close != 'N/A':
    if change_percent > 2:
        print("🔴 Aaj UP hai, wait karo thoda")
    elif change_percent < -2:
        print("🟢 Aaj DOWN hai, opportunity ho sakta")
    else:
        print("🟡 Stable hai, research karo")
else:
    print("Data nahi mila, check karo stock symbol")


# Agar comparison chahiye
if compare_with:
    print("\n" + "=" * 50)
    print(f"🔄 COMPARING: {stock_symbol} vs {compare_with}")
    print("=" * 50)
    
    try:
        compare_stock = yf.Ticker(compare_with)
        compare_info = compare_stock.info
        
        print(f"\n{stock_symbol}:")
        print(f"  Price: ${current_price:.2f}" if current_price != 'N/A' else f"  Price: {current_price}")
        print(f"  PE Ratio: {info.get('trailingPE', 'N/A')}")
        
        print(f"\n{compare_with}:")
        print(f"  Price: ${compare_info.get('currentPrice', 'N/A'):.2f}" if compare_info.get('currentPrice') else f"  Price: {compare_info.get('currentPrice', 'N/A')}")
        print(f"  PE Ratio: {compare_info.get('trailingPE', 'N/A')}")
        
        # Simple comparison
        price1 = current_price if current_price != 'N/A' else 0
        price2 = compare_info.get('currentPrice', 0) if compare_info.get('currentPrice') else 0
        
        if price1 and price2:
            if price1 > price2:
                print(f"\n{stock_symbol} {price1/price2:.1f}x mehenga hai {compare_with} se")
            else:
                print(f"\n{stock_symbol} {price2/price1:.1f}x sasta hai {compare_with} se")
                
    except:
        print(f"\n❌ {compare_with} ka data nahi mila")


# Save to file option
save_option = input("\n📁 Result file mein save karna hai? (y/n): ").lower()
if save_option == 'y':
    filename = f"stock_analysis_{stock_symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Stock Analysis Report\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Stock: {company_name} ({stock_symbol})\n")
        f.write(f"Price: ${current_price}\n")
        f.write(f"Change: {change_percent}%\n")
    print(f"✅ Saved to: {filename}")

print("\n" + "=" * 50)
print("✅ Analysis Complete!")
print("=" * 50)