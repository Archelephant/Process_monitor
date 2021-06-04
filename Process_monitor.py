import psutil
from datetime import datetime
import pandas as pd
import time
import os

def get_size(bytes):
    """
    Returns size of bytes in a nice format
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

#now let's make something simple and practical for the purposes of our energy research

def get_info_simple():
    processes = []
    for process in psutil.process_iter():
        pid = process.pid
        if pid == 0:
            # System Idle Process for Windows NT, useless to see anyways
            # We'll need all the processes for our research
            continue
        if process.status() == "stopped":
            #skipping the stopped processes
            continue
        name = process.name()
        path = process.exe()
        threads = process.num_threads()
        cpu = process.cpu_percent()
        mem = process.memory_percent()
        HDD_read = process.io_counters().read_bytes
        HDD_write = process.io_counters().write_bytes
        try:
            create_time = datetime.fromtimestamp(process.create_time())
        except OSError:
            # system processes, using boot time instead
            create_time = datetime.fromtimestamp(psutil.boot_time())
        processes.append({'Name': name, "Path": path, "Threads": threads,
                        "CPU Usage": cpu, "Memory Usage": mem, "HDD Read": HDD_read,
                        "HDD Write": HDD_write, "pid": pid, "Start time": create_time})
    return processes

def construct_dataframe_simple(processes):
    df = pd.DataFrame(processes)
    df.set_index('pid', inplace=True)
    df['Start time'] = df['Start time'].apply(datetime.strftime, args=("%Y-%m-%d %H:%M:%S",))
    return df

def get_system_info():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    HDD_read = psutil.disk_io_counters().read_bytes
    HDD_write = psutil.disk_io_counters().write_bytes
    Net_out = psutil.net_io_counters().bytes_sent
    Net_in = psutil.net_io_counters().bytes_recv
    return {'CPU Usage': cpu, 'VM Total': mem.total, 'VM Available': mem.available,
            'VM Free': mem.free, 'VM Used': mem.used, 'SM Total': swap.total,
            'SM Used': swap.used, 'SM Free': swap.free, 'HDD Read': HDD_read,
            'HDD Write': HDD_write, 'NW In': Net_in, 'NW Out': Net_out,
            'Time': timestamp}

#Note that I am not converting bytes into anything else ^^

if __name__ == "__main__":
    print("Checking the availability of \\data subdirectory")
    if os.path.isdir("data"):
        print("Subdirectory already exists.")
    else:
        print("Subdirectory not found, creating new one.")
        os.mkdir("data")
    print("Monitoring system and process info every 10 s:")
    try:
        while True:
            timenow_string = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            print("Adding data for ", timenow_string)
            snapshot = construct_dataframe_simple(get_info_simple())
            snapshot.to_csv("data\\"+"processes_" + timenow_string + ".csv", sep=";", decimal=",")
            sf = pd.DataFrame(get_system_info(), index=[0])
            sf.to_csv("data\\"+"system_" + timenow_string + ".csv", sep=";", decimal=",")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Exiting...")