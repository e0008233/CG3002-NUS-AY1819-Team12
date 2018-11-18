import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
import os
from os import listdir


# replace paths with your own paths
sample_path = str(Path().resolve()) + '\\CG3002_Main\\Data\\Sensor\\'
output_path = "C:\\Users\\Jelena Neo\\CG3002_Neural_Net\\CG3002_Main\\Data\\Plots\\"

print(sample_path)
sensors = ["Accelerometer", "Gyroscope"]
sensor_name = ['rh', 'lh', 'leg']
figs = []


def save_figures(filename, figs):
    pp = PdfPages(filename)
    for fig in figs:
        fig.savefig(pp, format='pdf')
    pp.close()

def plot_axis(axis, title, data):
    axis.set_title(title)
    axis.set_xlabel("Time")
    axis.grid(True)
    axis.plot(data)


def plot_activity(activity, sensorType, data):
    fig, axes = plt.subplots(nrows=3, figsize=(10, 8))
    ax0, ax1, ax2 = axes.flatten()
    plot_axis(ax0, sensorType + " X-axis", data.filter(regex='_x'))
    plot_axis(ax1, sensorType + " Y-axis", data.filter(regex='_y'))
    plot_axis(ax2, sensorType + " Z-axis", data.filter(regex='_z'))
    fig.suptitle("Activity: " + activity, fontsize=14)
    plt.subplots_adjust(hspace=0.2)
    plt.subplots_adjust(top=0.90)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    # plt.show(block=False)
    figs.append(fig)


for file in listdir(sample_path):
    if "new" in file and "features" not in file:
        dataForPlot = pd.read_csv(sample_path + file)
        dataForPlot.dropna(how='any', inplace=True)
        dataForPlot = dataForPlot.iloc[:1000, 1:] # get the first 1000 samples
        danceName = file[:-4]
        for i in range(3):
            col_index = i * 6
            plot_activity(danceName + "_" + sensor_name[i], sensors[0], dataForPlot.iloc[:, col_index: col_index+3])
            plot_activity(danceName + "_" + sensor_name[i], sensors[1], dataForPlot.iloc[:, col_index+3: col_index+6])
        save_figures(output_path + danceName + "_raw_trace_plots.pdf", figs)
        plt.close('all')
        figs = []
