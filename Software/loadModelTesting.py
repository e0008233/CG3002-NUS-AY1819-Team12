from sklearn.externals import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import time
hashMap = {0:"circle", 1:"lefttoright", 2:"uptodown"}

start = time.clock()
clf = joblib.load('RandomForest_Arduino.pkl')
path = str(Path().resolve().parent)+'\Data\Sensor'
activity = 'RealTest.csv'



df = pd.read_csv(open(path + '\\' + activity))
df.dropna(how='any', inplace=True)
dataSet = df.iloc[:, 1:7:1]
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
    # print (segment[i])
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
# Normalize data
df = (df - df.min()) / (df.max() - df.min())
# Round all values to 5 d.p.
df = df.round(5)
print (df)
df = pd.DataFrame(stat_list)
test_predict = clf.predict(df)

counts = np.bincount(test_predict)
result = np.argmax(counts)
print (hashMap[result])
