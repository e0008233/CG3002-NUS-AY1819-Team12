from sklearn.externals import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn import preprocessing

from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import time
hashMap = {0:"chicken", 1:"number7", 2:"sidestep",3:"turnclap",4:"wiper"}

path = str(Path().resolve())

clf = joblib.load(path+'/RandomForest_Arduino.pkl')
f = open(path+"/test_turnclap.csv")
df = pd.read_csv(f)
test_predict = clf.predict(df)

counts = np.bincount(test_predict)
result = np.argmax(counts)
print (test_predict)
print (hashMap[result])