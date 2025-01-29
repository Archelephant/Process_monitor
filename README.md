# Process_monitor

--------Initial Commit---------------
This Python script was created and tested with Python 3.6

External dependencies: 
- psutil - https://github.com/giampaolo/psutil
- pandas - https://pandas.pydata.org/

For precautionary measures, compile the script using py2exe into executable and use the flash drive on test systems - it will store in pandas-readable .csv files into the "\data" subfolder.

Py2Exe homepage - https://github.com/py2exe/py2exe/
External dependencies: 
- MS VC Redistributable - https://support.microsoft.com/en-us/topic/the-latest-supported-visual-c-downloads-2647da03-1eea-4433-9aff-95f26a218cc0

And don't forget to change the "decimal = ","" parameter!


----January, 29, 2025 update------------
Added Power_monitor.py to monitor voltage and power sensor reading and saving them into .csv.

Created and tested with Python 3.11.2

External dependencies:
- wmi https://pypi.org/project/WMI/1.0/ (1.0)
- LibreHardwareMonitor https://github.com/LibreHardwareMonitor/LibreHardwareMonitor
- (optional, for making standalone .exe only) pyinstaller https://pypi.org/project/pyinstaller/ (6.11.1)
