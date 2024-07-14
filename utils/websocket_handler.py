import asyncio
import logging
import random
import os

async def handle_websocket_reconnection(exchange, attempt=0):
    max_reconnection_attempts = 5
    min_reconnection_backoff = 1  # seconds
    max_reconnection_backoff = 30  # seconds

    def get_wait_time(attempt):
        wait_time = random.uniform(min_reconnection_backoff,
                                   min_reconnection_backoff * 2 ** attempt)
        return min(wait_time, max_reconnection_backoff)

    async def close_and_sleep(wait_time):
        await exchange.close()
        await asyncio.sleep(wait_time)

    while attempt < max_reconnection_attempts:
        try:
            wait_time = get_wait_time(attempt)
            logging.info(f"Attempting to reconnect to WebSocket "
                         f"(Exchange: {exchange.name}, Attempt: {attempt + 1}, "
                         f"Waiting: {wait_time:.2f} seconds)...")

            if exchange.is_connected():
                logging.info("WebSocket is still connected. No reconnection needed.")
                return True

            await close_and_sleep(wait_time)
            await exchange.load_markets(reload=True)

            logging.info(f"Successfully reconnected to {exchange.name}.")
            return True  # Successful reconnection

        except asyncio.CancelledError:
            logging.warning(f"WebSocket reconnection attempt {attempt + 1} "
                            f"cancelled for {exchange.name}.")
            raise

        except Exception as specific_error:
            logging.exception(f"Reconnection attempt {attempt + 1} failed for "
                              f"{exchange.name}: {specific_error}")
            attempt += 1

    logging.error(f"Maximum reconnection attempts reached for {exchange.name}. "
                  f"Initiating shutdown...")
    await exchange.close()
    return False