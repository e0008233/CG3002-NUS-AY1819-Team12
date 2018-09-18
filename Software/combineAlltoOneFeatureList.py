import pandas as pd
import numpy as np
from sklearn import preprocessing
from scipy.fftpack import fft
from pathlib import Path
import os

WINDOW_SIZE = 128

path = str(Path().resolve().parent) + '\Data'
print(path)

# Different volunteers
subjectList = ['Subject1', 'Subject2', 'Subject3', 'Subject4']
# subjectList = ['Subject1']
# Different activity classification
activityList = ['climbingdown','walking','jumping']
# activityList = ['jumping']
# sensor position needed
sensorPositionList = ['waist', 'chest','thigh']
# sensorPositionList = ['waist']
frame = pd.DataFrame()
list = []
for subject in subjectList:
    for activity in activityList:
        # ----------------------- Compiling all sensor data into one file -------------------------
        pathToOpen = path + '\\' + subject + '\\' + activity
        header = ['id']
        count = 0
        combinedData_sensor = []
        for fileName in os.listdir(pathToOpen):
            if fileName.endswith(".csv") and fileName.find("feature") != -1:

                df = pd.read_csv(open(pathToOpen + '\\' + fileName))
                list.append(df)
frame = pd.concat(list)

frame.to_csv(path + '\\' + 'combinedFeatureDataCSV.csv', index=None)



