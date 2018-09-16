import pandas as pd
import numpy as np
from sklearn import preprocessing
from scipy.fftpack import fft
from pathlib import Path
import os

path = str(Path().resolve().parent)
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

for subject in subjectList:
    for activity in activityList:
        # ----------------------- Compiling all sensor data into one file -------------------------
        pathToOpen = path + '\Data' + '\\' + subject + '\\' + activity
        header = ['id']
        count = 0
        combinedData_sensor = []
        for fileName in os.listdir(pathToOpen):
            for sensorPosition in sensorPositionList:
                if fileName.endswith(".csv") and fileName.find(sensorPosition) != -1:
                    if fileName.find('acc') != -1:
                        sensor = 'acc'
                    else:
                        sensor = 'gyr'
                    count = count + 1
                    df = pd.read_csv(open(pathToOpen + '\\' + fileName))

                    # drop all na values
                    df.dropna(how='any', inplace=True)
                    data = df.values

                    # add id column
                    if (count == 1):
                        toAdd = df.iloc[:, :1]
                        combinedData_sensor.append(toAdd)

                    # extract columns with value
                    toAdd = df.iloc[:, 2:]
                    # change the column names so they won't collide during concatenation
                    toAdd.columns = [str(cname) for cname in
                                     toAdd.columns + '_' + sensorPosition + '_' + sensor]
                    combinedData_sensor.append(toAdd)
        # concatenate them horizontally into a CSV file
        combinedDataCSV = pd.concat(combinedData_sensor, axis=1)
        combinedDataCSV.dropna(how='any', inplace=True)
        combinedDataCSV.to_csv(pathToOpen + '\\' + 'combinedDataCSV.csv', index=None)
        df = pd.DataFrame(combinedDataCSV)

        # ---------------------------------- Data segmentation ----------------------------------
        # Actual readings start at 2nd column
        data = df.values
        X = data[:, 1:]

        # get attribute names
        attriNameList = df.columns[1:]

        # create headers for features
        headers = []
        featureNameList = ['mean', 'median', 'std', 'iqr', 'max', 'min']
        for attriName in attriNameList:
            for featureName in featureNameList:
                headers.append(attriName + '_' + featureName)

        stat_list = []
        # windows of 2.56 sec and 50% overlap (128 readings/window), details in report section 5
        window_size = 128
        overlap = window_size // 2
        segment = []
        labels = []
        count = 0
        for i in range(int(len(X) / overlap)):
            segment.append(X[i * overlap : ((i * overlap) + window_size), 0:])

        # ---------------------------------- Feature extraction ----------------------------------
        for i in range(len(segment)):
            temp_row = []
            for j in range(0, np.size(segment[i], 1)):
                temp = segment[i][0:, j]
                # TODO: add more features
                # Mean = sum of everything / no. of data point
                mean = np.mean(temp)
                # Median = middle value of sorted
                median = np.median(temp)
                # Std = Standard Deviation, How individual points differs from the mean
                std = np.std(temp)
                # iqr = Inter-Quartile Range, 75th percentile - 25th percentile
                q75, q25 = np.percentile(temp, [75, 25])
                iqr = q75 - q25
                maximum = np.amax(temp)
                minimum = np.amax(temp)

                temp_row.append(mean)
                temp_row.append(median)
                temp_row.append(std)
                temp_row.append(iqr)
                temp_row.append(maximum)
                temp_row.append(minimum)
            stat_list.append(temp_row)

        df = pd.DataFrame(stat_list)

        # Insert label
        LABEL = 'Activity'
        labels = np.full(df.shape[0], activity)
        # Insert a column at the front with the right labels
        df.insert(loc=0, column=LABEL, value=labels)
        df.to_csv(pathToOpen + '\\' + activity + '_features.csv', header=headers, index=None)
