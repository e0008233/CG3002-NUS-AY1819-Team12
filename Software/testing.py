import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cross_validation import cross_val_score
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import time
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
np.random.seed(5)
start = time.clock()

# path = str(Path().resolve().parent) + '\Data\Subject'+ '\combinedFeatureDataCSV.csv'
path = str(Path().resolve().parent) + '\Data'+ '\combinedFeatureDataCSV_Arduino.csv'

print(path)

f = open(path)
df = pd.read_csv(f)
df.dropna(how = 'any',inplace=True)

features_name = df.columns[1:len(df)]
print('Number of features:',len(features_name))
d = np.random.uniform(0, 1, len(df))
p = np.percentile(d, 75)
df['is_train'] = d <= p
train, test = df[df['is_train']==True], df[df['is_train']==False]
print('Number of observations in the training data:', len(train))
print('Number of observations in the test data:',len(test))

train_label = pd.factorize(train['Activity'],sort=True)[0]
test_label,test_uni = pd.factorize(test['Activity'],sort=True)

clf = RandomForestClassifier(n_estimators =50, max_features = 'sqrt', n_jobs=2, min_samples_leaf = 1,criterion = 'entropy')
averageScore = np.mean(cross_val_score(clf, train[features_name], train_label, cv=10))
if (averageScore>0.95):
    print ("The classifier is good and average score for training is %s . " % averageScore)
else:
    if (averageScore<0.9):
        print ("The classifier is not bad and average score for training is %s . " % averageScore)
    else:
        print ("The classifier needs to be improved  and average score for training is %s . " % averageScore)
clf.fit(train[features_name],train_label)
test_predict = clf.predict(test[features_name])

# 10-Fold Cross validation

print ("-------------------")
print("Accuracy for RandomForest:", (accuracy_score(test_predict, test_label))*100)
accuracy = accuracy_score(test_predict, test_label)

print(classification_report(test_predict, test_label, target_names=test_uni))
print (confusion_matrix(test_label, test_predict,labels = [0,1,2]))
# joblib.dump(clf, 'RandomForest_Arduino.pkl')
joblib.dump(clf, 'RandomForest_Arduino.pkl')
end = time.clock()
print ("processing time of the model is: ",end - start)

# path = str(Path().resolve().parent) + '\Data'+ '\Sensor\circle_features.csv'
# f = open(path)
# df = pd.read_csv(f)
# df.dropna(how = 'any',inplace=True)
# df = df.iloc[:, 1:37:1]
# X= df.values
# test_predict = clf.predict(X)
# print (test_predict)

# clf2 = svm.SVC(kernel='linear')
# clf2.fit(train[features_name],train_label)
# test_predict_2 = clf2.predict(test[features_name])
# print("Accuracy linear SVM: ", (accuracy_score(test_predict_2, test_label))*100)
# accuracy = accuracy_score(test_predict_2, test_label)
# print("linear SVM's accuracy score: {}".format(accuracy))
# print(classification_report(test_predict_2, test_label, target_names=features_name))
# confusion_matrix(test_label, test_predict_2)
#
# clf3 = svm.SVC(kernel='rbf')
# clf3.fit(train[features_name],train_label)
# test_predict_3 = clf3.predict(test[features_name])
# print("Accuracy for rbf SVM:", (accuracy_score(test_predict_3, test_label))*100)
# accuracy = accuracy_score(test_predict_3, test_label)
# print("rbf SVM's accuracy score: {}".format(accuracy))
# print(classification_report(test_predict_3, test_label))

# print (confusion_matrix(test_label, test_predict_3))

