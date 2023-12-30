import resource
import psutil

def get_cpu_usage_percentage():
    return psutil.cpu_percent(interval=0.1)

def get_memory_usage_percentage():
    process = psutil.Process()
    return process.memory_percent()

def print_resources_consumption():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    print("User CPU time used (seconds):", usage.ru_utime)
    print("System CPU time used (seconds):", usage.ru_stime)
    print("Maximum resident set size (kilobytes):", usage.ru_maxrss)
    print("Soft page faults:", usage.ru_minflt)
    print("Hard page faults:", usage.ru_majflt)
    print("Voluntary context switches:", usage.ru_nvcsw)
    print("Involuntary context switches:", usage.ru_nivcsw)
    print("CPU usage percentage:", get_cpu_usage_percentage(), "%")
    print("Memory usage percentage:", get_memory_usage_percentage(), "%")
