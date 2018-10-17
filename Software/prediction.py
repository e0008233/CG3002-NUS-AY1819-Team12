import numpy as np
import processLiveData
from keras.models import model_from_json
from sklearn.externals import joblib
from keras import optimizers
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'


# loading model and encoder
with open('model_architecture.json', 'r') as f:
    loaded_model_json = f.read()
model = model_from_json(loaded_model_json)
model.load_weights('model_weights.h5')
encoder = joblib.load('encoder.sav')
sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
activity_list = encoder.inverse_transform([0, 1, 2, 3, 4])
print(activity_list)


def predict(data):
    features = processLiveData.extract_features(data)
    mlp_result = model.predict_classes(features)
    rf_result = model.predict(features)
    # find the most common label in result
    mlp_counts = np.bincount(mlp_result)
    mlp_result = np.argmax(mlp_counts)
    mlp_result = activity_list[mlp_result]
    rf_counts = np.bincount(rf_result)
    rf_result = np.argmax(rf_counts)
    #TODO: get orig label for RF
    # rf_result =
    print("MLP Predicted move: {}".format(mlp_result))
    print("RF Predicted move: {}".format(rf_result))
    return mlp_result, rf_result
