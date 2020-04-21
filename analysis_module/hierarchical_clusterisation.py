import dask.dataframe
from scipy.cluster.hierarchy import *
from matplotlib import pyplot as plt


def analyse_data(data_frame, params):
    # varieties = []
    # if labels is None:
    #     varieties.append(frame.pop('_id'))
    # else:
    #     varieties.append(frame.pop(labels[0]))
    mergings = linkage(data_frame, method=params['method'], metric=params['metric'])

    # fig = plt.figure(figsize=(25, 10))
    # dendrogram(mergings, truncate_mode='level')
    # plt.show()
    return mergings
