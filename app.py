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


def get_matchs(championship):

    # get data from database 
    CONNECTION_STRING = "mongodb+srv://amaury:ObNw8j6guIlWAeuG@cluster0.ffeme.mongodb.net/rankinator?retryWrites=true&w=majority"
    client = pymongo.MongoClient(CONNECTION_STRING)

    db = client.rankinator
    collection = db['championship']

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



@app.route('/api/v1.0/team_rankings/', methods=['POST'])
def get_team_rankings():

    params = request.get_json()
    constraints = params['constraints']
    championship = param['championship']
    matchs = get_matchs(championship)
    validator = get_validator(constraints)
    
    # compute rankings
    rankings = utils.get_team_rankings(matchs, validator)

    return jsonify({'rankings' : rankings })


@app.route('/api/v1.0/scorer_rankings/', methods=['POST'])
def get_scorer_rankings():

    params = request.get_json()
    constraints = params['constraints']
    championship = param['championship']
    matchs = get_matchs(championship)
    validator = get_validator(constraints)
    
    # compute rankings
    rankings = utils.get_scorer_rankings(matchs, validator)

    return jsonify({'rankings' : rankings })


@app.route('/api/v1.0/assister_rankings/', methods=['POST'])
def get_assister_rankings():

    params = request.get_json()
    constraints = params['constraints']
    championship = param['championship']
    matchs = get_matchs(championship)
    validator = get_validator(constraints)
    
    # compute rankings
    rankings = utils.get_assister_rankings(matchs, validator)

    return jsonify({'rankings' : rankings })


@app.route('/api/v1.0/clean_sheet_rankings/', methods=['POST'])
def get_clean_sheet_rankings():

    params = request.get_json()
    constraints = params['constraints']
    championship = param['championship']
    matchs = get_matchs(championship)
    validator = get_validator(constraints)
    
    # compute rankings
    rankings = utils.get_clean_sheet_rankings(matchs, validator)

    return jsonify({'rankings' : rankings })


@app.route('/api/v1.0/rankings_evolution/', methods=['POST'])
def get_rankings_evolution():

    params = request.get_json()
    team = params['team']
    championship = param['championship']
    matchs = get_matchs(championship)
    
    evolution = utils.get_ranking_evolution(matchs, team)

    return jsonify({'evolution' : evolution })


@app.route('/api/v1.0/teams/', methods=['GET'])
def get_teams():

    params = request.get_json()
    championship = param['championship']
    matchs = get_matchs(championship)
    
    teams = utils.get_teams(matchs)

    return jsonify({'teams' : teams})



if __name__ == '__main__':
    app.run(debug=True)
