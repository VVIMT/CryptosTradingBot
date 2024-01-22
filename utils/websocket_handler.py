import asyncio
import logging
import random
import os

async def handle_websocket_reconnection(exchange, attempt=0):
    MAX_RECONNECTION_ATTEMPTS = 5
    MIN_RECONNECTION_BACKOFF = 1  # seconds
    MAX_RECONNECTION_BACKOFF = 30  # seconds

    while attempt < MAX_RECONNECTION_ATTEMPTS:
        try:
            # Exponential backoff with a random jitter
            wait_time = random.uniform(MIN_RECONNECTION_BACKOFF, MIN_RECONNECTION_BACKOFF * 2 ** attempt)
            wait_time = min(wait_time, MAX_RECONNECTION_BACKOFF)
            logging.info(f"Attempting to reconnect to WebSocket (Exchange: {exchange.name}, Attempt: {attempt + 1}, Waiting: {wait_time:.2f} seconds)...")

            if exchange.is_connected():
                logging.info("WebSocket is still connected. No reconnection needed.")
                return True

            await exchange.close()
            await asyncio.sleep(wait_time)
            await exchange.load_markets(reload=True)
            # Add additional steps here to ensure the state of your bot is consistent with the market

            logging.info(f"Successfully reconnected to {exchange.name}.")
            return True  # Successful reconnection
        except Exception as specific_error:  # Consider catching specific exceptions
            logging.exception(f"Reconnection attempt {attempt + 1} failed for {exchange.name}: {specific_error}")
            attempt += 1

    logging.error(f"Maximum reconnection attempts reached for {exchange.name}. Initiating shutdown...")
    # Clean up resources and shutdown procedures
    await exchange.close()
    # Consider adding a notification or alert system here
    return False