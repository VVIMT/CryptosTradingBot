from threading import Thread
from datetime import datetime
import os

def data_file(args):
    if not os.path.exists('data'):
        os.makedirs('data')
    # Format the filename with the current timestamp, trading pair, duration, and datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    formatted_pair = args.symbol.replace('/', '')
    total_duration = f"{args.hours}h{args.minutes}m{args.seconds}s"
    filename = f"orderbook_{formatted_pair}_{total_duration}_{timestamp}.csv"
    return os.path.join('data', filename)

def writer_thread(data_queue, csv_filepath):
    header_written = False
    while True:
        data_batch = data_queue.get()
        with open(csv_filepath, mode='a', newline='') as file:
            data_batch.to_csv(file, index=False, header=not header_written)
        header_written = True
        data_queue.task_done()
