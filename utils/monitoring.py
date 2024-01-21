import time
import resource
import psutil

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
    with open("resources_consumption.log", "w") as log_file:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        log_file.write(f"User CPU time used (seconds): {usage.ru_utime}\n")
        log_file.write(f"System CPU time used (seconds): {usage.ru_stime}\n")
        log_file.write(f"Maximum resident set size (kilobytes): {usage.ru_maxrss}\n")
        log_file.write(f"Soft page faults: {usage.ru_minflt}\n")
        log_file.write(f"Hard page faults: {usage.ru_majflt}\n")
        log_file.write(f"Voluntary context switches: {usage.ru_nvcsw}\n")
        log_file.write(f"Involuntary context switches: {usage.ru_nivcsw}\n")
        log_file.write(f"CPU usage percentage: {get_cpu_usage_percentage()} %\n")
        log_file.write(f"Memory usage percentage: {get_memory_usage_percentage()} %\n")

        sent_throughput, recv_throughput = calculate_throughput()
        log_file.write(f"Upload throughput (Mbps): {sent_throughput}\n")
        log_file.write(f"Download throughput (Mbps): {recv_throughput}\n")