import asyncio
import psutil
#import bleak.exc
from bleak import BleakClient, BleakScanner
#from bleak.backends.device import BLEDevice
from datetime import datetime
#from typing import Callable, Any
from time import time
import os, sys
import pandas as pd
import re

home_dir = "D:\\Research\\Smart_Plug"
os.chdir(home_dir)
output_file = "plug_dump_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".csv"
#Data timeout gathering constant, in seconds
DATA_TIMEOUT = 1200

################BLE code#########################
#Scan for plug
async def scan_plug():
    start_time = time()
    try:
        devices = await BleakScanner.discover()
        for i, d in enumerate(devices):
            #print(f"{i}: {d.name}, {d.address}")
            plug_name = d.name
            if plug_name is not None:
                if 'SMART_PLUG' in plug_name:
                    plug_addr = d.address
                    print(f"Found {plug_name} at {plug_addr}")
                    end_time = time()
                    print(f'Scan complete in {end_time - start_time} s.')
                    return plug_name, plug_addr
    except TypeError:
        print(i)
    #end_time = time()
    #print(f'Scan complete in {end_time - start_time} s.' )

plug_name, plug_addr = asyncio.run(scan_plug())

#These are constants for my plug
service_UUID = '2064c3e2-a7b1-11ed-ada1-0242ac120002'
characteristic_UUID = '2064c34e-a7b1-11ed-ada1-0242ac120002'

#We need a notification handler for working with Notification-type GATTs
def notification_handler(sender: str, data: bytearray):
    """Notification handler which transforms the received bytearray and saves the data received."""
    try:
        V_RMS_mV = int(data[0]) + int(data[1]*256) + int(data[2]*256*256)
        I_RMS_mA = int(data[4]) + int(data[5]*256) + int(data[6]*256*256)
        P_RMS_mW = int(data[8]) + int(data[9]*256) + int(data[10]*256*256)
        #timestamp = int(data[12]) + int(data[13]*256) + int(data[14]*256*256)
        cpu = psutil.cpu_percent()
        mem = str(psutil.virtual_memory())
        try:
            free_mem = re.findall(r'used=\d+?, free=(\d+?)\)', mem)[0]
        except IndexError:
            free_mem = 0
        try:
            used_mem = re.findall(r'used=(\d+?), free=\d+?', mem)[0]
        except IndexError:
            used_mem = 0
        swap = str(psutil.swap_memory())
        try:
            free_swm = re.findall(r'used=\d+?, free=(\d+?)\,', swap)[0]
        except IndexError:
            free_swm = 0
        try:
            used_swm = re.findall(r'used=(\d+?), free=\d+?', swap)[0]
        except IndexError:
            used_swm = 0
        HDD_read = psutil.disk_io_counters().read_bytes
        HDD_write = psutil.disk_io_counters().write_bytes
        Net_out = psutil.net_io_counters().bytes_sent
        Net_in = psutil.net_io_counters().bytes_recv
        #print(f"V_RMS= {V_RMS_mV} mV, I_RMS= {I_RMS_mA}, mA, P= {P_RMS_mW}, mW, Time: {timestamp}")
        with open(output_file, 'a+') as f:
            if os.stat(output_file).st_size == 0:
                print(f"Created new file {output_file}.")
                f.write("V_RMS, mV; I_RMS, mI; P_RMS, mW; CPU Load; VM Free Size; VM Used Size; Swap Mem Free Size; Swap Mem Used Size; HDD Read; HDD Write; NW Out; NW In; Time" + "\n\r")
            else:
                f.write(f"{V_RMS_mV}; {I_RMS_mA}; {P_RMS_mW}; {cpu}; {free_mem}; {used_mem}; {free_swm}; {used_swm}; {HDD_read}; {HDD_write}; {Net_out}; {Net_in}; {time()}" + "\n\r")

    except IndexError:
        print('Not enough bytes received.')

#Main async method, to be called from loop
async def main(plug_name, plug_addr):
    async with BleakClient(plug_addr, services=[service_UUID], timeout=10.0) as client:
        try:
            if (not client.is_connected):
                raise "No connection!"
            services = await client.get_services()
            for service in services:
                print(f"Service handle: {service.handle}, UUID: {service.uuid}, description: {service.description}")
                characteristics = service.characteristics
                for char in characteristics:
                    print(
                        f"Characteristics: {char.handle}, UUID: {char.uuid}, Description: {char.description}, Properties: {char.properties}.")
                    descriptors = char.descriptors
                    for desc in descriptors:
                        print("Descriptor: ", desc, ".")
            #TO DO: fix pairing with bleak
            #print("Trying to pair...")
            #try:
            #    await client.pair()
            #except NotImplementedError:
                # This is expected on Mac
            #    pass
            #except bleak.exc.BleakError:
            #    print("Pairing failed. Using time from receiving system.")
            print(f'Start checking for notifications on {characteristic_UUID} at {plug_name}:')
            await client.start_notify(characteristic_UUID, notification_handler)
            await asyncio.sleep(DATA_TIMEOUT)
            #Here we receive only one notification before exiting the try loop
        finally:
            print('Stop reading notifications.')
            await client.stop_notify(characteristic_UUID)

#main function to check functionality without async coroutines and loops
def work():
    try:
        asyncio.run(main(plug_name, plug_addr))
    except asyncio.exceptions.TimeoutError:
        print("Timed out. Try again.")

#Manual start of routines
output_file = "plug_dump_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".csv"
work()

async def start_notifications():
    async with BleakClient(plug_addr, services=[service_UUID], timeout=10.0) as client:
        try:
            if (not client.is_connected):
                raise "No connection!"
            await client.start_notify(characteristic_UUID, notification_handler)
        finally:
            print(f'Reading notifications on {characteristic_UUID}.')

async def stop_notifications():
    async with BleakClient(plug_addr, services=[service_UUID], timeout=10.0) as client:
        try:
            if (not client.is_connected):
                raise "No connection!"
            await client.stop_notify(characteristic_UUID)
        finally:
            print('Notifications successfully stopped.')

async def read_notifications():
    await asyncio.sleep(0.1)

def notif():
    asyncio.run(start_notifications())
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith("There is no current event loop in thread"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    try:
        asyncio.ensure_future(read_notifications())
        loop.run_forever()
    except KeyboardInterrupt:
        asyncio.run(stop_notifications())
        pass
    finally:
        print("Exiting loop.")

#Uncomment when working from console or in debug mode
work()

#TODO: add loops

##############PSUtiles code###################
def get_size(bytes):
    """
    Returns size of bytes in a nice format
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

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

