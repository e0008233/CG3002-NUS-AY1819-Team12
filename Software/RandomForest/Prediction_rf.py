import numpy as np
import pandas as pd
from sklearn.externals import joblib
import os
from pathlib import Path

hashMap = {0:"chicken", 1:"number7", 2:"sidestep",3:"turnclap",4:"wiper"}
path = str(Path().resolve())
clf = joblib.load(path+'/randomForest/RandomForest_Arduino.pkl')

def predict(data){
    features = ProcessData.extract_features(data)
    features = pd.DataFrame(features).T
    rf_result = clf.predict(features)
    counts = np.bincount(test_predict)
    result = np.argmax(counts)
    result = hashMap(result)
    print("-------------------------------------")
    print("RF Predicted move:")
    print(result)

    return result

}