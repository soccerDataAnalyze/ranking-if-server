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


def get_ranking(data, keys):

    """From a dict with the data compute the ranking

       :param data: a dict with the data to rank
       :param keys: keys in order of importance to rank
       :return: a list with the ranking"""

    
    ranking = sorted(data, key=lambda t: [t[k] for k in keys], reverse=True)

    return ranking
    

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


def get_points(matchs, validator, loc_filter="all"):

    """"Compute the points and other data that the teams in the
        matchs dicts have taken under some constraints

        :param matchs: list of dict with matchs data
        :param validator: validator object to validate goals
        :param loc_filter: filter points from home, away or both match 
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

        if loc_filter == "all" or loc_filter == "home":
            points_by_team[i_home_team]['gf'] += score['home']
            points_by_team[i_away_team]['ga'] += score['home']

        if loc_filter == "all" or loc_filter == "away":        
            points_by_team[i_away_team]['gf'] += score['away']
            points_by_team[i_home_team]['ga'] += score['away']

        if winner == 'draw':
            if loc_filter == "all" or loc_filter == "home":
                points_by_team[i_home_team]['points'] += 1
                points_by_team[i_home_team]['draw'] += 1

            if loc_filter == "all" or loc_filter == "away":
                points_by_team[i_away_team]['points'] += 1
                points_by_team[i_away_team]['draw'] += 1

        elif winner == 'home':
            if loc_filter == "all" or loc_filter == "home":
                points_by_team[i_home_team]['points'] += 3
                points_by_team[i_home_team]['victory'] += 1

            if loc_filter == "all" or loc_filter == "away":
                points_by_team[i_away_team]['defeat'] += 1

        elif winner == 'away':
            if loc_filter == "all" or loc_filter == "away":
                points_by_team[i_away_team]['points'] += 3
                points_by_team[i_away_team]['victory'] += 1

            if loc_filter == "all" or loc_filter == "home":
                points_by_team[i_home_team]['defeat'] += 1

    return points_by_team


def get_team_rankings(matchs, validator):

    rankings = {'all': [], 'home': [], 'away': []}

    for ranking_type in ['all', 'home', 'away']:
        points = get_points(matchs, validator, ranking_type)
        ranking = get_ranking(points, ['points', 'gf'])
        rankings[ranking_type] = ranking

    return rankings


def get_goals_by_player(matchs, validator, loc_filter="all"):

    """"Compute the winner of an interval of 
        the match between two minutes

        :param matchs: list of dict with matchs data
        :param validator: validator object to validate goals
        :return: dict with number of goals for each player"""

    tmp = {}
    
    teams = []
    if loc_filter == 'all':
        teams = ['home', 'away']
    elif loc_filter == 'home':
        teams = ['home']
    elif loc_filter == 'away':
        teams = ['away']

    for match in matchs:
        for team in teams:
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


def get_scorer_rankings(matchs, validator):

    rankings = {'all': [], 'home': [], 'away': []}

    for ranking_type in ['all', 'home', 'away']:
        goals_by_player = get_goals_by_player(matchs, validator, ranking_type)
        ranking = get_ranking(goals_by_player, ['goals'])
        rankings[ranking_type] = ranking

    return rankings



def get_assists_by_player(matchs, validator, loc_filter="all"):

    """"Compute the winner of an interval of 
        the match between two minutes

        :param matchs: list of dict with matchs data
        :param validator: validator object to validate goals
        :return: dict with number of goals for each player"""

    tmp = {}

    teams = []
    if loc_filter == 'all':
        teams = ['home', 'away']
    elif loc_filter == 'home':
        teams = ['home']
    elif loc_filter == 'away':
        teams = ['away']

    for match in matchs:
        for team in teams:
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


def get_assister_rankings(matchs, validator):

    rankings = {'all': [], 'home': [], 'away': []}

    for ranking_type in ['all', 'home', 'away']:
        assists_by_player = get_assists_by_player(matchs, validator, ranking_type)
        ranking = get_ranking(assists_by_player, ['assists'])
        rankings[ranking_type] = ranking

    return rankings


def get_clean_sheets(matchs, validator, loc_filter="all"):

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

        if loc_filter == "all" or loc_filter == "home":
            if len(match['goals']['home']) == 0:
                cs_by_team[i_away_team]['clean_sheets'] += 1

        if loc_filter == "all" or loc_filter == "away":
            if len(match['goals']['away']) == 0:
                cs_by_team[i_home_team]['clean_sheets'] += 1

    return cs_by_team


def get_clean_sheet_rankings(matchs, validator):

    rankings = {'all': [], 'home': [], 'away': []}

    for ranking_type in ['all', 'home', 'away']:
        clean_sheets = get_clean_sheets(matchs, validator, ranking_type)
        ranking = get_ranking(clean_sheets, ['clean_sheets'])
        rankings[ranking_type] = ranking

    return rankings


def get_ranking_evolution(matchs, team):

    """Get the ranking evolution of a team

    :param matchs: list of dict with matchs data
    :param team: the name of the team
    :return: list with position for each minute"""

    ranking_evolution = {'all': [], 'home': [], 'away': []}
    for to_min in range(1, 91):
        validator = GoalValidator()
        validator.add_constraint({'field': 'minute', 
                                'condition': '>', 
                                'ref': 0})
        validator.add_constraint({'field': 'minute', 
                                'condition': '<', 
                                'ref': to_min})
        

        for ranking_type in ['all', 'home', 'away']:
            points = get_points(matchs, validator, ranking_type)
            ranking = get_ranking(points, ['points', 'gf'])
            pos = next((i for (i, d) in enumerate(ranking) if d["team"] == team), None)
            ranking_evolution[ranking_type].append(pos)

    return ranking_evolution


def get_teams(matchs):

    """Get the names of all the teams in a list
       of matchs.

    :param matchs: list of dict with matchs data
    :return: list with the teams names"""

    teams = [team for match in matchs for team in match['teams'].values()]
    teams = list(set(teams))

    return teams

        





    


        
