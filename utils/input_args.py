import argparse
import logging
import ccxt

def parse_args():
    parser = argparse.ArgumentParser(description="A trading bot using CCXT Pro for real-time data from exchanges.")
    parser.add_argument("--mode", type=str, choices=["feed_model", "gather_data"], default="feed_model", help="Choose between 'feed_model' and 'gather_data' modes.")
    parser.add_argument("--debug_mode", type=bool, default=False, help="Enable debug mode for verbose logging.")
    parser.add_argument("--batch_size", type=int, default=1000, help="Specify the batch size for saving data to CSV.")
    parser.add_argument("--exchange", type=str, choices=["bybit", "binance"], required=True, help="Specify the exchange to fetch data from.")
    parser.add_argument("--symbol", type=str, default="BTC/USDT", help="Specify the trading pair to fetch data for, e.g., 'BTC/USD'.")
    parser.add_argument("--category", type=str, choices=["spot", "linear", "inverse", "option"], help="Specify the product type.")
    parser.add_argument("--depth", type=int, default=50, help="Specify the depth of the order book to fetch.")
    parser.add_argument("--hours", type=int, default=0, help="Specify the number of hours to run the bot.")
    parser.add_argument("--minutes", type=int, default=0, help="Specify the number of minutes to run the bot.")
    parser.add_argument("--seconds", type=int, default=5, help="Specify the number of seconds to run the bot.")
    parser.add_argument("--print", type=int, default=0, help="Specify the number of lines of the pandas table to print.")
    args = parser.parse_args()

    # Control the Input Values
    if args.print < 0:
        logging.error("Error: The --print value cannot be negative.")
        exit(1)
    if args.hours < 0 or args.minutes < 0 or args.seconds < 0:
        logging.error("Error: Time values cannot be negative.")
        exit(1)
    if args.depth <= 0:
        logging.error("Error: Order book depth must be a positive integer.")
        exit(1)

    # Fetch all trading pairs for validation
    exchange_sync = getattr(ccxt, args.exchange)()
    all_pairs = list(exchange_sync.load_markets().keys())
    if args.symbol not in all_pairs:
        logging.error("Error: Invalid trading pair.")
        exit(1)

    return args
