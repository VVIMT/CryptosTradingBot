import os
import logging
import ccxt
import ccxt.pro as ccxtpro


def init_exchange(exchange_name, api_key, api_secret):
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

def get_api_keys(exchange_name):
    API_KEY = os.environ.get(f'{exchange_name.upper()}_API_KEY')
    API_SECRET = os.environ.get(f'{exchange_name.upper()}_API_SECRET')
    if not API_KEY or not API_SECRET:
        raise ValueError(f"API key and secret for {exchange_name} must be set as environment variables")
    return API_KEY, API_SECRET
