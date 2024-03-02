from flask import Flask, Response, request, render_template, redirect, abort, url_for
import pymongo

import datasets
import services
import backend
# TODO: either decide that this is stupid and fix it or remove this message
from helpers import url_bool

# this should be fork safe as long as nothing uses the client and triggers the connection before the fork happens
client = pymongo.MongoClient(backend.MONGO_URL, connect=False)

app = Flask(__name__)



@app.route('/')
def index():
    with open('static/javascript/fill_template.js') as file:
        javascript_code = file.read()

    with open('templates/template.html') as file:
        html_code = file.read()

    return render_template('index.html', html_code=html_code, javascript_code=javascript_code)


@app.route('/test')
def test():
    url = request.args.get('url', 'http://localhost')

    return render_template('test.html', url=url)


@app.route('/dashboard')
def dashboard():
    return render_template('datasets.html',
        file_datasets=datasets.get_file_datasets(client),
        table_datasets=datasets.get_table_datasets(client)
    )


@app.route('/create-dataset', methods=['POST'])
def create_dataset():
    dataset_name = request.form.get('dataset_name')
    dataset_type = request.form.get('dataset_type')

    # this object is a wrapper around a tempfile.SpooledTemporaryFile, so it contains the actual zip file data
    zip_file = request.files.get('zip_file')  

    if dataset_type == 'file':
        datasets.create_file_dataset(dataset_name, zip_file, client)
    elif dataset_type == 'table':
        datasets.create_table_dataset(dataset_name, zip_file, client)
    else:
        abort(400, 'Incorrect dataset type. This should never happen; if it does please notify someone.')

    return redirect(url_for('index'))


@app.route('/delete-dataset')
def delete_dataset():
    dataset_name = request.args.get('dataset_name')
    dataset_type = request.args.get('dataset_type')

    if dataset_type == 'file':
        datasets.delete_file_dataset(dataset_name, client)
    elif dataset_type == 'table':
        datasets.delete_table_dataset(dataset_name, client)
    else:
        abort(400, 'Incorrect dataset type. This should never happen; if it does please notify someone.')

    return redirect(url_for('index'))


@app.route('/query-dataset')
def query_dataset():
    question_number = request.args.get('question_number', int)

    return services.jgetter(client, int(question_number))


@app.route('/upload', methods=['POST'])
def upload():
    dataset_name = request.form.get('dataset_name')
    survey_id = request.form.get('survey_id')

    # zip_file should be of type werkzeug.datastructures.file_storage.FileStorage, which is a thin wrapper around tempfile.SpooledTemporaryFile.
    # tempfile.SpooledTemporaryFile is just a temporary file stored in memory unless its too large, in which case it begins using disk storage
    zip_file = request.files.get('zip_file')

    backend.create(dataset_name, survey_id, zip_file, client)

    return redirect('/')


@app.route('/get_file')
def get_file():
    survey_id = request.args.get('survey_id')
    response_id = request.args.get('response_id')
    loop_number = request.args.get('loop_number', type=int)
    should_redirect = request.args.get('redirect', type=url_bool)

    if None in (loop_number, response_id, should_redirect):
        abort(400, 'The URL is missing required parameters and/or gives them invalid types.')

    path = backend.get_file_path(response_id, str(loop_number), str(survey_id), client)

    if should_redirect:
        return redirect(f'/file/{path.removeprefix("/")}')
    else:
        response = Response(path)
        response.headers['Access-Control-Allow-Origin'] = '*'

        return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
