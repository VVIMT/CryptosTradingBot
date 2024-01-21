import asyncio
import logging

async def handle_websocket_reconnection(exchange, attempt=0):
    MAX_RECONNECTION_ATTEMPTS = 5
    RECONNECTION_BACKOFF = 2  # seconds

    while attempt < MAX_RECONNECTION_ATTEMPTS:
        try:
            logging.info("Attempting to reconnect to WebSocket...")
            await exchange.close()
            await asyncio.sleep(RECONNECTION_BACKOFF ** attempt)
            await exchange.load_markets(reload=True)
            return True  # Successful reconnection
        except Exception as e:
            logging.error(f"Reconnection attempt {attempt + 1} failed: {e}")
            attempt += 1

    logging.error("Maximum reconnection attempts reached.")
    return False  # Reconnection failed
