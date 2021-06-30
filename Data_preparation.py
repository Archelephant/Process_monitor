import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import seaborn as sns
#I'm working with PyCharm with default interactive mode, enable the line below for Anaconda
#%matplotlib inline
import os

#This is optional
sns.set_style(style='darkgrid')

path='Your path to the subdirectory with data files'
filelist = os.listdir(path)
os.chdir(path)
#but before we dive into the cycle, initialize empty dataframes
amps_df = pd.DataFrame()
volts_df = pd.DataFrame()
system_df = pd.DataFrame()
processes_df = pd.DataFrame()
for file in filelist:
    # checking for the file "amps.txt" in the directory
    if 'amps' in file:
        # building the dataframe with current readings vs. datetime stamps
        amps_df = amps_df.append(pd.read_csv(file, header=None, sep=" +", skiprows=3, decimal="."))
    # checking for the file volts.txt in the directory
    if 'volts' in file:
        try:
            volts_df = volts_df.append(pd.read_csv(file, sep="\t--\t", decimal=".", comment="V", encoding='utf16', engine='python'))
        except ImportError:
            continue
    #browsing through the directory for all files containing system status info
    if 'system' in file:
        system_df=system_df.append(pd.read_csv(file, sep=';', decimal=','))

    #finally, the hardest one - gathering information on processes into one dataframe
    #I couldn't find anything better than to use multi-indexing approach
    #But before we get to multi-indexing, I'm building the dataframe with repeating datetime indices
    if 'processes' in file:
        try:
            timestring = re.findall(r'processes_(\d\d\d\d-\d\d-\d\d-\d\d-\d\d-\d\d).csv', file, re.IGNORECASE)[0]
            #For the purpose of saving data, might be useful to keep the datetime string format
            #datescol = [timestring for i in range(len(temp))]
            # For analysis purposes I will be using timestamps instead of datetime strings
            timestamp = datetime.strptime(timestring, '%Y-%m-%d-%H-%M-%S')
            temp = pd.read_csv(file, sep=';', decimal=',')
            datescol = [timestamp for i in range(len(temp))]
            temp['Datetime'] = datescol
            processes_df = processes_df.append(temp)
        except IndexError:
            timestring = '0000-00-00-00-00-00'
            timestamp = datetime.strptime(timestring, '%Y-%m-%d-%H-%M-%S')
            temp = pd.read_csv(file, sep=';', decimal=',')
            datescol = [timestamp for i in range(len(temp))]
            temp['Datetime'] = datescol
            processes_df = processes_df.append(temp)
#Time to clean up current readings
amps_df['Datetime'] = pd.to_datetime(amps_df[4], format='%d.%m.%Y\\%H:%M:%S')
amps_df.drop([0, 1, 3, 4], inplace=True, axis=1)
amps_df.columns=['Current', "Datetime"]
#And time to clean up voltage readings, too
volts_df['Datetime'] = pd.to_datetime(volts_df.index.values, format='%d/%m/%Y  %H:%M:%S')
volts_df.columns=['Voltage', 'Datetime']
#repeat until no more outliers are left
while volts_df['Voltage'].max() > 250.0:
    volts_df = volts_df.drop(volts_df.loc[volts_df['Voltage'] == volts_df['Voltage'].max()].index.values.astype(str)[0])
#also, need to get the system information reading back into timestamp format instead of datetime string read from file
system_df['Datetime'] = pd.to_datetime(system_df['Time'], format='%Y-%m-%d %H:%M:%S')
#system_df['Timestamp'] = datetime.strptime(system_df['Time'], '%Y-%m-%d %H:%M:%S')

#checking the consistency of current readings[Optional]
amps_df.plot(x='Datetime', y='Current')
print('Time lapse for current records: ', amps_df['Datetime'].max()-amps_df['Datetime'][0])
#checking the consistency of voltage readings [Optional\
volts_df.plot(x='Datetime', y='Voltage')
print('Time lapse for voltage records: ', volts_df['Datetime'].max()-volts_df['Datetime'][0])

#truncating the dataframes to contain only records that have corresponding current readings
#I am going to try pandas merge in a inner join manner
readings = pd.merge(left =  volts_df, right= amps_df, how='inner', on='Datetime')
system = pd.merge(left=readings, right = system_df, how='inner', on='Datetime')
system.drop(['Time', 'Unnamed: 0'], axis=1, inplace=True)

#You should get smth like this:
#system.columns = ['Voltage', 'Datetime', 'Current', 'CPU Usage', 'VM Total', 'VM Available',
#       'VM Free', 'VM Used', 'SM Total', 'SM Used', 'SM Free', 'HDD Read',
#       'HDD Write', 'NW In', 'NW Out']

#TODO: write a function that merges system information dataframe with processes information datafram
