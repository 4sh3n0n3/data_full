import dask.dataframe
import datetime
from scipy.cluster.hierarchy import *


def analyse_data(data_frame, params):
    now = datetime.datetime.now()
    dist_matrix = linkage(data_frame, method=params['method'], metric=params['metric'])
    print('скорость кластеризации O(n^2): ', datetime.datetime.now() - now)
    context = {
        'min_dist': min([dist[2] for dist in dist_matrix]),
        'max_dist': max([dist[2] for dist in dist_matrix]),
    }

    if params['is_flattened'] == 'True':
        flattened = fcluster(dist_matrix, t=float(params['threshold']), criterion=params['criterion'])
        context.update({'is_flattened': True})
        context.update({'num_of_clusters': max(flattened)})
        context.update({'threshold': params['threshold']})
        context.update({'criterion': params['criterion']})
        return flattened, context
    else:
        context.update({'is_flattened': False})
        context.update({'num_of_clusters': max([dist[1] for dist in dist_matrix])})
        return dist_matrix, context
