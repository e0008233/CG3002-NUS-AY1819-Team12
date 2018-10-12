import numpy as np
import pandas as pd
import keras
from keras import optimizers
from keras.models import Sequential
from keras.layers import Dense, Activation
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import seaborn as sns
from sklearn.externals import joblib
import matplotlib.pyplot as plt
from pathlib import Path
# gets rid of AVX warning
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'


EPOCHS = 50
NUM_LABELS = 5
NUM_NEURONS = 10

# to remove the below section when actual data comes
# fix random seed for reproducibility
# seed = 7
# np.random.seed(seed)

# load dataset
file_path = str(Path().resolve()) + '\CG3002_Main\Data\Sensor'
# file_path = os.path.dirname(os.path.abspath(__file__))
print(file_path)
mainDf = pd.read_csv(file_path + "\combinedFeatureDataCSV_Arduino.csv")

df, testDf = train_test_split(mainDf, test_size=0.25)
# prepare data for processing i.e. extract labels etc.
X_train = df.drop(df.columns[0], axis=1)  # input var
num_samples = X_train.shape[0]
input_dim = X_train.shape[1]    # also the # of features
X_train = X_train.values
y = df.iloc[:, 0]  # output var
Y = y.values.ravel()

# encode class values as integers
encoder = LabelEncoder()
encoded_Y = encoder.fit_transform(Y)
# convert integers to dummy variables (i.e. one hot encoded)
Y_train = keras.utils.to_categorical(encoded_Y, num_classes=NUM_LABELS)

X_test = testDf.drop(testDf.columns[0], axis=1).values
Y_test = testDf.iloc[:, 0].values.ravel()
encoded_Y_test = encoder.fit_transform(Y_test)
Y_test = keras.utils.to_categorical(encoded_Y_test, num_classes=NUM_LABELS)

temp = num_samples + X_test.shape[0]
print("Number of observations in training data: {} ({:.2f}%)".format(num_samples, num_samples / temp * 100))
print("Number of observations in test data: {} ({:.2f}%)\n".format(X_test.shape[0], X_test.shape[0] / temp * 100))

# define baseline model
# MLP using back propagation
def baseline_model():
    # create model
    model = Sequential()
    model.add(Dense(NUM_NEURONS, input_dim=input_dim, activation='relu'))   #input layer
    model.add(Dense(NUM_LABELS, activation='softmax'))  # output layer
    # Compile model
    sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy']) #might wanna try other loss functions
    # model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy']) #might wanna try other loss functions
    # https://www.dlology.com/blog/quick-notes-on-how-to-choose-optimizer-in-keras/
    # print(model.summary())
    return model


# feed data into model
# need to define # of iterations(epochs) and batch size
model = baseline_model()


# validate model and calculate errors and confusion matrix
# evaluating using K-fold cross-validation
# kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
kfold = StratifiedKFold(n_splits=10, shuffle=True)


# get results
cvscores = []
for train, test in kfold.split(X_train, y):
    # create model
    model = baseline_model()
    # Fit the model
    model.fit(X_train[train], Y_train[train], epochs=EPOCHS, batch_size=5, verbose=0)
    # evaluate the model
    scores = model.evaluate(X_train[test], Y_train[test], verbose=0)
    # print("%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))
    cvscores.append(scores[1] * 100)
print("Classification accuracy for 10-fold validation: {:.2f}% (+/- {:.2f}%)\n".format(np.mean(cvscores), np.std(cvscores)))


def format_confusion_matrix(confusion_matrix, class_names, figsize=(10, 7), fontsize=13):
    df_cm = pd.DataFrame(
        confusion_matrix, index=class_names, columns=class_names,
    )
    fig = plt.figure(figsize=figsize)
    try:
        heatmap = sns.heatmap(df_cm, annot=True, fmt="d")
    except ValueError:
        raise ValueError("Confusion matrix values must be integers.")
    heatmap.yaxis.set_ticklabels(heatmap.yaxis.get_ticklabels(), rotation=0, ha='right', fontsize=fontsize)
    heatmap.xaxis.set_ticklabels(heatmap.xaxis.get_ticklabels(), rotation=45, ha='right', fontsize=fontsize)
    plt.ylabel('True label', fontsize=15)
    plt.xlabel('Predicted label', fontsize=15)
    plt.title('Confusion Matrix', fontsize=18)
    plt.tight_layout()
    return plt


Y_pred = model.predict_classes(X_test)
labels = np.unique(encoded_Y)
targetNames = encoder.inverse_transform(labels)
print("Classification accuracy on test set: {:.2f}%\n".format(accuracy_score(encoded_Y_test, Y_pred) * 100))
print('Classification report:')
report = classification_report(encoded_Y_test, Y_pred, target_names=targetNames)
print(report)

print("Parameters used:")
print("Number of neurons: {}".format(NUM_NEURONS))
print("Number of epochs: {}".format(EPOCHS))
print("Number of layers: {}".format(2))

format_confusion_matrix(confusion_matrix(encoded_Y_test, Y_pred), targetNames).show()


# saving model
json_model = model.to_json()
open('model_architecture.json', 'w').write(json_model)
# saving weights
model.save_weights('model_weights.h5', overwrite=True)
filename = 'encoder.sav'
joblib.dump(encoder, filename)
print()
print("Saved model to disk")


