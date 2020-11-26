#! /usr/bin/env python3
# coding: utf-8

def get_winner_between(goals, from_min, to_min):
    
    """"Compute the winner of an interval of 
        the match between two minutes

        :param goals: list of dict with goal data
        :param from_min: first minute of the interval
        :param to_min: last minute of the interval
        :return: string representing the winner"""

    teams_goals = {'home': 0, 'away': 0}
    for goal in goals:
        if goal['min'] >= from_min and goal['min'] <= to_min:
            teams_goals[goal['team']] += 1

    winner = ''
    if teams_goals['home'] > teams_goals['away']:
        winner = 'home'
    
    elif teams_goals['away'] > teams_goals['home']:
        winner = 'away'

    else:
        winner = 'draw'

    return winner


def get_points_between(matchs, from_min, to_min):

    """"Compute the points that the teams in the
        matchs dicts have taken between two minutes

        :param matchs: list of dict with matchs data
        :param from_min: first minute of the interval
        :param to_min: last minute of the interval
        :return: list of dicts with points for each team"""

    teams = [team for match in matchs for team in match['teams'].values()]
    teams = list(set(teams))
    points_by_team = [{'team': team, 'points': 0} for team in teams]

    for match in matchs:
        winner = get_winner_between(match['goals'], from_min, to_min)
        if winner == 'draw':
            i_home_team = next((i for (i, t) in enumerate(points_by_team) 
                                if t["team"] == match['teams']['home']), None)
            i_away_team = next((i for (i, t) in enumerate(points_by_team) 
                                if t["team"] == match['teams']['away']), None)
            points_by_team[i_home_team]['points'] += 1
            points_by_team[i_away_team]['points'] += 1

        else:
            i_team = next((i for (i, t) in enumerate(points_by_team) 
                           if t["team"] == match['teams'][winner]), None)
            points_by_team[i_team]['points'] += 3

    return points_by_team


def get_ranking(points):

    """From a dict with the points for each 
       teams, compute the ranking

       :param points: a dict with the point for each team
       :return: a list with the ranking"""

    ranking = sorted(points, key=lambda t: t['points'], reverse=True)

    return ranking 

    


        
