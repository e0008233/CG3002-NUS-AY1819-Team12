from sklearn.externals import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn import preprocessing

from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import time

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
featureNameList = ['mean', 'median', 'std', 'iqr']

test_predict = clf.predict(df)

counts = np.bincount(test_predict)
result = np.argmax(counts)
print (test_predict)
print (hashMap[result])
