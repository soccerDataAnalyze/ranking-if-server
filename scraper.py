import os
import re
import yaml
import time
import json

import pymongo
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_match_ids_by_url(url, driver, wait_time):

    """Recuperate the ids of the matchs in the page
        :param url: url of the page
        :param driver: chromedriver object
        :param wait_time: time to wait for some event (js loading, ...)
        :return: tupple with a list of the ids and the title of the page"""

    driver.get(url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "sportName")))
    title = driver.title
    word = re.search(r'\b(Results)\b', title)
    title = title[0:word.start()]

    # click on more button until all the matchs are displayed
    while True:
        more_link = driver.find_elements_by_class_name("event__more--static")
        if more_link == []:
            break
        driver.execute_script("arguments[0].click();", more_link[0])
        time.sleep(wait_time)

    # recuperate match_ids
    match_ids = [match.get_attribute("id")[4:] for
                 match in driver.find_elements_by_class_name(
                    "event__match--static")]

    return (match_ids, title)


def get_goals_by_match_id(match_id, driver):

    """Recuperate the stats of a match by his id
        :param match_id: the id of the match
        :param driver: chromedriver object
        :return: a list with a dict for each match that contains
                 the goals"""


    match_path = "{}/#match-summary".format(match_id)
    match_path = "https://www.flashscore.com/match/{}".format(match_path)
    driver.get(match_path)

    match = {'teams': {}, 'goals':[]}
    home_team = ''
    away_team = ''

    while home_team == '' or away_team == '':
        teams_elem = WebDriverWait(driver, 60).until(EC.presence_of_element_located(
                        (By.CLASS_NAME, "team-primary-content")))
        home_elem = teams_elem.find_element_by_class_name("home-box")
        home_team = home_elem.find_element_by_class_name("team-text").text
        away_elem = teams_elem.find_element_by_class_name("away-box")
        away_team = away_elem.find_element_by_class_name("team-text").text

    match['teams']['home'] = home_team
    match['teams']['away'] = away_team

    content = WebDriverWait(driver, 60).until(EC.presence_of_element_located(
                (By.ID, "summary-content")))
    
    for team in ['home', 'away']:
        event_elems = content.find_elements_by_class_name('incidentRow--{}'.format(team))
        
        for e in event_elems:
            goal_elem = e.find_elements_by_class_name('soccer-ball')
            if goal_elem != []:

                goal_min_elem = e.find_elements_by_class_name('time-box')
                if goal_min_elem != []:
                    goal_min = ''
                    while goal_min == '':
                        goal_min = goal_min_elem[0].text
                    end = goal_min.find("'")
                    goal_min = int(goal_min[:end])

                goal_min_elem = e.find_elements_by_class_name('time-box-wide')
                if goal_min_elem != []:
                    goal_min = ''
                    while goal_min == '':
                        goal_min = goal_min_elem[0].text
                    end = goal_min.find('+')
                    goal_min = int(goal_min[:end])
                
                goal = {'team': team, 'min': goal_min}
                match['goals'].append(goal)
    
    return match


def main():

    # database client
    CONNECTION_STRING = "mongodb+srv://amaury:ObNw8j6guIlWAeuG@cluster0.ffeme.mongodb.net/rankinator?retryWrites=true&w=majority"
    client = pymongo.MongoClient(CONNECTION_STRING)
    db = client.rankinator
    col = db.matchs

    # manage chrome driver options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"),
                              options=chrome_options)

    with open('params.yml') as f_params:
        data = yaml.load(f_params, Loader=yaml.FullLoader)
        urls = data['urls']

    for url in urls:
        match_ids, title = get_match_ids_by_url(url, driver, 15)

    for i, match_id in enumerate(match_ids):
        match = get_goals_by_match_id(match_id, driver)
        col.insert_one(match)



if __name__ == '__main__':
    main()