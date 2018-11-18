import numpy as np
import pandas as pd
from sklearn.externals import joblib
import os
import ProcessData
from pathlib import Path

hashMap = {0:"number7",1:"byebye", 2:"chicken",3:"cowboy",4:"mermaid",5:"numbersix",6:"numner7",7:"number7",8:"salute",9:"sidestep",10:"swing",11:"turnclap",12:"wipers"}
# hashMap = {0:"chicken", 1:"sidestep", 2:"wipers"}
path = str(Path().resolve())
clf = joblib.load(path+'/randomForest/RandomForest_Arduino.pkl')

def predict(data):
    features = ProcessData.extract_features(data)
    features = pd.DataFrame(features).T 
    rf_result = clf.predict(features)
    counts = np.bincount(rf_result)
    result = np.argmax(counts)
    result = hashMap[result]
    print("-------------------------------------")
    print("RF Predicted move:")
    print(result)

    return result


