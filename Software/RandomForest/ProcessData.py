import pandas as pd
import numpy as np
from sklearn import preprocessing
from scipy.fftpack import fft
from pathlib import Path
from sklearn import preprocessing

import os

path = str(Path().resolve().parent.parent)+'\Data\Sensor\Dance'
activityList = ['wipers','number7','chicken', 'sideStep', 'turnclap']
print(path)

for fileName in os.listdir(path):

    for activity in activityList:
        if fileName.endswith(".csv") and fileName.find(activity) != -1 and fileName.find('feature') == -1:

            df = pd.read_csv(open(path + '\\' + fileName))

            df.dropna(how='any', inplace=True)
            dataSet = df.iloc[:, 1:]
            attriNameList = dataSet.columns[0:]
            X = dataSet.values
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
            for i in range(int(len(X) / overlap)):
                segment.append(X[i * overlap: ((i * overlap) + window_size), 0:])

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
                    maximum = np.max(temp)
                    minimum = np.min(temp)

                    temp_row.append(mean)
                    temp_row.append(median)
                    temp_row.append(std)
                    temp_row.append(iqr)
                    temp_row.append(maximum)
                    temp_row.append(minimum)
                stat_list.append(temp_row)

            # stat_list = preprocessing.normalize(stat_list)
            df = pd.DataFrame(stat_list)

            # Normalize data
            df = (df - df.min()) / (df.max() - df.min())
            # Round all values to 5 d.p.
            df = df.round(5)

            # Insert label
            LABEL = 'Activity'
            labels = np.full(df.shape[0], activity)
            # Insert a column at the front with the right labels
            df.insert(loc=0, column=LABEL, value=labels)
            headers.insert(0, LABEL)
            df.to_csv(path + '\\' + activity + '_features.csv', header=headers, index=None)

list = []
for fileName in os.listdir(path):
    if fileName.endswith(".csv") and fileName.find("feature") != -1 and fileName.find("combined") == -1:
        df = pd.read_csv(open(path + '\\' + fileName))
        df.dropna(how='any',inplace = True)
        list.append(df)
frame = pd.concat(list)

frame.to_csv(path + '\\' + 'combinedFeatureDataCSV_Dance.csv', index=None)