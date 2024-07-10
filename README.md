# CryptosTradingBot

## Overview

This project consists of a trading bot that fetches real-time order book data for a specified symbol from a chosen exchange using the `ccxtpro` library and a websocket connection. It runs for a user-defined duration and can either save the data to a CSV file in batches or feed the latest order book as a DataFrame.

## Directory Structure

```
CryptoTradingBot/
CryptosTradingBot/
├── core/
│   ├── data_writer.py
│   ├── exchange_init.py
│   ├── exchange.py
│   ├── orchestrator.py
│   ├── orders.py
├── data/
├── Docker/
├── Logs/
├── utils/
│   ├── input_args.py
│   ├── log_config.py
│   ├── monitoring.py
│   ├── websocket_handler.py
├── main.py
├── README.md
└── requirements.txt

```

## Key Features

1. **Real-time Data Fetching**: Utilizes the `ccxtpro` library and a websocket connection to fetch real-time order book data.
2. **Argument Parsing**: Leverages `argparse` to take in various command-line arguments.
3. **Input Validation**: Ensures non-negative time values, positive depth, and validates the provided symbol against available options on the chosen exchange.
4. **Data Storage and Processing**: Processes the fetched data into a pandas DataFrame and either returns the latest order book or saves it to a CSV file in batches.
5. **Parallel Processing**: Uses a separate thread to handle disk writes, ensuring that they don't block the real-time data processing.
6. **Output**: Showcases the DataFrame's memory consumption and, if requested, prints a subset of the gathered data.

### Command-Line Arguments

- `--mode`: Operation mode, choose between "feed_model" (returns latest order book DataFrame) and "gather_data" (saves data to CSV file). Default is "feed_model".
- `--batch_size`: Specify the batch size for saving to CSV. Default is `1000`.
- `--hours`: Duration in hours for the bot's operation. Default is `0`.
- `--minutes`: Duration in minutes. Default is `0`.
- `--seconds`: Duration in seconds. Default is `5`.
- `--exchange`: Specify the exchange to fetch data from. Use `python main.py --help` to view available choices.
- `--symbol`: Specify the symbol for data collection. Default is `BTC/USDT`.
- `--depth`: Specify the depth of the order book to fetch. Default is `50`.
- `--print`: Designate the number of lines from the DataFrame to display. Default is `0`.

### Example Usages

1. **Retrieve Real-time Data for 1 Hour for BTC/USDT and Save to CSV**:
   ```bash
   python main.py --mode gather_data --hours 1 --symbol BTC/USDT
   ```

2. **Retrieve Real-time Data for 30 Minutes for ETH/USDT and Print the Last 5 Rows**:
   ```bash
   python main.py --minutes 30 --symbol ETH/USDT --print 5
   ```

3. **Show Help Information**:
   ```bash
   python main.py --help
   ```

### Requirements

- Python 3.12 (Recommended)
- Libraries: `asyncio`, `pandas`, `ccxt`, `ccxtpro`

### Installation Guide

1. **Clone the Repository and Navigate to the Project Directory**:
   ```bash
   git clone https://github.com/VVIMT/CryptoTradingBot.git && cd CryptoTradingBot
   ```

2. **Install the Required Libraries**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set the Exchange API Keys and Secrets as Environment Variables (Choose 'bybit' or 'binance')**:
   ```bash
   export EXCHANGE_NAME_API_KEY=your_api_key
   export EXCHANGE_NAME_API_SECRET=your_api_secret
   ```

4. **Run the Script (Choose 'bybit' or 'binance')**:
   ```bash
   python main.py --mode gather_data --exchange bybit --symbol BTC/USDT > output.log 2>&1 &
   ```

### Additional Information

- Depending on the chosen exchange, the relevant API keys and secrets should be set as environment variables for authentication.
- It's essential to have the necessary libraries installed.
- The script incorporates error-handling mechanisms to address potential network and exchange-related disruptions.

To use this script, you'd need an account on the chosen exchange and then set the relevant API keys and secrets as environment variables. Always maintain the confidentiality of your API keys and avoid embedding them directly into scripts.
