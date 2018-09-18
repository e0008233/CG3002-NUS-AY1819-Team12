import pandas as pd
import numpy as np
from pathlib import Path

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn import svm
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
np.random.seed(0)

path = str(Path().resolve().parent) + '\Data'+ '\combinedFeatureDataCSV.csv'
print(path)

f = open(path)
df = pd.read_csv(f)
df.dropna(how = 'any',inplace=True)

features_name = df.columns[1:len(df)]

d = np.random.uniform(0, 1, len(df))
p = np.percentile(d, 75)
df['is_train'] = d <= p
train, test = df[df['is_train']==True], df[df['is_train']==False]
print('Number of observations in the training data:', len(train))
print('Number of observations in the test data:',len(test))

train_label = pd.factorize(train['Activity'])[0]
test_label = pd.factorize(test['Activity'])[0]

clf = RandomForestClassifier(n_estimators = 10, n_jobs=2, random_state=0)
clf.fit(train[features_name],train_label)
test_predict = clf.predict(test[features_name])
print ("-------------------")
print("Accuracy for RandomForest:", (accuracy_score(test_predict, test_label))*100)
accuracy = accuracy_score(test_predict, test_label)
print("RandomForest's accuracy score: {}".format(accuracy))
print(classification_report(test_predict, test_label, target_names=features_name))


clf2 = svm.SVC(kernel='linear')
clf2.fit(train[features_name],train_label)
test_predict_2 = clf2.predict(test[features_name])
print("Accuracy linear SVM: ", (accuracy_score(test_predict_2, test_label))*100)
accuracy = accuracy_score(test_predict_2, test_label)
print("linear SVM's accuracy score: {}".format(accuracy))
print(classification_report(test_predict_2, test_label, target_names=features_name))

clf3 = svm.SVC(kernel='rbf')
clf3.fit(train[features_name],train_label)
test_predict_3 = clf3.predict(test[features_name])
print("Accuracy for rbf SVM:", (accuracy_score(test_predict_3, test_label))*100)
accuracy = accuracy_score(test_predict_3, test_label)
print("rbf SVM's accuracy score: {}".format(accuracy))
print(classification_report(test_predict_3, test_label, target_names=features_name))
