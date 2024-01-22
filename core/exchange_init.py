import ccxt
import ccxt.pro as ccxtpro
import logging

def initialize_exchange(exchange_name, api_key, api_secret):
    try:
        exchange_class = getattr(ccxtpro, exchange_name)
        if not exchange_class:
            raise ValueError(f"Exchange {exchange_name} not found in ccxt.pro")

        if not api_key or not api_secret:
            raise ValueError("API key and secret must be provided")

        exchange = exchange_class({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })

        return exchange

    except (ccxt.NetworkError, ccxt.ExchangeError) as e:
        logging.error(f"Error initializing {exchange_name} exchange: {e}")
    except Exception as e:
        logging.error(f"Unexpected error occurred while initializing {exchange_name} exchange: {e}")

    return None
