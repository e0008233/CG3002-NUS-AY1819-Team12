import pandas as pd
import keras
from keras import optimizers
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from keras.wrappers.scikit_learn import KerasClassifier
# gets rid of AVX warning, safe to ignore
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'


# key params
EPOCHS = 130
NUM_LABELS = 11
NUM_NEURONS = 10
NUM_NEURONS_INTERMED = 150


def create_model(activation='tanh'):
    # create model
    model = Sequential()
    model.add(Dense(NUM_NEURONS, input_dim=72, activation='relu'))  # input layer
    model.add(Dense(NUM_NEURONS_INTERMED, activation=activation))
    model.add(Dense(NUM_LABELS, activation='softmax'))  # output layer
    sgd = optimizers.SGD(lr=0.01, decay=0.5e-6, momentum=0.9, nesterov=True)
    # Compile model
    model.compile(loss='categorical_crossentropy', optimizer=sgd,
                  metrics=['accuracy'])  # might wanna try other loss functions
    return model

def grid_search():
    # load dataset
    # change file_path to your own file path
    file_path = 'C:\\Users\\Jelena Neo\\CG3002_Neural_Net\\CG3002_Main\\Data\\Sensor'
    print(file_path)
    mainDf = pd.read_csv(file_path + "\combinedFeatureDataCSV_Arduino.csv")

    df, testDf = train_test_split(mainDf, test_size=0.25)
    # prepare data for processing i.e. extract labels etc.
    X_train_intermmed = df.drop(df.columns[0], axis=1)  # input var
    num_samples = X_train_intermmed.shape[0]
    input_dim = X_train_intermmed.shape[1]  # also the num of features
    X_train = X_train_intermmed.values
    y = df.iloc[:, 0]  # output var
    Y = y.values.ravel()

    # encode class values as integers
    encoder = LabelEncoder()
    encoded_Y = encoder.fit_transform(Y)
    # convert integers to dummy variables (i.e. one hot encoded)
    Y_train = keras.utils.to_categorical(encoded_Y, num_classes=NUM_LABELS)

    X_test_intermmed = testDf.drop(testDf.columns[0], axis=1)
    X_test = X_test_intermmed.values
    Y_test_intermmed = testDf.iloc[:, 0]
    Y_test = Y_test_intermmed.values.ravel()
    encoded_Y_test = encoder.fit_transform(Y_test)
    Y_test = keras.utils.to_categorical(encoded_Y_test, num_classes=NUM_LABELS)

    temp = num_samples + X_test.shape[0]
    print("Number of observations in training data: {} ({:.2f}%)".format(num_samples, num_samples / temp * 100))
    print("Number of observations in test data: {} ({:.2f}%)\n".format(X_test.shape[0], X_test.shape[0] / temp * 100))


    epochs = [70,80,90,100,120,130]
    activation = ['relu','tanh','sigmoid','hard_sigmoid']
    param_grid = dict(epochs=epochs, activation=activation)
    grid_model = KerasClassifier(build_fn=create_model, epochs=EPOCHS, batch_size=5, verbose=0)
    grid = GridSearchCV(estimator=grid_model, param_grid=param_grid, n_jobs=-1, scoring='accuracy', cv=10)
    grid_result = grid.fit(X_train, encoded_Y)
    # summarize results
    print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
    means = grid_result.cv_results_['mean_test_score']
    stds = grid_result.cv_results_['std_test_score']
    params = grid_result.cv_results_['params']
    for mean, stdev, param in zip(means, stds, params):
        print("%f (%f) with: %r" % (mean, stdev, param))

if __name__ == '__main__':
    # need to wrap the whole code in a function to use parallel-computing in a script
    grid_search()
