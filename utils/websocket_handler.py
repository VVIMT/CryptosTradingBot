import asyncio
import logging
import os

async def handle_websocket_reconnection(exchange, attempt=0):
    MAX_RECONNECTION_ATTEMPTS = 5
    RECONNECTION_BACKOFF = 2  # seconds

    while attempt < MAX_RECONNECTION_ATTEMPTS:
        try:
            wait_time = RECONNECTION_BACKOFF ** attempt
            logging.info(f"Attempting to reconnect to WebSocket (Exchange: {exchange.name}, Attempt: {attempt + 1}, Waiting: {wait_time} seconds)...")
            await exchange.close()
            await asyncio.sleep(wait_time)
            await exchange.load_markets(reload=True)
            return True  # Successful reconnection
        except Exception as e:
            logging.exception(f"Reconnection attempt {attempt + 1} failed for {exchange.name}: {e}")
            attempt += 1

    logging.error(f"Maximum reconnection attempts reached for {exchange.name}.")
    return False  # Reconnection failed
