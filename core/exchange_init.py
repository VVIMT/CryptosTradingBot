import ccxt.pro as ccxtpro

def initialize_exchange(exchange_name, api_key, api_secret):
    exchange_class = getattr(ccxtpro, exchange_name)
    exchange = exchange_class({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
    })
    return exchange
