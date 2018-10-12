import numpy as np

def extract_features(segment):

    temp_row = []
    for i in range(0, np.size(segment, 1)):
        temp = segment[0:, i]
        # Mean = sum of everything / no. of data point
        mean = np.mean(temp)
        # Median = middle value of sorted
        median = np.median(temp)
        # Std = Standard Deviation, How individual points differs from the mean
        std = np.std(temp)
        # iqr = Inter-Quartile Range, 75th percentile - 25th percentile
        q75, q25 = np.percentile(temp, [75, 25])
        iqr = q75 - q25
        maximum = np.amax(temp)
        minimum = np.amax(temp)

        temp_row.append(mean)
        temp_row.append(median)
        temp_row.append(std)
        temp_row.append(iqr)
        temp_row.append(maximum)
        temp_row.append(minimum)
    return temp_row
