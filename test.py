#! /usr/bin/env python3
# coding: utf-8

import pytest

from modules.utils import *

# test get_winner_between()
goals_A = [{'team': 'home', 'min': 12}, {'team': 'home', 'min': 23},
           {'team': 'home', 'min': 72}, {'team': 'away', 'min': 82}]

goals_B = [{'team': 'away', 'min': 17}, {'team': 'home', 'min': 53},
           {'team': 'home', 'min': 67}, {'team': 'away', 'min': 85}]

test_values = [(goals_A, 10, 89, 'home'), (goals_A, 80, 87, 'away'), 
               (goals_A, 70, 90, 'draw'), (goals_A, 84, 90, 'draw'),
               (goals_B, 10, 89, 'draw'), (goals_B, 80, 87, 'away'), 
               (goals_B, 70, 90, 'away'), (goals_B, 84, 90, 'away')]


@pytest.mark.parametrize('goals, from_min, to_min, expected', test_values)
def test_get_winner_between(goals, from_min, to_min, expected):
    assert get_winner_between(goals, from_min, to_min) == expected


# test get_points_between()
match_A = {'teams': {'home': 'Team_1', 
                     'away': 'Team_2'}, 
           'goals': goals_A}

match_B = {'teams': {'home': 'Team_3', 
                     'away': 'Team_1'}, 
           'goals': goals_B}

matchs = [match_A, match_B]

test_values = [(matchs, 10, 89, [{'team': 'Team_1', 'points': 4}, 
                                 {'team': 'Team_2', 'points': 0}, 
                                 {'team': 'Team_3', 'points': 1}]),
               (matchs, 80, 87, [{'team': 'Team_1', 'points': 3}, 
                                 {'team': 'Team_2', 'points': 3}, 
                                 {'team': 'Team_3', 'points': 0}]),
               (matchs, 70, 90, [{'team': 'Team_1', 'points': 4}, 
                                 {'team': 'Team_2', 'points': 1}, 
                                 {'team': 'Team_3', 'points': 0}]),
               (matchs, 84, 90, [{'team': 'Team_1', 'points': 4}, 
                                 {'team': 'Team_2', 'points': 1}, 
                                 {'team': 'Team_3', 'points': 0}])]

@pytest.mark.parametrize('matchs, from_min, to_min, expected', test_values)
def test_get_points_between(matchs, from_min, to_min, expected):
    output = get_points_between(matchs, from_min, to_min)
    sorted_output = sorted(output, key=lambda t: t['team'], reverse=True)
    sorted_expected = sorted(expected, key=lambda t: t['team'], reverse=True)

    assert sorted_output == sorted_expected


# test get_ranking()

test_values = [([{'team': 'Team_1', 'points': 4}, 
                 {'team': 'Team_2', 'points': 0}, 
                 {'team': 'Team_3', 'points': 1}], 
                [{'team': 'Team_1', 'points': 4}, 
                 {'team': 'Team_3', 'points': 1}, 
                 {'team': 'Team_2', 'points': 0}])]

@pytest.mark.parametrize('points, expected', test_values)
def test_get_ranking(points, expected):
    assert get_ranking(points) == expected