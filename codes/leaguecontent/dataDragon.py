import os, mal, dotenv, pprint, requests, json
from dotenv import load_dotenv
from riotwatcher import LolWatcher, ApiError

load_dotenv()
RIOT_KEY = os.getenv('RIOT_KEY')
watcher = LolWatcher(RIOT_KEY)
my_region = 'BR1'
lang_code = 'pt_BR'

#TODO Transformar este arquivo todo em uma classe, que será instanciada na Cog LeagueOfLegends.py

def get_current_version():
    response = requests.get('https://ddragon.leagueoflegends.com/api/versions.json')
    league_versions = response.json()
    return league_versions[0]

def get_profile_icon(iconID: int):
    latest = get_current_version()
    return f'http://ddragon.leagueoflegends.com/cdn/{latest}/img/profileicon/{iconID}.png'

def get_champion_name(championID: int):
    champion_name = ''
    for item in all_champions['data']:
        row = all_champions['data'][item]
        if row['key'] == str(championID):
            champion_name = row['name']
    
    return champion_name

latest = get_current_version()

all_champions_url = f'http://ddragon.leagueoflegends.com/cdn/{latest}/data/{lang_code}/champion.json'
all_response = requests.get(all_champions_url)
all_champions = all_response.json()