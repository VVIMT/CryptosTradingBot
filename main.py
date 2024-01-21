import asyncio
import os
import logging
from queue import Queue
from threading import Thread
import pandas as pd
from core.exchange_init import initialize_exchange
from core.exchange import fetch_orderbook
from core.data_writer import writer_thread, data_file
from utils.monitoring import print_resources_consumption
from utils.input_args import parse_args

class SharedState:
    def __init__(self):
        self.registering = True
        self.orderbooks_df = pd.DataFrame()
        self.id_counter = 0
        self.csv_filepath = None
        self.data_queue = Queue()

# Set up logging
logging.basicConfig(level=logging.INFO)
# Parse command-line arguments
args = parse_args()

async def window(state, hours, minutes, seconds):
    total_seconds = hours * 3600 + minutes * 60 + seconds
    await asyncio.sleep(total_seconds)
    state.registering = False

def main():
    state = SharedState()
    # Initialize the exchange
    API_KEY = os.environ.get(f'{args.exchange.upper()}_API_KEY')
    API_SECRET = os.environ.get(f'{args.exchange.upper()}_API_SECRET')
    exchange = initialize_exchange(args.exchange, API_KEY, API_SECRET)

    if args.mode == "gather_data":
        state.csv_filepath = data_file(args)
        # Start writer thread
        writer_thread_obj = Thread(target=writer_thread, args=(state.data_queue, state.csv_filepath))
        writer_thread_obj.daemon = True
        writer_thread_obj.start()

    loop = asyncio.get_event_loop()
    loop.create_task(window(state, hours=args.hours, minutes=args.minutes, seconds=args.seconds))
    loop.run_until_complete(fetch_orderbook(state, exchange, args))

    if args.mode == "gather_data" and not state.orderbooks_df.empty:
        with open(state.csv_filepath, mode='a', newline='') as file:
            state.orderbooks_df.to_csv(file, index=False, header=False)
        logging.info(f"Data saved to {state.csv_filepath}")
        if args.print > 0:
            print(state.orderbooks_df.head(args.print))

    print_resources_consumption()
    loop.run_until_complete(exchange.close())

if __name__ == "__main__":
    main()