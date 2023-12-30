import ccxt.pro as ccxtpro
import asyncio
import argparse

# Argument Parsing
parser = argparse.ArgumentParser(description="Fetch trading pairs from ByBit using CCXT Pro.")
parser.add_argument("--exchange", type=str, choices=["bybit", "binance"], required=True, help="Specify the exchange to fetch data from.")
parser.add_argument("--num_pairs", type=int, default=None, help="Number of trading pairs to display. If not specified, all pairs will be displayed.")
args = parser.parse_args()

# Control the Input
if args.num_pairs and args.num_pairs < 0:
    print("Error: The number of trading pairs cannot be negative.")
    exit(1)

exchange = getattr(ccxtpro, args.exchange)()

async def main():
    all_pairs = await fetch_all_trading_pairs(args.num_pairs)
    for pair in all_pairs:
        print(pair)
    await exchange.close()

async def fetch_all_trading_pairs(num_pairs=None):
    markets = await exchange.load_markets()
    trading_pairs = list(markets.keys())
    return trading_pairs[:num_pairs] if num_pairs else trading_pairs

if __name__ == "__main__":
    asyncio.run(main())