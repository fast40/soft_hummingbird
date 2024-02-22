import pathlib
import zipfile
import random

MONGO_URL = 'mongodb://mongo:27017'

DATABASE = 'survey'

DATASETS_COLLECTION = 'datasets'
RESPONSES_COLLECTION = 'responses'

FILES_DIRECTORY = pathlib.Path('/files')


# assuming this is used as intended, flask passes a temporary file to zip_file (so zip_file is not a path but the actual contents of a file)
def create(dataset_name, zip_file, client):
    dataset_path = FILES_DIRECTORY.joinpath(dataset_name)

    if dataset_path.exists():
        raise FileExistsError('Dataset has already been created once.')

    with zipfile.ZipFile(zip_file) as zf:
        zf.extractall(dataset_path)

    client[DATABASE][DATASETS_COLLECTION].insert_many({
        'dataset_name': dataset_name,
        'file_path': str(file_path.relative_to(FILES_DIRECTORY)),
        'loop_number': str(i + 1)
    } for i, file_path in enumerate(file_path for file_path in dataset_path.rglob('*') if file_path.is_file() and file_path.name[0] != '.'))


def get_datasets(client):
    return client[DATABASE][DATASETS_COLLECTION].distinct('dataset_name')


def pick_response_dataset(client):
    dataset_names = client[DATABASE][DATASETS_COLLECTION].distinct('dataset_name')

    # TODO: this can and probably should be done with an aggregation pipeline
    # this basically gets the number of uses on each dataset as indicated by the responses
    # the code goes on to only include the datasets with the minimum number of views
    dataset_uses = [{
        'dataset_name': dataset_name,
        'uses': client[DATABASE][RESPONSES_COLLECTION].count_documents({'dataset_name': dataset_name})
    } for dataset_name in dataset_names]

    min_uses = min(dataset_uses, key=lambda x: x['uses'])['uses']

    candidate_datasets = [dataset['dataset_name'] for dataset in dataset_uses if dataset['uses'] == min_uses]

    dataset_choice = random.choice(candidate_datasets)

    return dataset_choice


def get_file_path(response_id, loop_number: str, client):
    response = client[DATABASE][RESPONSES_COLLECTION].find_one({'response_id': response_id})

    if response is None:
        print(1)
        dataset_name = pick_response_dataset(client)
        client[DATABASE][RESPONSES_COLLECTION].insert_one({'response_id': response_id, 'dataset_name': dataset_name})
    elif loop_number in response:
        print(2)
        return response[loop_number]
    else:
        print(3)
        dataset_name = response['dataset_name']

    print('---------------------')
    print(dataset_name)
    print(loop_number)
    print('---------------------')
    file_path = client[DATABASE][DATASETS_COLLECTION].find_one({'dataset_name': dataset_name, 'loop_number': loop_number})['file_path']

    client[DATABASE][RESPONSES_COLLECTION].update_one({'response_id': response_id}, {'$set': {loop_number: file_path}})

    return file_path
