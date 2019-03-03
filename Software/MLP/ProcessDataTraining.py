import pandas as pd
import numpy as np
from pathlib import Path
import os

# replace path with your own path
path = str(Path().resolve().parent)+'\Data\Sensor'
activityList = ['wipers','number7','chicken', 'sidestep', 'turnclap', 'number6', 'swing', 'mermaid', 'salute', 'cowboy', 'byebye']
print(path)


window_size = 72
overlap = float(window_size * 0.50)


# normalize data between
def normalize_val(num, min_value, max_value):
    if min_value < max_value:
        return (num - min_value) / (max_value - min_value)
    if min_value > 0:
        return min_value / (min_value + 1)
    return min_value / (min_value - 1)


for fileName in os.listdir(path):
    for activity in activityList:
        if fileName.endswith(".csv") and fileName.find(activity.lower()) != -1 and fileName.find("new") != -1 and fileName.find('feature') == -1:
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
            segments = []
            labels = []
            for i in range(int(len(X) / overlap)):
                segments.append(X[int(i * overlap): int(((i * overlap) + window_size)), 0:])

            # ---------------------------------- Feature extraction ----------------------------------
            # Note: segments is an array of 2-d array. each segment in segments is a 2-d array
            for i in range(len(segments)):

                feature_col = []
                for j in range(0, np.size(segments[i], 1)):
                    temp_col = segments[i][0:, j]
                    # TODO: add more features
                    # Mean = sum of everything / no. of data point
                    mean = np.mean(temp_col)
                    # Median = middle value of sorted
                    median = np.median(temp_col)
                    # Std = Standard Deviation, How individual points differs from the mean
                    std = np.std(temp_col)
                    # iqr = Inter-Quartile Range, 75th percentile - 25th percentile
                    q75, q25 = np.percentile(temp_col, [75, 25])
                    iqr = q75 - q25

                    feature_col.append(mean)
                    feature_col.append(median)
                    feature_col.append(std)
                    feature_col.append(iqr)

                maximum = np.max(feature_col)
                minimum = np.min(feature_col)
                # Normalize data
                norm_row = [normalize_val(x, minimum, maximum) for x in feature_col]

                stat_list.append(norm_row)
            df = pd.DataFrame(stat_list)
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
    if fileName.endswith(".csv") and fileName.find("feature") != -1 and fileName.find("new") != -1 and fileName.find("combined") == -1:
        df = pd.read_csv(open(path + '\\' + fileName))
        print(fileName)
        df.dropna(how='any',inplace = True)
        list.append(df)
frame = pd.concat(list)

frame.to_csv(path + '\\' + 'combinedFeatureDataCSV_Arduino.csv', index=None)