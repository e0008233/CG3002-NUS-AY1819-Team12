## Readme For Machine Learning component

There are multiple files used over the development of the project, but the final code used in our demo is in MLP and RandomForest folders.

## Installing packages on Rpi
The packages needed to run the programs are detailed in the final report under _5.4.5 Libraries/Packages used_

For installing on Rpi, use the following commands in the terminal:
* sudo apt install libatlas-base-dev
* sudo pip3 install tensorflow
* sudo apt-get install python3-matplotlib
* sudo apt-get install python3-numpy
* sudo apt-get install libblas-dev
* sudo apt-get install liblapack-dev
* sudo apt-get install python3-dev
* sudo apt-get install gfortran
* sudo apt-get install python3-setuptools
* sudo apt-get install python3-scipy
* sudo apt-get update
* sudo apt-get install python3-h5py
* sudo pip3 install keras 
* sudo pip3 install scikit-learn
* sudo apt-get install python3-pandas
* sudo pip3 install seaborn
* sudo pip3 install eli5
* sudo apt-get install python-dev ipython jupyter

## Readme For files in MLP folders
Note: configure the file paths properly to link to the right folders. Run the files using Python3.

If there are warnings shown, it is safe to ignore them according to research online.


* `EDA.py`: used for exploratory data analysis. 

* `mlp_model.py`: used to train and do validation fo the MLP model (includes feature importance analysis).
	* If running `feature_importance(create_model)`, enter `jupyter notebook` int the terminal Make sure that you are in the same directory where the `mlp_model.py` is at.
	* When the notebook has started create a new notebook and insert `%run mlp_model.py` in a cell and run that cell. This is needed so that you can view the result of feature analysis that is in HTML format.

* `prediction.py`: used in real-time recognition to load and predict dance moves

* `ProcessData.py`: used to preprocess data during real-time recognition

* `ProcessDataRpi.py`: used to preprocess data for training the model

* `grid_search.py`: used to find the most suitable parameters



* `14_Nov1850.h5`: the trained MLP model

* `14_Nov1850.sav`: the saved encoder to encode and decode multiclass labels


