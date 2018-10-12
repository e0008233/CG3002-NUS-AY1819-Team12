import pandas as pd
import numpy as np
from sklearn import preprocessing
from scipy.fftpack import fft
from pathlib import Path
import os

path = str(Path().resolve().parent)+'\Data\Sensor'
activityList = ['Wipers','NumberSeven','Chicken', 'SideStep', 'Turnclap']
activityList_lower = [activity.lower() for activity in activityList]
# print(activityList_lower)
print(path)


def normalize(df):
    result = df.copy()
    for col in df.columns:
        max_value = df[col].max()
        min_value = df[col].min()
        if min_value < max_value:
            result[col] = (df[col] - min_value) / (max_value - min_value)
        elif min_value > 0:
            result[col] = min_value / (min_value + 1)
        else:
            result[col] = min_value / (min_value - 1)
    return result


def normalize_val(num, min_value, max_value):
    if min_value < max_value:
        return (num - min_value) / (max_value - min_value)
    if min_value > 0:
        return min_value / (min_value + 1)
    return min_value / (min_value - 1)

for fileName in os.listdir(path):
    for activity in activityList_lower:
        if fileName.endswith(".csv") and fileName.find(activity) != -1 and fileName.find('feature') == -1:
            df = pd.read_csv(open(path + '\\' + fileName))

            df.dropna(how='any', inplace=True)
            dataSet = df.iloc[:, 1:]
            attriNameList = dataSet.columns[0:]
            X = dataSet.values
            # create headers for features
            headers = []
            featureNameList = ['mean', 'median', 'std', 'iqr']
            for attriName in attriNameList:
                for featureName in featureNameList:
                    headers.append(attriName + '_' + featureName)
            stat_list = []
            # windows of 2.56 sec and 50% overlap (128 readings/window), details in report section 5
            window_size = 128
            overlap = window_size // 2
            segments = []
            labels = []
            for i in range(int(len(X) / overlap)):
                segments.append(X[i * overlap: ((i * overlap) + window_size), 0:])

            # ---------------------------------- Feature extraction ----------------------------------
            for i in range(len(segments)):

                temp_row = []
                for j in range(0, np.size(segments[i], 1)):
                    temp = segments[i][0:, j]
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


                    temp_row.append(mean)
                    temp_row.append(median)
                    temp_row.append(std)
                    temp_row.append(iqr)
                maximum = np.max(temp_row)
                minimum = np.min(temp_row)
                norm_row = [normalize_val(x, minimum, maximum) for x in temp_row]
                stat_list.append(norm_row)

            df = pd.DataFrame(stat_list)
            # Normalize data
            # df = normalize(df)
            df = df.round(5)

            # Insert label
            LABEL = 'Activity'
            labels = np.full(df.shape[0], activity)
            # Insert a column at the front with the right labels
            df.insert(loc=0, column=LABEL, value=labels)
            headers.insert(0, LABEL)
            df.to_csv(path + '\\' + fileName[:-4] + '_features.csv', header=headers, index=None)

list = []
for fileName in os.listdir(path):
    if fileName.endswith(".csv") and fileName.find("feature") != -1 and fileName.find("combined") == -1:
        df = pd.read_csv(open(path + '\\' + fileName))
        df.dropna(how='any',inplace = True)
        list.append(df)
frame = pd.concat(list)

frame.to_csv(path + '\\' + 'combinedFeatureDataCSV_Arduino.csv', index=None)