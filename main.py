import asyncio
import os
from queue import Queue
from threading import Thread
import pandas as pd
import logging
import random
from core.exchange_init import init_exchange, get_api_keys
from core.exchange import fetch_orderbook
from core.orders import *
from core.data_writer import writer_thread, data_file
from utils.websocket_handler import handle_websocket_reconnection
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

def init_logging_and_state(debug_mode):
    setup_logging(debug_mode)
    logging.info("Starting trading bot")
    return SharedState()

def start_writer_thread(state, args):
    state.csv_filepath = data_file(args)
    logging.info("Starting data gathering mode")
    writer_thread_obj = Thread(target=writer_thread, args=(state.data_queue, state.csv_filepath))
    writer_thread_obj.daemon = True
    writer_thread_obj.start()

async def run_fetch_orderbook(state, exchange, args):
    loop = asyncio.get_event_loop()
    loop.create_task(window(state, hours=args.hours, minutes=args.minutes, seconds=args.seconds))
    while state.registering:
        try:
            await fetch_orderbook(state, exchange, args)
        except ccxt.NetworkError as e:
            logging.error(f"Network error occurred: {e}. Attempting to reconnect...")
            success = await handle_websocket_reconnection(exchange)
            if not success:
                break
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            break

def write_remaining_data(state):
    if state.csv_filepath and not state.orderbooks_df.empty:
        logging.info("Writing remaining data to CSV")
        with open(state.csv_filepath, mode='a', newline='') as file:
            state.orderbooks_df.to_csv(file, index=False, header=False)

async def main_async():
    state = init_logging_and_state(args.debug_mode)

    try:
        api_key, api_secret = get_api_keys(args.exchange)
        exchange = init_exchange(args.exchange, api_key, api_secret)

        trading_fees = await fetch_trading_fees(exchange)
        logging.info(f"Trading fees: {trading_fees}")

        balance = await fetch_balance(exchange)
        logging.info(f"Account balance: {balance}")

        if args.mode == "gather_data":
            start_writer_thread(state, args)

        await run_fetch_orderbook(state, exchange, args)
        write_remaining_data(state)

        resources = print_resources_consumption()
        logging.info(f"Resources consumption: {resources}")

        await exchange.close()
        logging.info("Exchange connection closed")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_async())

if __name__ == "__main__":
    main()
