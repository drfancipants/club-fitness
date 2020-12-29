from stravatools.scraper import StravaScraper
import json
import pdb
import requests
from bs4 import BeautifulSoup
import pandas as pd

VERSION = '0.1.0'

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
USER_AGENT = "stravalib-scraper/%s" % VERSION

HEADERS = {'User-Agent': USER_AGENT}

BASE_URL = "https://www.strava.com"

URL_LOGIN = "%s/login" % BASE_URL
URL_SESSION = "%s/session" % BASE_URL
URL_DASHBOARD = "%s/dashboard" % BASE_URL
URL_CLUB = "%s/clubs/781964/feed?feed_type=club" % BASE_URL

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

def convert_to_seconds(s):
    return int(s[:-1]) * seconds_per_unit[s[-1]]

def get_page(session, url):
    response = session.get(url, headers=HEADERS)
    response.raise_for_status()
    return response

def parse_elapsed_time(to_parse):
    return sum([convert_to_seconds(x) for x in to_parse.text.split()])

def load_json_file(filename):
    with open(filename) as json_file:
        json_data = json.load(json_file)

    return json_data

def session_authenticate(session, credentials, url):    
    response = get_page(session, url)

    soup = BeautifulSoup(response.content, 'html.parser')

    utf8 = soup.find_all('input',
                         {'name': 'utf8'})[0].get('value').encode('utf-8')
    token = soup.find_all('input',
                          {'name': 'authenticity_token'})[0].get('value')
    data = {
        'utf8': utf8,
        'authenticity_token': token,
        'plan': "",
        'email': credentials['email'],
        'password': credentials['password'],
    }

    response = session.post(URL_SESSION,
                            data=data,
                            headers=HEADERS)
    
    response.raise_for_status()

    return True

def scrape_single_activities(soup, start_index, activities, latest):
    cActs = start_index
    latestRecord = latest
    
    acts = soup.find_all('div', {"class": "activity"})

    if (not acts):
        print('Break')
        return [activities, cActs, latestRecord]

    for act in acts:
        activities.loc[cActs, 'id'] = int(act['id'].split('-')[1])
        activities.loc[cActs, 'start_date_local'] = act.time['datetime']
        activities.loc[cActs, 'data-updated-at'] = act['data-updated-at']
        activities.loc[cActs, 'elapsed_time'] = parse_elapsed_time(act.find('li', {'title': 'Time'}))

        try:
            activities.loc[cActs, 'distance'] = float(act.find('li', {'title': 'Distance'}).text.split()[0])
        except:
            activities.loc[cActs, 'distance'] = float(0)
            
        activities.loc[cActs, 'name'] = act.find('strong').text.strip()
        activities.loc[cActs, 'athlete'] = act.find('a', {'class': 'entry-athlete'}).text.strip().split('\n')[0]

        lat = int(act['data-updated-at'])

        if lat < latestRecord:
            latestRecord = lat
            
        cActs = cActs + 1

    return [activities, cActs, latestRecord]

def scrape_group_activities(soup, start_index, activities, latest):
    cActs = start_index
    latestRecord = latest
    
    acts = soup.find_all('div', {"class": "group-activity"})
    
    if (not acts):
        print('Break')
        return [activities, cActs, latestRecord]

    for act in acts:
        entries = act.find_all('li', {"class": "entity-details"})

        for entry in entries:
            activities.loc[cActs, 'id'] = int(entry['id'].split('-')[1])
            activities.loc[cActs, 'start_date_local'] = act.time['datetime']
            activities.loc[cActs, 'data-updated-at'] = act['data-updated-at']
            activities.loc[cActs, 'elapsed_time'] = parse_elapsed_time(entry.find('li', {'title': 'Time'}))

            try:
                activities.loc[cActs, 'distance'] = float(entry.find('li', {'title': 'Distance'}).text.split()[0])
            except:
                activities.loc[cActs, 'distance'] = float(0)
            
            activities.loc[cActs, 'name'] = entry.find('strong').text.strip()
            activities.loc[cActs, 'athlete'] = entry.find('a', {'class': 'entry-athlete'}).text.strip().split('\n')[0]

            cActs = cActs + 1
            
        lat = int(act['data-updated-at'])

        if lat < latestRecord:
            latestRecord = lat

    return [activities, cActs, latestRecord]

if __name__ == "__main__":
    # load credential data
    credentials = load_json_file('.secret/api_credentials.json')

    # create session and authenticate
    session = requests.Session()
    session.cookies.clear()

    is_authed = session_authenticate(session, credentials, URL_LOGIN)
    
    ## Create the dataframe ready for the API call to store your activity data
    activities = pd.DataFrame(
        columns = [
            "id",
            "athlete",
            "data-updated-at",
            "elapsed_time",
            "distance",
            "name",
        ]
    )

    # Get initial response
    cActs = 0
    feedUrl = URL_CLUB
    latestRecord = 9999999999 
    lastcActs = 0
    
    while True:
        response = get_page(session, feedUrl)
        soup = BeautifulSoup(response.content, 'lxml')

        # Scrape individual feed activites
        [activities, cActs, latestRecord] = scrape_single_activities(soup, cActs, activities, latestRecord)
        
        # Scrape group feed activities
        [activities, cActs, latestRecord] = scrape_group_activities(soup, cActs, activities, latestRecord)
        
        if(cActs == lastcActs):
            break
        else:
            lastcActs = cActs
            print(latestRecord)
            
        feedUrl = URL_CLUB + '&before=' + str(latestRecord) + '&cursor=' + str(latestRecord)
    
    print(activities)
    activities.to_csv('strava_activities.csv')

    
