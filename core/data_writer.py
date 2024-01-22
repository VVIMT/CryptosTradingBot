from threading import Thread
from datetime import datetime
import os
import logging

def data_file(args):
    if not os.path.exists('data'):
        os.makedirs('data')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    formatted_pair = args.symbol.replace('/', '')
    total_duration = f"{args.hours}h{args.minutes}m{args.seconds}s"
    filename = f"orderbook_{formatted_pair}_{total_duration}_{timestamp}.csv"
    return os.path.join('data', filename)

def writer_thread(data_queue, csv_filepath):
    header_written = False
    while True:
        try:
            data_batch = data_queue.get()
            with open(csv_filepath, mode='a', newline='') as file:
                data_batch.to_csv(file, index=False, header=not header_written)
            header_written = True
            data_queue.task_done()
        except Exception as e:
            logging.error(f"Error in writer_thread: {e}")
