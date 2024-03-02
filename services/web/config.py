import pathlib

DATASETS_FOLDER = pathlib.Path('/datasets')

FILE_DATASETS_FOLDER = DATASETS_FOLDER.joinpath('file')
TABLE_DATASETS_FOLDER = DATASETS_FOLDER.joinpath('table')

DATABASE = 'soft_hummingbird'

FILE_DATASETS_COLLECTION = 'file_datasets'
TABLE_DATASETS_COLLECTION = 'table_datasets'
