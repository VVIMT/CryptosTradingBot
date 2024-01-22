import asyncio
import os
from queue import Queue
from threading import Thread
import pandas as pd
import logging
from core.exchange_init import initialize_exchange
from core.exchange import fetch_orderbook
from core.data_writer import writer_thread, data_file
from utils.monitoring import print_resources_consumption
from utils.input_args import parse_args
from utils.log_config import setup_logging

class SharedState:
    def __init__(self):
        self.registering = True
        self.orderbooks_df = pd.DataFrame()
        self.id_counter = 0
        self.csv_filepath = None
        self.data_queue = Queue()

# Parse command-line arguments
args = parse_args()

async def window(state, hours, minutes, seconds):
    total_seconds = hours * 3600 + minutes * 60 + seconds
    await asyncio.sleep(total_seconds)
    state.registering = False

def main():
    setup_logging(args.debug_mode)  # Initialize logging configuration
    logging.info("Starting trading bot")

    state = SharedState()

    try:
        # Initialize the exchange
        API_KEY = os.environ.get(f'{args.exchange.upper()}_API_KEY')
        API_SECRET = os.environ.get(f'{args.exchange.upper()}_API_SECRET')
        exchange = initialize_exchange(args.exchange, API_KEY, API_SECRET)
        logging.info(f"Initialized {args.exchange} exchange")

        if args.mode == "gather_data":
            state.csv_filepath = data_file(args)
            logging.info("Starting data gathering mode")
            # Start writer thread
            writer_thread_obj = Thread(target=writer_thread, args=(state.data_queue, state.csv_filepath))
            writer_thread_obj.daemon = True
            writer_thread_obj.start()

        loop = asyncio.get_event_loop()
        loop.create_task(window(state, hours=args.hours, minutes=args.minutes, seconds=args.seconds))
        loop.run_until_complete(fetch_orderbook(state, exchange, args))

        if args.mode == "gather_data" and not state.orderbooks_df.empty:
            logging.info("Writing remaining data to CSV")
            with open(state.csv_filepath, mode='a', newline='') as file:
                state.orderbooks_df.to_csv(file, index=False, header=False)

        resources = print_resources_consumption()
        logging.info(f"Resources consumption: {resources}")
        loop.run_until_complete(exchange.close())
        logging.info("Exchange connection closed")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()