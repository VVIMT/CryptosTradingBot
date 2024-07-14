import pandas as pd
import numpy as np
import ccxt
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def fetch_historical_data(symbol, exchange_name, timeframe='1m', limit=100):
    exchange = getattr(ccxt, exchange_name)()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    return data

def calculate_returns(data):
    data['returns'] = data['close'].pct_change()
    return data

def calculate_volatility(returns):
    return returns.std()  # Volatility without annualizing

def compute_portfolio_volatility(assets, exchange_name, limit=100):
    all_returns = []
    individual_volatilities = {}
    
    for symbol in assets:
        try:
            data = fetch_historical_data(symbol, exchange_name, limit=limit)
            data = calculate_returns(data)
            volatility = calculate_volatility(data['returns'])
            individual_volatilities[symbol] = volatility
            all_returns.append(data['returns'])
        except ccxt.BaseError as e:
            print(f"Error fetching data for {symbol}: {e}")
    
    # Create a DataFrame to hold the returns of all assets
    returns_df = pd.concat(all_returns, axis=1)
    returns_df.columns = [symbol for symbol in individual_volatilities.keys()]
    
    # Calculate the portfolio returns by averaging the returns of individual assets
    portfolio_returns = returns_df.mean(axis=1)
    
    # Calculate the volatility of the portfolio returns
    portfolio_volatility = calculate_volatility(portfolio_returns)
    
    return portfolio_volatility, individual_volatilities

def get_top_symbols(exchange_name, top_n=10):
    exchange = getattr(ccxt, exchange_name)()
    markets = exchange.load_markets()
    symbols = [symbol for symbol in markets if 'USDT' in symbol and '/USDT' in symbol]
    if 'USDC/USDT' in symbols:
        symbols.remove('USDC/USDT')  # Remove USDC/USDT pair
    return symbols[:top_n]

# Example usage:
if __name__ == "__main__":
    exchange_name = 'bybit'  # Exchange name supported by ccxt
    assets = get_top_symbols(exchange_name, top_n=100)
    observation_window = 10080  # Number of minutes to look back
    portfolio_volatility, individual_volatilities = compute_portfolio_volatility(assets, exchange_name, limit=observation_window)

    # Add portfolio volatility to the dictionary
    individual_volatilities['Portfolio'] = portfolio_volatility

    # Sort volatilities from lowest to highest
    sorted_volatilities = sorted(individual_volatilities.items(), key=lambda x: x[1])

    # Display the sorted volatilities
    for asset, vol in sorted_volatilities:
        if asset == 'Portfolio':
            print(Fore.GREEN + f'Volatility of {asset}: {vol}')
        else:
            print(f'Volatility of {asset}: {vol}')
