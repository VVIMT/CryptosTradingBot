import argparse
import asyncio
import os
from datetime import datetime
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
            since = deposits[-1]['timestamp'] + 1
        return all_deposits

    def calculate_pnl(self, deposits, exchange_rate_usd_to_eur):
        total_deposits_usd = sum(d['amount'] for d in deposits)
        total_pnl_eur = total_deposits_usd / exchange_rate_usd_to_eur if exchange_rate_usd_to_eur else None
        return total_pnl_eur

# Main function
async def main():
    args = parse_dates()
    exchange = None
    try:
        exchange = initialize_exchange(
            args.exchange, 
            os.getenv(f'{args.exchange.upper()}_API_KEY'), 
            os.getenv(f'{args.exchange.upper()}_API_SECRET')
        )
        pnl_tracker = PnLTracker(exchange)
        exchange_rate_usd_to_eur = await pnl_tracker.fetch_exchange_rate()
        deposits = await pnl_tracker.fetch_all_deposits(
            args.currency, start_date=args.start_date, end_date=args.end_date
        )
        pnl_eur = pnl_tracker.calculate_pnl(
            deposits, exchange_rate_usd_to_eur
        )
        print(f"PnL EUR: {pnl_eur}")
    finally:
        if exchange:
            await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
