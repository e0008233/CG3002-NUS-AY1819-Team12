import numpy as np
import pandas as pd
from keras.models import model_from_json
from sklearn.externals import joblib
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'


# loading model and encoder
model = model_from_json(open('model_architecture.json').read())
model.load_weights('model_weights.h5')
encoder = joblib.load('encoder.sav')
print("Loaded model from disk\n")


# path = str(Path().resolve())
# print(path)
# path = "C:\\Users\\Jelena Neo\\CG3002_Neural_Net\\CG3002_Main\\Data\\Sensor"
path = os.path.dirname(os.path.abspath(__file__))


df = pd.read_csv(path + '\\training_circle.csv')
# calculations to process data
df.dropna(how='any', inplace=True)
X = df.iloc[:300, 1:7].values
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
        maximum = np.max(temp)
        minimum = np.min(temp)

        temp_row.append(mean)
        temp_row.append(median)
        temp_row.append(std)
        temp_row.append(iqr)
        temp_row.append(maximum)
        temp_row.append(minimum)
    stat_list.append(temp_row)

df = pd.DataFrame(stat_list)
df = (df - df.min()) / (df.max() - df.min())
# Round all values to 5 d.p.
X_real = df.round(5).values


model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
result = model.predict_classes(X_real)
# find the most common label in result
counts = np.bincount(result)
result = np.argmax(counts)
# transform numerical label back to original activity
result = encoder.inverse_transform(result)
print("Predicted move: {}".format(result))
