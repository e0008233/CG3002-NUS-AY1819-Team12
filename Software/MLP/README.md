## Readme for files in MLP folder
Note: Configure the file paths properly to link to the right folders. Run the files using Python3.

If there are warnings shown, it is safe to ignore them (according to research online).

**Run `ProcessDataTraining.py` first before any other programs.**


* `ExploratoryDataAnalysis.py`: Plot raw data to expose trends and anomalies.

    * Plot of raw data (Accelerometer X-axis) for a dance move called "Salute"

    ![](https://github.com/jelneo/CG3002-NUS-AY1819-Team12/blob/master/Software/MLP/images/raw_plot_salute_dance_right_hand.png | width=200)

* `mlp_model.py`: used to train and do validation fo the MLP model (includes feature importance analysis).
	* Only this file needs to be run on jupyter. For the other files, it can be run on other IDEs.
	* If running `feature_importance(create_model)` (uncomment that line), enter `jupyter notebook` in the terminal. Make sure that you are in the same directory where the `mlp_model.py` is at.
	* When the notebook has started create a new notebook and insert `%run mlp_model.py` in a cell and run that cell. This is needed so that you can view the result of feature analysis that is in HTML format.

    Outputs for:
    * Confusion matrix

    ![](https://github.com/jelneo/CG3002-NUS-AY1819-Team12/blob/master/Software/MLP/images/confusion_matrix.JPG | width=200)

    * Feature importance

    ![](https://github.com/jelneo/CG3002-NUS-AY1819-Team12/blob/master/Software/MLP/images/feature_importance.JPG | width=200)

* `prediction.py`: used in real-time recognition to load and predict dance moves

* `ProcessDataRealTime.py`: used to preprocess data during real-time recognition

* `ProcessDataTraining.py`: used to preprocess data for training the model

* `grid_search.py`: used to find the most suitable parameters

* `14_Nov1850.h5`: the trained MLP model

* `14_Nov1850.sav`: the saved encoder to encode and decode multiclass labels


