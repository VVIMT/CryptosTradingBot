import ccxt
import ccxt.pro as ccxtpro
import pandas as pd
import logging

def initialize_exchange(exchange_name, api_key, api_secret):
    exchange = getattr(ccxtpro, exchange_name)({
        'apiKey': api_key,
        'secret': api_secret,
    })
    return exchange

async def fetch_orderbook(state, exchange, args):
    params = {'category': args.category}
    while state.registering:
        try:
            raw_orderbook = await exchange.watchOrderBook(args.symbol, args.depth, params)
            order_book_df = pd.DataFrame(raw_orderbook)

            # Splitting the tuples in the 'asks' and 'bids' columns
            order_book_df[['ask_price', 'ask_volume']] = order_book_df['asks'].apply(pd.Series)
            order_book_df[['bid_price', 'bid_volume']] = order_book_df['bids'].apply(pd.Series)

            # Dropping the original 'asks' and 'bids' columns
            order_book_df = order_book_df.drop(columns=['asks', 'bids'])

            # Insert the "id" column at the first position and 'trade_priority' next to 'symbol'
            order_book_df.insert(0, 'id', state.id_counter)
            order_book_df.insert(order_book_df.columns.get_loc('symbol') + 1, 'trade_priority', order_book_df.groupby('id').cumcount() + 1)

            state.id_counter += 1

            state.orderbooks_df = pd.concat([state.orderbooks_df, order_book_df], ignore_index=True)
            if args.mode == "gather_data" and len(state.orderbooks_df) >= args.batch_size:
                state.data_queue.put(state.orderbooks_df)  # Put data into the queue
                state.orderbooks_df = pd.DataFrame()

        except ccxt.RequestTimeout as e:
            logging.error(f"Request timeout error: {e}")
        except ccxt.ExchangeError as e:
            logging.error(f"Exchange error: {e}")
        except ccxt.AuthenticationError as e:
            logging.error(f"Authentication error: {e}")
        except ccxt.DDoSProtection as e:
            logging.error(f"DDoS Protection error: {e}")
        except ccxt.RateLimitExceeded as e:
            logging.error(f"Rate limit exceeded error: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    return state
