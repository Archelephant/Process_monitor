#Requires running LibreHardwareMonitor (https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/) running in background
#Original commin by sergey@lourie.info

import wmi
from datetime import datetime
import os
import time

def LHWM_check():
    c = wmi.WMI(moniker='//./root')
    for __NAMESPACE in c.query("SELECT * FROM __NAMESPACE"):
        if 'LibreHardwareMonitor' in __NAMESPACE.Name:
            return False
        else:
            return True
        #This is weird, but it seems that this check is flipped... but it works!

def query_sensor_readings():
    # Initialize the WMI object in LibreHardwareMonitor namespace
    w = wmi.WMI(namespace="root\LibreHardwareMonitor")

    # Query for sensor data (e.g., current sensors)
    try:
        #Search for sensors in WMI with WQL
        #sensors = wmi_obj.query("SELECT * FROM Sensor")
        #Instead of WQL search we call for .Sensor() method
        sensors = w.Sensor()

        if not sensors:
            #print("No sensors found.")
            return None

        # Iterate through the sensors and return their values
        return {sensor.Name: sensor.Value for sensor in sensors}
            
        '''
        for sensor in sensors:
            print(f"Sensor Name: {sensor.Name}, Value: {sensor.Value}")
            #print(f"Current Reading: {sensor.CurrentReading} A")
            #CurrentReading is a method inherited from WMI, but without LibreHardwareMonitor it's always None
        '''

    except Exception as e:
        print(f"An error occurred while querying sensor data: {e}")
        return None

if __name__ == "__main__":
    c = wmi.WMI(moniker='//./root')
    if not LHWM_check():
        print('LibreHardwareMonitor not found in system, exiting.')
        exit()
    elif query_sensor_readings() == None:
        print('No sensor values supplied via WMI, check that LibreHardwareMonitor is running in the background.')
        exit()
    else:
        timenow_string = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        with open(timenow_string + '.csv', '+tw') as f:
            try:
                qdict = query_sensor_readings()
                qnames = [key + '; ' for key in qdict.keys()]
                qnames.append('timestamp')
                f.write(''.join(qnames) + '\n')
                while True:
                    qdict = query_sensor_readings()
                    qvals = [str(val) + '; ' for val in qdict.values()]
                    strtime = str(datetime.now())
                    qvals.append(strtime)
                    f.write(''.join(qvals) + '\n')
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Exiting...")
                f.close()