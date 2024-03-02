from __future__ import annotations

from typing import TYPE_CHECKING

from flask import jsonify

from config import DATABASE, TABLE_DATASETS_COLLECTION

if TYPE_CHECKING:
    import pymongo


# initial_answer.csv, meta_abs_error_rank.csv, meta_meta_abs_error.csv
def jgetter(client: pymongo.MongoClient, question_number: int):
    pipeline = [
        {'$match': {'dataset_name': 'jerry'}},
        {'$sample': {'size': 2}},
        {'$project': {
            'row_number': 1,
            'value': {'$objectToArray': {'$arrayElemAt': ['$row', question_number - 1]}},  # objectToArray does this: {'key1': 'value1', 'key2': 'value2'} -> [{'k': 'key1', 'v': 'value1'}, {'k': 'key2', 'v': 'value2'}]
            'rank': {'$objectToArray': {'$arrayElemAt': ['$row', question_number - 1 + 14]}},
            'error': {'$objectToArray': {'$arrayElemAt': ['$row', question_number - 1 + 28]}},
        }},
        {'$project': {
            '_id': 0,
            'row_number': 1,
            'value': {'$arrayElemAt': ['$value.v', 0]},  # syntax is $arrayElemAt: [array, index] idk why $value.v is an array but it is. (it's an array of length one)
            'rank': {'$arrayElemAt': ['$rank.v', 0]},
            'error': {'$arrayElemAt': ['$error.v', 0]},
        }}
    ]

    rows = list(client[DATABASE][TABLE_DATASETS_COLLECTION].aggregate(pipeline))

    # wow this sucks
    # the person at index 0 is 1 if the most accurate person is person 1
    # the person at index 0 is 2 if the most accurate person is person 2
    if int(rows[0]['rank']) < int(rows[1]['rank']):
        rows[0]['person'] = '1'
        rows[1]['person'] = '2'
    else:
        rows[0]['person'] = '2'
        rows[1]['person'] = '1'
    
    response = jsonify(rows)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response
