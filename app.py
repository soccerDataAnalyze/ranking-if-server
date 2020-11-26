#! /usr/bin/env python3
# coding: utf-8

import json

import pymongo
from flask_cors import CORS
from flask import Flask, jsonify
from flask import request

from modules import utils


app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/api/v1.0/ranking/', methods=['GET'])
def get_ranking():
    
    from_min = request.args.get("from")
    to_min = request.args.get("to")

    # get data from database 
    CONNECTION_STRING = "mongodb+srv://amaury:ObNw8j6guIlWAeuG@cluster0.ffeme.mongodb.net/rankinator?retryWrites=true&w=majority"
    client = pymongo.MongoClient(CONNECTION_STRING)

    db = client.rankinator
    collection = db.matchs

    cursor = collection.find({})
    matchs = []
    for document in cursor:
        matchs.append(document)

    # compute ranking with matchs data
    from_min = int(from_min)
    to_min = int(to_min)
    points = utils.get_points_between(matchs, from_min, to_min)
    ranking = utils.get_ranking(points)

    return jsonify({'ranking' : ranking })


if __name__ == '__main__':
    app.run(debug=True)
