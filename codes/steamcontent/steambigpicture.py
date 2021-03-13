import os, dotenv, requests, json, pprint, random
from dotenv import load_dotenv
from pprint import pprint
import steam

import codes.settings as st


load_dotenv()
my_steam_id = '76561198058563121'
steam_key = os.getenv('STEAM_KEY')
class SteamBigPicture:
    #EMOJIS
    EMOJI_METACRITIC = '<:metacritic_logo:819722763492261898>'
    
    
    def __init__(self):
        self.get_all_games()
        
    def get_all_games(self, source = 'steam'):
        '''Read data from 'steam_data.txt'
        
        source - 'steam' or 'steamspy'
        '''
        if source == 'steam':
            with open(st.steam_data_path + 'steam_data.txt', 'r') as json_file:
                data = json.load(json_file)
            return data
        elif source == 'steamspy':
            with open(st.steam_data_path + 'steam_spy_data.txt', 'r') as json_file:
                data = json.load(json_file)
            return data
    
    def request_all_games(self, source = 'steam'):
        '''Requests new data from Steam/SteamSpy and update the '.txt' file
        
        source - 'steam' or 'steamspy'
        '''
        if source == 'steam':
            response_all_steam_apps = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
            all_steam_apps = response_all_steam_apps.json()
            
            with open(st.steam_data_path + 'steam_data.txt', 'w') as outfile:
                json.dump(all_steam_apps, outfile)
        elif source == 'steamspy':
            all_steamspy_apps = {}
            
            #Page 0 to 9 - 10000 itens mais comprados da Steam, segundo o SteamSpy
            for i in range(10):
                payload = {'request': 'all', 'page':i}
                response_all_steamspy_apps = requests.get('https://steamspy.com/api.php', params=payload)
                if i == 0:
                    all_steamspy_apps = response_all_steamspy_apps.json()
                else:
                    all_steamspy_apps.update(response_all_steamspy_apps.json()) 
                
            with open(st.steam_data_path + 'steam_spy_data.txt', 'w') as outfile:
                json.dump(all_steamspy_apps, outfile)
            
    def get_game_info(self, game_title, source = 'steam'):
        '''Get game info
        
        game_title: str\n
        source: 'steam' or 'steamspy'
        '''
        if source == 'steam':
            all_games_json = self.get_all_games('steam')
            all_games_list = all_games_json['applist']['apps']
            
            game_info = next((item for item in all_games_list if item['name'] == game_title), None)
            app_id = game_info['appid']
            
            #Request to https://store.steampowered.com/api/appdetails/'
            payload = {'appids' : app_id, 'l':'brazilian'}
            response_game_info = requests.get('https://store.steampowered.com/api/appdetails/', params=payload)
            game_info = response_game_info.json()
            return game_info[str(app_id)]['data']
        
        elif source == 'steamspy':
            all_games_steamspy_json = self.get_all_games('steamspy')
            app_id_steamspy = next((item for item in all_games_steamspy_json if all_games_steamspy_json[item]['name'] == game_title), None)
            
            #Request to steamspy.com/api.php?
            payload = {'request':'appdetails', 'appid':app_id_steamspy}
            response_steamspy_game_info = requests.get('https://steamspy.com/api.php', params=payload)
            game_info_steamspy = response_steamspy_game_info.json()
            return game_info_steamspy
    
    #TODO Request All Free Games

# steam = SteamBigPicture()
# game = steam.get_game_info('Hollow Knight', 'steamspy')
# pprint(game)