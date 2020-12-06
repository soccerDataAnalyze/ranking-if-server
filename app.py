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


def get_matchs():

    # get data from database 
    CONNECTION_STRING = "mongodb+srv://amaury:ObNw8j6guIlWAeuG@cluster0.ffeme.mongodb.net/rankinator?retryWrites=true&w=majority"
    client = pymongo.MongoClient(CONNECTION_STRING)

    db = client.rankinator
    collection = db.matchs

    cursor = collection.find({})
    matchs = []
    for document in cursor:
        matchs.append(document)

    return matchs


def get_validator(constraints):

    validator = utils.GoalValidator()
    validator.add_constraint({'field': 'minute', 
                              'condition': '>', 
                              'ref': constraints['from_min']})
    validator.add_constraint({'field': 'minute', 
                              'condition': '<', 
                              'ref': constraints['to_min']})
    if constraints['body_part'] !=  'all':
        validator.add_constraint({'field': 'body_part', 
                                  'condition': '==',
                                  'ref': constraints['body_part']})
    if constraints['situation'] !=  'all':
        validator.add_constraint({'field': 'situation', 
                                  'condition': '==', 
                                  'ref': constraints['situation']})

    return validator



@app.route('/api/v1.0/team_ranking/', methods=['POST'])
def get_team_ranking():

    constraints = request.get_json()
    matchs = get_matchs()
    validator = get_validator(constraints)
    
    # compute ranking
    points = utils.get_points(matchs, validator)
    ranking = utils.get_ranking(points, ['points', 'gf'])

    return jsonify({'ranking' : ranking })


@app.route('/api/v1.0/scorer_ranking/', methods=['POST'])
def get_scorer_ranking():

    constraints = request.get_json()
    matchs = get_matchs()
    validator = get_validator(constraints)
    
    # compute ranking
    goals_by_player = utils.get_goals_by_player(matchs, validator)
    ranking = utils.get_ranking(goals_by_player, ['goals'])

    return jsonify({'ranking' : ranking })


@app.route('/api/v1.0/assister_ranking/', methods=['POST'])
def get_assister_ranking():

    constraints = request.get_json()
    matchs = get_matchs()
    validator = get_validator(constraints)
    
    # compute ranking
    assists_by_player = utils.get_assists_by_player(matchs, validator)
    ranking = utils.get_ranking(assists_by_player, ['assists'])

    return jsonify({'ranking' : ranking })


@app.route('/api/v1.0/clean_sheet_ranking/', methods=['POST'])
def get_clean_sheet_ranking():

    constraints = request.get_json()
    matchs = get_matchs()
    validator = get_validator(constraints)
    
    # compute ranking
    clean_sheets = utils.get_clean_sheets(matchs, validator)
    ranking = utils.get_ranking(clean_sheets, ['clean_sheets'])

    return jsonify({'ranking' : ranking })


@app.route('/api/v1.0/ranking_evolution/', methods=['POST'])
def get_ranking_evolution():

    team = request.get_json()['team']
    matchs = get_matchs()
    
    evolution = utils.get_ranking_evolution(matchs, team)

    return jsonify({'evolution' : evolution })


if __name__ == '__main__':
    app.run(debug=True)
