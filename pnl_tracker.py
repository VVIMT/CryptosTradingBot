import argparse
from datetime import datetime
import asyncio
import os
from core.exchange_init import initialize_exchange

# Function to parse command-line arguments for date range
def parse_dates():
    parser = argparse.ArgumentParser(
        description='Track profit and loss within a specified date range.'
    )
    parser.add_argument('--start-date', type=str, help='Start date for PnL calculation in YYYY-MM-DD format.')
    parser.add_argument('--end-date', type=str, help='End date for PnL calculation in YYYY-MM-DD format.')
    parser.add_argument('--exchange', type=str, required=True, help='Specify the exchange to use.')
    parser.add_argument('--currency', type=str, required=True, help='Specify the currency code for deposits.')
    return parser.parse_args()

# Function to convert date string to timestamp
def str_to_timestamp(date_str):
    if date_str:
        return int(datetime.strptime(date_str, '%Y-%m-%d').timestamp()) * 1000
    return None

# PnL Tracker class
class PnLTracker:
    def __init__(self, exchange):
        self.exchange = exchange
        self.trades = []
        self.deposits = []

    async def fetch_exchange_rate(self):
        ticker = await self.exchange.fetch_ticker('USDT/EUR')
        return ticker['last'] if ticker['last'] else None

    async def fetch_all_deposits(self, currency_code, start_date=None, end_date=None):
        all_deposits = []
        since = str_to_timestamp(start_date) if start_date else None
        until = str_to_timestamp(end_date) if end_date else datetime.now().timestamp() * 1000
        while True:
            deposits = await self.exchange.fetch_deposits(
                code=currency_code, since=since, limit=50
            )
            if not deposits:
                break
            all_deposits.extend(deposits)
            # Update 'since' to fetch next batch of deposits if there are more than 50
            since = deposits[-1]['timestamp'] + 1
        self.deposits = all_deposits

    def calculate_pnl(self, exchange_rate_usd_to_eur, start_date=None, end_date=None):
        start_ts = str_to_timestamp(start_date) if start_date else None
        end_ts = str_to_timestamp(end_date) if end_date else None
        filtered_trades = [
            t for t in self.trades if 
            (not start_ts or t['timestamp'] >= start_ts) and 
            (not end_ts or t['timestamp'] <= end_ts)
        ]
        total_pnl_usd = sum(
            (t['price'] - t['cost']) * t['amount'] for t in filtered_trades
        )
        # Convert USD PnL to EUR using the fetched exchange rate
        total_pnl_eur = total_pnl_usd / exchange_rate_usd_to_eur if exchange_rate_usd_to_eur else None
        return total_pnl_usd, total_pnl_eur

# Main function
async def main():
    args = parse_dates()
    exchange = initialize_exchange(
        args.exchange, 
        os.getenv(f'{args.exchange.upper()}_API_KEY'), 
        os.getenv(f'{args.exchange.upper()}_API_SECRET')
    )
    pnl_tracker = PnLTracker(exchange)
    exchange_rate_usd_to_eur = await pnl_tracker.fetch_exchange_rate()
    await pnl_tracker.fetch_all_deposits(
        args.currency, start_date=args.start_date, end_date=args.end_date
    )
    pnl_usd, pnl_eur = pnl_tracker.calculate_pnl(
        exchange_rate_usd_to_eur, 
        start_date=args.start_date, 
        end_date=args.end_date
    )
    print(f"PnL USD: {pnl_usd}, PnL EUR: {pnl_eur}")
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
