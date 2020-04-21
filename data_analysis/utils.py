from data_module.models import *
from data_module.mongo_scripts import *
from importlib import import_module

import dask.dataframe
import dask.bag


STEP = 1000


def get_researches_menu_context():
    context = {}
    context.update({"research_groups": ResearchGroup.objects.all()})
    context.update({"researches_without_group": Research.objects.filter(group=None)})
    return context


def get_datasets_by_research_id(research_id, n_rows=0):
    context = {}

    datasets = Dataset.objects.filter(researches=research_id)
    for dataset in datasets:
        dataset.entries = find_data(dataset.name, limit=n_rows)
        dataset.headers = Header.objects.filter(dataset=dataset).order_by('id')

    context.update({'research_datasets': datasets})
    return context


def add_dataset_details(dataset, starts_from=0, n_rows=0):
    context = {}
    context.update({'entries': find_data(dataset.name, skip=starts_from, limit=n_rows)})
    context.update({'headers': Header.objects.filter(dataset=dataset).order_by('id')})
    return context


@dask.delayed(nout=STEP)
def _query_mongo_delayed(dataset_name, from_row, to_row, projection=None):
    return list(find_data(dataset_name, limit=to_row, skip=from_row, projection=projection))


def _collect_dataframe(dataset_name, projection=None):
    n_rows = count_data(dataset_name)
    steps = (n_rows // STEP) + 1

    data = [_query_mongo_delayed(dataset_name, i*STEP, i+STEP, projection=projection) for i in range(0, steps)]

    frame = dask.bag.from_delayed(data).to_dataframe()
    return frame


def analyse(dataset, analyser, labels, projection=None, params={}):
    imported_analyser_module = import_module('analysis_module.' + analyser.get('module_name'))
    data_frame = _collect_dataframe(dataset.name, projection=projection)

    print(labels)

    data_frame.pop("_id")

    analysis_result = imported_analyser_module.analyse_data(data_frame, params=params)
    print(analysis_result)
