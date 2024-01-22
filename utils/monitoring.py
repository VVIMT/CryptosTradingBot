import logging
import time
import resource
import psutil

# Import the custom log level
from utils.log_config import RESOURCE_CONSUMPTION_LEVEL

# Initialize the logger for resource consumption
resource_logger = logging.getLogger('resource_consumption')

def log_resource_consumption(msg, *args, **kwargs):
    resource_logger.log(RESOURCE_CONSUMPTION_LEVEL, msg, *args, **kwargs)

def get_cpu_usage_percentage():
    return psutil.cpu_percent(interval=0.1)

def get_memory_usage_percentage():
    process = psutil.Process()
    return process.memory_percent()

def get_network_io():
    net_io = psutil.net_io_counters()
    return net_io.bytes_sent, net_io.bytes_recv

def calculate_throughput():
    old_sent, old_recv = get_network_io()
    time.sleep(1)  # Wait for a second
    new_sent, new_recv = get_network_io()

    # Calculate throughput
    sent_throughput = (new_sent - old_sent) * 8 / 1024 / 1024  # Convert bytes to Mbps
    recv_throughput = (new_recv - old_recv) * 8 / 1024 / 1024  # Convert bytes to Mbps

    return sent_throughput, recv_throughput

def print_resources_consumption():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    log_resource_consumption(f"User CPU time used (seconds): {usage.ru_utime}")
    log_resource_consumption(f"System CPU time used (seconds): {usage.ru_stime}")
    log_resource_consumption(f"Maximum resident set size (kilobytes): {usage.ru_maxrss}")
    log_resource_consumption(f"Soft page faults: {usage.ru_minflt}")
    log_resource_consumption(f"Hard page faults: {usage.ru_majflt}")
    log_resource_consumption(f"Voluntary context switches: {usage.ru_nvcsw}")
    log_resource_consumption(f"Involuntary context switches: {usage.ru_nivcsw}")
    log_resource_consumption(f"CPU usage percentage: {get_cpu_usage_percentage()} %")
    log_resource_consumption(f"Memory usage percentage: {get_memory_usage_percentage()} %")

    sent_throughput, recv_throughput = calculate_throughput()
    log_resource_consumption(f"Upload throughput (Mbps): {sent_throughput}")
    log_resource_consumption(f"Download throughput (Mbps): {recv_throughput}")
