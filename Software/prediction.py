import numpy as np
import pandas as pd
import ProcessData
from keras.models import load_model
from sklearn.externals import joblib
from keras import optimizers
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

# loading model and encoder
file_name = '14Nov_1850'
model = load_model(file_name + '.h5')

encoder = joblib.load(file_name + '.sav')
activity_list = encoder.inverse_transform(list(range(11)))
print(activity_list)


def predict(data):
    features = ProcessData.extract_features(data)
    features = pd.DataFrame(features).T
    mlp_result = model.predict_classes(features)

    mlp_counts = np.bincount(mlp_result)
    mlp_result = np.argmax(mlp_counts)
    mlp_result = activity_list[mlp_result]

    print("MLP Predicted move: {}".format(mlp_result))

    return mlp_result
