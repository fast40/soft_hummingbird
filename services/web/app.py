from flask import Flask, Response, request, render_template, redirect, abort
import pymongo

import backend
# TODO: either decide that this is stupid and fix it or remove this message
from helpers import url_bool

# this should be fork safe as long as nothing uses the client and triggers the connection before the fork happens
client = pymongo.MongoClient(backend.MONGO_URL, connect=False)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', datasets=backend.get_datasets(client))


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
