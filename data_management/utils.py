from data_module.models import *
from importlib import import_module
from data_module.mongo_scripts import insert_data
import pandas as pd


def get_researches_menu_context():
    context = {}
    context.update({"research_groups": ResearchGroup.objects.all()})
    context.update({"researches_without_group": Research.objects.filter(group=None)})
    return context


def upload_data_to_dataset(file, file_type, dataset):
    imported_module = import_module('upload_module.' + file_type)
    partitions = imported_module.process_file(file)

    _proceed_headers(partitions[0].columns, dataset)

    for partition in partitions:
        insert_data(eval(partition.fillna(value='').to_json(index=False, orient='table', force_ascii=False)).get('data'),
                    dataset.name)


def _proceed_headers(headers, dataset):
    for header in headers:
        base_user_type = CustomType.objects.filter(is_default_for_base=True).order_by('created_at').first()
        header = Header(name=header, dataset=dataset, custom_type=base_user_type)
        header.save()
