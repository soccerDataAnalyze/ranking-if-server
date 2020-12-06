#! /usr/bin/env python3
# coding: utf-8


class GoalValidator:
    def __init__(self):
        self.constraints = []

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def validate(self, goal):
        valid = True
        
        if goal['minute'] == " " or goal['minute'] == "":
            return False
        
        goal['minute'] = int(goal['minute'])
        for constraint in self.constraints:
            ref = None
            if type(constraint['ref']) == str:
                ref = "'{}'".format(constraint['ref'])
                
            else:
                ref = constraint['ref']

            field = None
            if type(goal[constraint['field']]) == str:
                field = "'{}'".format(goal[constraint['field']])
                
            else:
                field = goal[constraint['field']]
            
            eval_string = "{}{}{}".format(field,
                                          constraint['condition'],
                                          ref)

            if not eval(eval_string):
                valid = False
                break
        
        return valid
    

def get_winner(goals, validator):
    
    """"Compute the winner of an interval of 
        the match between two minutes

        :param goals: list of dict with goal data
        :param validator: validator object to validate goals
        :return: string representing the winner"""

    score = {'home': 0, 'away': 0}

    for team in score.keys():
        for goal in goals[team]:
            if validator.validate(goal):
                score[team] += 1

    winner = ''
    if score['home'] > score['away']:
        winner = 'home'
    
    elif score['away'] > score['home']:
        winner = 'away'

    else:
        winner = 'draw'

    result = {'winner': winner, 'score': score}
    
    return result


def get_points(matchs, validator):

    """"Compute the points and other data that the teams in the
        matchs dicts have taken under some constraints

        :param matchs: list of dict with matchs data
        :param validator: validator object to validate goals
        :return: list of dicts with points for each team"""

    teams = [team for match in matchs for team in match['teams'].values()]
    teams = list(set(teams))
    points_by_team = [{'team': team, 'points': 0, 'victory': 0, 
                       'draw': 0, 'defeat': 0, 'gf': 0, 'ga': 0} for team in teams]

    for match in matchs:
        result = get_winner(match['goals'], validator)
        winner = result['winner']
        score = result['score']

        i_home_team = next((i for (i, t) in enumerate(points_by_team) 
                            if t["team"] == match['teams']['home']), None)
        i_away_team = next((i for (i, t) in enumerate(points_by_team) 
                            if t["team"] == match['teams']['away']), None)

        points_by_team[i_home_team]['gf'] += score['home']
        points_by_team[i_home_team]['ga'] += score['away']
        points_by_team[i_away_team]['gf'] += score['away']
        points_by_team[i_away_team]['ga'] += score['home']

        if winner == 'draw':
            points_by_team[i_home_team]['points'] += 1
            points_by_team[i_home_team]['draw'] += 1
            points_by_team[i_away_team]['points'] += 1
            points_by_team[i_away_team]['draw'] += 1

        elif winner == 'home':
            points_by_team[i_home_team]['points'] += 3
            points_by_team[i_home_team]['victory'] += 1
            points_by_team[i_away_team]['defeat'] += 1

        elif winner == 'away':
            points_by_team[i_away_team]['points'] += 3
            points_by_team[i_away_team]['victory'] += 1
            points_by_team[i_home_team]['defeat'] += 1

    return points_by_team


def get_ranking(data, keys):

    """From a dict with the data compute the ranking

       :param data: a dict with the data to rank
       :param keys: keys in order of importance to rank
       :return: a list with the ranking"""

    
    ranking = sorted(data, key=lambda t: [t[k] for k in keys], reverse=True)

    return ranking


def get_goals_by_player(matchs, validator):

    """"Compute the winner of an interval of 
        the match between two minutes

        :param matchs: list of dict with matchs data
        :param validator: validator object to validate goals
        :return: dict with number of goals for each player"""

    tmp = {}
    for match in matchs:
        for team in ['home', 'away']:
            for goal in match['goals'][team]:
                if validator.validate(goal):
                    if goal['scorer'] not in tmp.keys():
                        tmp[goal['scorer']] = 1
                    else:
                        tmp[goal['scorer']] += 1
    
    goals_by_player = []

    for player, goals in tmp.items():
        goals_by_player.append({'player': player, 
                                'goals': goals})

    return goals_by_player



def get_assists_by_player(matchs, validator):

    """"Compute the winner of an interval of 
        the match between two minutes

        :param matchs: list of dict with matchs data
        :param validator: validator object to validate goals
        :return: dict with number of goals for each player"""

    tmp = {}
    for match in matchs:
        for team in ['home', 'away']:
            for goal in match['goals'][team]:
                if validator.validate(goal) and goal['assister'] != 'None':
                    if goal['assister'] not in tmp.keys():
                        tmp[goal['assister']] = 1
                    else:
                        tmp[goal['assister']] += 1
    
    assists_by_player = []

    for player, assists in tmp.items():
        assists_by_player.append({'player': player, 
                                  'assists': assists})

    return assists_by_player


def get_clean_sheets(matchs, validator):

    """Compute the number of clean sheets for 
       each teams

    :param matchs: list of dict with matchs data
    :param validator: validator object to validate goals
    :return: dict with number of clean sheets for each team"""

    teams = [team for match in matchs for team in match['teams'].values()]
    teams = list(set(teams))
    cs_by_team = [{'team': team, 'clean_sheets': 0} for team in teams]

    for match in matchs:

        i_home_team = next((i for (i, t) in enumerate(cs_by_team) 
                            if t["team"] == match['teams']['home']), None)
        i_away_team = next((i for (i, t) in enumerate(cs_by_team) 
                            if t["team"] == match['teams']['away']), None)

        if len(match['goals']['home']) == 0:
            cs_by_team[i_away_team]['clean_sheets'] += 1

        if len(match['goals']['away']) == 0:
            cs_by_team[i_home_team]['clean_sheets'] += 1

    return cs_by_team


def get_ranking_evolution(matchs, team):

    """Get the ranking evolution of a team

    :param matchs: list of dict with matchs data
    :param team: the name of the team
    :return: list with position for each minute"""

    ranking_evolution = []
    for to_min in range(5, 95, 5):
        validator = GoalValidator()
        validator.add_constraint({'field': 'minute', 
                                'condition': '>', 
                                'ref': 0})
        validator.add_constraint({'field': 'minute', 
                                'condition': '<', 
                                'ref': to_min})
        
        points = get_points(matchs, validator)
        ranking = get_ranking(points, ['points', 'gf'])

        pos = next((i for (i, d) in enumerate(ranking) if d["team"] == team), None)

        ranking_evolution.append(pos)

    return ranking_evolution
        





    


        
