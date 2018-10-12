import numpy as np


def normalize_val(num, min_value, max_value):
    if min_value < max_value:
        return (num - min_value) / (max_value - min_value)
    if min_value > 0:
        return min_value / (min_value + 1)
    return min_value / (min_value - 1)


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
        maximum = np.max(temp)
        minimum = np.min(temp)

        temp_row.append(mean)
        temp_row.append(median)
        temp_row.append(std)
        temp_row.append(iqr)
        norm_row = [normalize_val(x, minimum, maximum) for x in temp_row]
    return norm_row
