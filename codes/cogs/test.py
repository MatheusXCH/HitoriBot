import os, mal, dotenv
from dotenv import load_dotenv
from jikanpy import Jikan

from google_trans_new import google_translator
from howlongtobeatpy import HowLongToBeat

import random, pandas, pprint
from pprint import pprint
from riotwatcher import LolWatcher, ApiError

import json
import requests
import codes.settings as st

from roleidentification import *


url = "https://steamspy.com/api.php"
parameters = {"request":"all"}

json_data = requests.get(url, params=parameters)
json_data = json_data.json()
pprint(json_data)

with open(st.steam_data_path + 'steam_spy_data.txt', 'w') as outfile:
            json.dump(json_data, outfile)

# # response = requests.get('https://ddragon.leagueoflegends.com/api/versions.json')
# # league_versions = response.json()
# # pprint(league_versions[0])


#GAME_INFO - Retorna informações sobre o game passado ao parâmetro "?appids=<game_id>"
#<game_id> pode ser uma lista

# def load_all_games():
#     with open('steam_data.txt', 'r') as json_file:
#         data = json.load(json_file)
    
#     return data

# def get_game_info(game_title, keys = None):
#     '''Get game info
#     game_title <str>
#     keys = parameter to pass in filters. It is not a list, but a string with simple comma (,) as filters separators. DO NOT PUT SPACES on <keys>
#     '''
#     all_games_json = load_all_games()
#     all_games_list = all_games_json['applist']['apps']
    
#     game_info = next((item for item in all_games_list if item['name'] == game_title), None)
#     app_id = game_info['appid']
    
#     #Request to https://store.steampowered.com/api/appdetails/'
#     payload = {'appids' : app_id, 'filters' : keys}
#     response_game_info = requests.get('https://store.steampowered.com/api/appdetails/', params=payload)
#     game_info = response_game_info.json()
#     return game_info[str(app_id)]
#     # pprint(response_game_info.url)
#     # pprint(game_info)

# #APP_LIST = Request que retorna todos os itens disponíveis na Steam
# def get_all_games():
#     response_all_steam_apps = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
#     all_steam_apps = response_all_steam_apps.json()
#     # pprint(all_steam_apps)
#     with open('steam_data.txt', 'w') as outfile:
#         json.dump(all_steam_apps, outfile)

# game = input('Qual jogo? --> ')
# keys = input('Filtros? --> ')

# #keys = 'price_overview,platforms'
# game_data = get_game_info(game)
# print(f'\n\n Informações solicitadas sobre {game}:\n')
# pprint(game_data)