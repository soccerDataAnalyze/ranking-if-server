#! /usr/bin/env python3
# coding: utf-8

import pytest

from modules.utils import *

# test get_winner()
goals_A = {
    'home': [
        {
            'min': 12,
            'scorer': 'player_A',
            'assister': 'player_B',
            'body_part': 'left',
            'situation': 'open play'   
        },
        {
            'min': 72,
            'scorer': 'player_A',
            'assister': 'player_C',
            'body_part': 'left',
            'situation': 'penalty'   
        }],
    'away': [
        {
            'min': 25,
            'scorer': 'player_D',
            'assister': 'player_E',
            'body_part': 'head',
            'situation': 'open play'   
        },
        {
            'min': 83,
            'scorer': 'player_D',
            'assister': 'player_E',
            'body_part': 'right',
            'situation': 'corner'   
        }]
}

goals_B = {
    'home': [
        {
            'min': 32,
            'scorer': 'player_F',
            'assister': 'player_B',
            'body_part': 'right',
            'situation': 'open play'   
        }],
    'away': [
        {
            'min': 38,
            'scorer': 'player_A',
            'assister': 'None',
            'body_part': 'left',
            'situation': 'open play'   
        }]
} 

validator_A = GoalValidator()
validator_A.add_constraint({'field': 'min', 'condition': '>', 'ref': 10})
validator_A.add_constraint({'field': 'min', 'condition': '<', 'ref': 70})
validator_A.add_constraint({'field': 'body_part', 'condition': '==', 'ref': 'left'})
validator_A.add_constraint({'field': 'situation', 'condition': '==', 'ref': 'open play'})

validator_B = GoalValidator()
validator_B.add_constraint({'field': 'min', 'condition': '>', 'ref': 19})
validator_B.add_constraint({'field': 'min', 'condition': '<', 'ref': 87})
validator_B.add_constraint({'field': 'body_part', 'condition': '==', 'ref': 'right'})

test_values = [(goals_A, validator_A, {'winner': 'home', 
                                       'score': {'home': 1, 'away': 0}}),
               (goals_A, validator_B, {'winner': 'away',
                                       'score': {'home': 0, 'away': 1}}), 
               (goals_B, validator_A, {'winner': 'away',
                                       'score': {'home': 0, 'away': 1}}),
               (goals_B, validator_B, {'winner': 'home', 
                                       'score': {'home': 1, 'away': 0}})]


@pytest.mark.parametrize('goals, validator, expected', test_values)
def test_get_winner(goals, validator, expected):
    assert get_winner(goals, validator) == expected


# test get_points_between()
match_A = {'teams': {'home': 'Team_1', 
                     'away': 'Team_2'}, 
           'goals': goals_A}

match_B = {'teams': {'home': 'Team_3', 
                     'away': 'Team_1'}, 
           'goals': goals_B}

matchs = [match_A, match_B]

test_values = [(matchs, validator_A, [{'team': 'Team_1', 'points': 6, 'victory': 2, 
                                       'draw': 0, 'defeat': 0, 'gf': 2, 'ga': 0}, 
                                      {'team': 'Team_2', 'points': 0, 'victory': 0,
                                       'draw': 0, 'defeat': 1, 'gf': 0, 'ga': 1}, 
                                      {'team': 'Team_3', 'points': 0, 'victory': 0,
                                       'draw': 0, 'defeat': 1, 'gf': 0, 'ga': 1}]),
               (matchs, validator_B, [{'team': 'Team_1', 'points': 0, 'victory': 0, 
                                       'draw': 0, 'defeat': 2, 'gf': 0, 'ga': 2}, 
                                      {'team': 'Team_2', 'points': 3, 'victory': 1, 
                                       'draw': 0, 'defeat': 0, 'gf': 1, 'ga': 0}, 
                                      {'team': 'Team_3', 'points': 3, 'victory': 1,
                                       'draw': 0, 'defeat': 0, 'gf': 1, 'ga': 0}])]

@pytest.mark.parametrize('matchs, validator, expected', test_values)
def test_get_points(matchs, validator, expected):
    output = get_points(matchs, validator)
    sorted_output = sorted(output, key=lambda t: t['team'], reverse=True)
    sorted_expected = sorted(expected, key=lambda t: t['team'], reverse=True)

    assert sorted_output == sorted_expected


# test get_ranking()
test_values = [([{'team': 'Team_1', 'points': 4, 'goals': 1}, 
                 {'team': 'Team_2', 'points': 4, 'goals': 3}, 
                 {'team': 'Team_3', 'points': 0, 'goals': 10}],
                ['points', 'goals'],
                [{'team': 'Team_2', 'points': 4, 'goals': 3}, 
                 {'team': 'Team_1', 'points': 4, 'goals': 1}, 
                 {'team': 'Team_3', 'points': 0, 'goals': 10}]),
               ([{'player': 'player_A', 'goals': 3},
                 {'player': 'player_B', 'goals': 5},
                 {'player': 'player_C', 'goals': 7}],
                ['goals'],
                [{'player': 'player_C', 'goals': 7},
                 {'player': 'player_B', 'goals': 5},
                 {'player': 'player_A', 'goals': 3}])]

@pytest.mark.parametrize('data, keys, expected', test_values)
def test_get_ranking(data, keys, expected):
    assert get_ranking(data, keys) == expected


# test get_goals_by_players()
test_values = [(matchs, validator_A, [{'player': 'player_A', 'goals': 2}]),
               (matchs, validator_B, [{'player': 'player_D', 'goals': 1}, 
                                      {'player': 'player_F', 'goals': 1}])]

@pytest.mark.parametrize('matchs, validator, expected', test_values)
def test_get_goals_by_player(matchs, validator, expected):
    output = get_goals_by_player(matchs, validator)
    sorted_output = sorted(output, key=lambda t: t['player'], reverse=True)
    sorted_expected = sorted(expected, key=lambda t: t['player'], reverse=True)

    assert sorted_output == sorted_expected


# test get_assists_by_players()
test_values = [(matchs, validator_A, [{'player': 'player_B', 'assists': 1}]),
               (matchs, validator_B, [{'player': 'player_B', 'assists': 1}, 
                                      {'player': 'player_E', 'assists': 1}])]

@pytest.mark.parametrize('matchs, validator, expected', test_values)
def test_get_assists_by_player(matchs, validator, expected):
    output = get_assists_by_player(matchs, validator)
    sorted_output = sorted(output, key=lambda t: t['player'], reverse=True)
    sorted_expected = sorted(expected, key=lambda t: t['player'], reverse=True)

    assert sorted_output == sorted_expected