import dask.dataframe
import datetime
import os


def process_file(file):
    dir_abs_path = os.path.abspath(os.curdir)
    upload_module_path = 'upload_module'
    temp_files_path = 'temp_files'
    csv_path = 'csv'
    file_rel_path = 'dataset_{}_temp.csv'.format(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))

    file_destination = os.path.join(dir_abs_path, upload_module_path, temp_files_path, csv_path, file_rel_path)
    print('Temporary file created at {}'.format(file_destination))

    with open(file_destination, 'wb+') as temp:
        for chunk in file.chunks():
            temp.write(chunk)

    data = dask.dataframe.read_csv(file_destination, dtype=object, blocksize=1000000)
    chunks = []

    for partition in data.partitions:
        chunks.append(partition.compute())

    os.remove(file_destination)
    print('Data processed. Temporary file removed from {}'.format(file_destination))
    return chunks
