import ccxt
import requests
import socket
import pandas as pd
import logging
import time
from utils.websocket_handler import handle_websocket_reconnection
from urllib3.exceptions import HTTPError

async def fetch_orderbook(state, exchange, args):
    params = {'category': args.category}
    retry_delay = 5  # initial retry delay in seconds
    max_retries = 5  # maximum number of retries
    current_retry = 0

    while state.registering:
        try:
            raw_orderbook = await exchange.watchOrderBook(args.symbol, args.depth, params)
            order_book_df = pd.DataFrame(raw_orderbook)

            # Processing the order book data
            order_book_df[['ask_price', 'ask_volume']] = order_book_df['asks'].apply(pd.Series)
            order_book_df[['bid_price', 'bid_volume']] = order_book_df['bids'].apply(pd.Series)
            order_book_df.drop(columns=['asks', 'bids'], inplace=True)

            order_book_df.insert(0, 'id', state.id_counter)
            order_book_df.insert(order_book_df.columns.get_loc('symbol') + 1, 'trade_priority', order_book_df.groupby('id').cumcount() + 1)

            state.id_counter += 1
            state.orderbooks_df = pd.concat([state.orderbooks_df, order_book_df], ignore_index=True)

            if args.mode == "gather_data" and len(state.orderbooks_df) >= args.batch_size:
                state.data_queue.put(state.orderbooks_df)
                state.orderbooks_df = pd.DataFrame()
            # Reset the retry counter after a successful request
            current_retry = 0

        except ccxt.NetworkError as e:
            logging.error(f"ccxt Network error (possible disconnection): {e}")
            if not await handle_websocket_reconnection(exchange, attempt=current_retry):
                break
            current_retry += 1
            if current_retry >= max_retries:
                logging.error("Max retries exceeded for WebSocket reconnection. Exiting.")
                break

        except (requests.ConnectionError, socket.gaierror, HTTPError) as e:
            logging.error(f"Network connectivity error: {e}")
            if current_retry < max_retries:
                time.sleep(retry_delay)
                current_retry += 1
                retry_delay *= 2  # Exponential backoff
            else:
                logging.error("Max retries exceeded. Exiting.")
                break

        except (ccxt.RequestTimeout, ccxt.ExchangeError, ccxt.AuthenticationError, 
                ccxt.DDoSProtection, ccxt.RateLimitExceeded) as e:
            logging.error(f"Exchange-specific error: {e}")
            # Optional: Implement specific logic for each error type if needed

        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            break  # or implement a different strategy for unexpected errors

    return state
