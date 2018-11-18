import numpy as np
import pandas as pd
import keras
import eli5
from eli5.sklearn import PermutationImportance
from IPython.core.display import display
from keras import optimizers
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import seaborn as sns
from sklearn.externals import joblib
import matplotlib.pyplot as plt
from keras.wrappers.scikit_learn import KerasClassifier
# gets rid of AVX warning
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

# key params
EPOCHS = 130
NUM_LABELS = 11
NUM_NEURONS = 10
NUM_NEURONS_INTERMED = 150


# load dataset
# change file_path to your own file path
file_path = 'C:\\Users\\Jelena Neo\\CG3002_Neural_Net\\CG3002_Main\\Data\\Sensor'
print(file_path)
mainDf = pd.read_csv(file_path + "\combinedFeatureDataCSV_Arduino.csv")
featureNames = list(mainDf.columns.values)
featureNames.remove('Activity')


df, testDf = train_test_split(mainDf, test_size=0.25)
# prepare data for processing i.e. extract labels etc.
X_train_intermmed = df.drop(df.columns[0], axis=1)  # input var
num_samples = X_train_intermmed.shape[0]
input_dim = X_train_intermmed.shape[1]    # also the num of features
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


# create model
# MLP using back propagation
def create_model(momentum=0.9, activation1='tanh'):
    # create model
    model = Sequential()
    model.add(Dense(NUM_NEURONS, input_dim=input_dim, activation='relu'))   #input layer
    model.add(Dense(NUM_NEURONS_INTERMED, activation=activation1))
    model.add(Dense(NUM_LABELS, activation='softmax'))  # output layer
    sgd = optimizers.SGD(lr=0.01, decay=0.5e-6, momentum=momentum, nesterov=True)
    # Compile model
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy']) #might wanna try other loss functions
    return model


def k_fold_val():
    kfold = StratifiedKFold(n_splits=10, shuffle=True)
    # get results
    cvscores = []
    for train, test in kfold.split(X_train, y):
        # create model
        model = create_model()
        # Fit the model
        model.fit(X_train[train], Y_train[train], epochs=EPOCHS, batch_size=5, verbose=0)
        # evaluate the model
        test_score = model.evaluate(X_train[test], Y_train[test], verbose=0)[1]
        cvscores.append(test_score * 100)
    print("Classification accuracy for 10-fold validation: {:.2f}% (+/- {:.2f}%)\n".format(np.mean(cvscores),
                                                                                           np.std(cvscores)))


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


def feature_importance(create_model):
    t_model = KerasClassifier(build_fn=create_model, epochs=EPOCHS, batch_size=5, verbose=0)
    t_model.fit(X_train,Y_train)
    perm = PermutationImportance(t_model, random_state=1).fit(X_train,Y_train)
    display(eli5.show_weights(perm, feature_names = featureNames))


if __name__ == '__main__':
    model = create_model()

    # #fit the model
    # model.fit(X_train, Y_train, epochs=EPOCHS, batch_size=5, verbose=0)
    #
    # #test set accuracy (Prediction on test set)
    # Y_pred = model.predict_classes(X_test)
    # labels = np.unique(encoded_Y)
    # targetNames = encoder.inverse_transform(labels)
    # print("Classification accuracy on test set: {:.2f}%\n".format(accuracy_score(encoded_Y_test, Y_pred) * 100))
    # print('Classification report for test set:')
    # report = classification_report(encoded_Y_test, Y_pred, target_names=targetNames)
    # print(report)
    # # need to close the pop-up containing the confusion matrix so that the program can continue
    # format_confusion_matrix(confusion_matrix(encoded_Y_test, Y_pred), targetNames).show()

    #saving model
    shld_save = input("save model? y/n: ")
    if (shld_save == 'y' or shld_save == 'N'):
        file_name = input('Enter model name: ')
        model.save(file_name + '.h5')  # creates a HDF5 file 'my_model.h5'
        joblib.dump(encoder, file_name + '.sav')
        del model  # deletes the existing model
        print("Saved model to disk")

    # Validate model using k-fold cross-validation and calculate errors and confusion matrix
    to_kfold = input('Run kfold? (y/n)? ')
    if to_kfold == 'y' or to_kfold == 'Y':
        k_fold_val()

    #uncomment the line(s) that you want to run
    feature_importance(create_model)