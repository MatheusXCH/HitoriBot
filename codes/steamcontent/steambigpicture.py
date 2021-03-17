import os, dotenv, requests, json, pprint, random, time
from dotenv import load_dotenv
from pprint import pprint
import steam

import codes.settings as st


# TODO Melhorar ainda mais a busca ao converter todos os nomes de jogos (Input, Output e Arquivos Salvos) para UPPERCASE
class SteamBigPicture:
    """Handles GET requests to Steamworks Web API, Steam StorefrontAPI and SteamSpy API to return info about Games or DLCs in JSON format
    
    Some usefull links:
    - 'Steamworks Web API' Documentation: https://partner.steamgames.com/doc/webapi
    - 'SteamSpy API' Documentation: https://steamspy.com/api.php
    - 'StorefrontAPI' Documentation: https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI    
    """
    #EMOJIS
    EMOJI_METACRITIC = '<:metacritic_logo:819722763492261898>'


    def __init__(self):
        pass


    def get_all_games(self, source: str):
        """Read local data from 'steam_spy_data.txt' or 'steam_data.txt'

        Parameters
        ----------
        - source : str \\
        ['steam' to search Steam database, 'steamspy' to search SteamSpy database]

        Returns
        -------
        - data : JSON \\
            [Return the JSON data read from 'steam_spy_data.txt' or 'steam_data.txt'] \\
            [Returns an empty JSON if missing < source > parameter]
        """

        if source == 'steamspy':
            with open(st.steam_data_path + 'steam_spy_data.txt', 'r') as json_file:
                data = json.load(json_file)
            return data
        elif source == 'steam':
            with open(st.steam_data_path + 'steam_data.txt', 'r') as json_file:
                data = json.load(json_file)
            return data
        else:
            return {}


    def request_all_games(self):
        """Requests new data from SteamSpy/Steam and writes then in the correspondent '.txt' file"""

        # # # STEAMSPY:
        i = 0
        all_steamspy_apps = {}

        # Iterates through SteamSpy pages until hit the last one plus 1, wich triggers the 'except ValueError' and break the loop
        while(True):
            try:
                payload = {'request': 'all', 'page':i}
                response_steamspy_app = requests.get('https://steamspy.com/api.php', params=payload)
                all_steamspy_apps.update(response_steamspy_app.json())

            except ValueError:  # ValueError includes 'simplejson.decoder.JSONDecodeError'
                break

        with open(st.steam_data_path + 'steam_spy_data.txt', 'w') as outfile:
            json.dump(all_steamspy_apps, outfile)

        # # STEAM:
        all_steam_apps = {}
        response_all_steam_apps = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
        all_steam_apps.update(response_all_steam_apps.json())

        with open(st.steam_data_path + 'steam_data.txt', 'w') as outfile:
            json.dump(all_steam_apps['applist']['apps'], outfile)


    def __search_game(self, game_title: str, source: str):
        """Implements the 'Precise' and 'Imprecise' search

        - Precise Search = Returns the exactly key that matches < game_title >
        - Imprecise Search = Returns all the keys that contains the substring < game_title >
        
        The search handles < game_title >, as well as the game database titles, in uppercase. This makes 
        it possible for the user to do a successfull search by even writting "Dota 2", "DOTA 2", "dota 2",
        and so go on.

        Parameters
        ----------
        - game_title : str \\
        [Title of the game to search for]
        - source : str \\
        ['steam' to search Steam database, 'steamspy' to search SteamSpy database]

        Returns
        -------
        - search : list \\
        [List of games appids found by 'Precise' or 'Imprecise' search on the select database]\\ 
        [Empty list if nothing found or missing <source> attribute]
        """
        # Get games from selected source
        all_games_json = self.get_all_games(source)
        game_title = game_title.upper() # Uppercase to make a broader search
        
        if source == 'steamspy':
            # # # STEAMSPY:
            # # PRECISE SEARCH
            # Case <game_title> matches a game name on the database
            search = [item for item in all_games_json if all_games_json[item]['name'].upper() == game_title]

            if search != []:
                print("Não funcionou!")
                return search
            else:
                # # IMPRECISE SEARCH
                # Case there isn't a game name equal to <game_title>, search for all items that contais <game_title> as a substring
                search = [item for item in all_games_json if game_title in all_games_json[item]['name'].upper()]
                return search

        elif source == 'steam':
            # # # STEAM:
            # # PRECISE SEARCH
            # Case <game_title> matches a game name on the database
            search = [item['appid'] for item in all_games_json if item['name'].upper() == game_title]
            if search != []:            
                return search
            else:
                # # IMPRECISE SEARCH
                # Case there isn't a game name equal to <game_title>, search for all items that contais <game_title> as a substring
                search = [item['appid'] for item in all_games_json if game_title in item['name'].upper()]
                return search

        # If 'source' missing
        else:
            return []

    def get_steam_game(self, game_title: str, max_items = 5):
        """Get detailed information about games \\
        If a correpondent key value is passed as <game_title>, returns info about this game. Otherwise, requests information
        of a list of games that the key matches the substring <game_title>

        Parameters
        ----------
        - game_title : str \\
        [Title of the game to search for]
        - max_items : int \\
        [Max number of games to return in the list. By default: 5]

        Returns
        -------
        - steam_game_info_list : list \\
        [List of JSON, where each one contains info about the games found on the search] \\
        [Empty list if nothing found on search]
        """

        # First, search for the game on SteamSpy database (more accurate, but with less amount of items)
        search = self.__search_game(game_title, 'steamspy')
        
        # If there's no matching item on SteamSpy after 'Precise' and 'Imprecise' search, 
        # try to search for it directly on Steam database (lesse accurate, but with higher amount of items)
        if search == []:
            search = self.__search_game(game_title, 'steam')

            # If still no matching item, then the search result is 'None'
            if search == []:
                return search

        # Limit the searched items to only 'max_items' or less values (for best performance)
        if len(search) < max_items: 
            max_range = len(search)
        else: 
            max_range = max_items

        steam_game_info_list = []
        # GET request for each of the items founded
        for item in range(max_range):
            #Request to 'https://store.steampowered.com/api/appdetails/'
            payload = {'appids':search[item], 'l':'brazilian', 'cc':'br'}
            response_steam_game_info = requests.get('https://store.steampowered.com/api/appdetails/', params=payload)
            steam_game_info_json = response_steam_game_info.json()

            # If there's an error on the data obtained via GET, ignore and continue to next iterate
            try:
                if steam_game_info_json[str(search[item])]['success'] == True:
                    steam_game_info = steam_game_info_json[str(search[item])]['data']
            except:
                continue
            steam_game_info_list.append(steam_game_info)

        return steam_game_info_list  # Returns the list of founded items, ordered by 'Owners' in case those were obtained on SteamSpy database

    def get_steam_package(self, app_id_list: list):
        
        steam_packages_list = []
        for item in app_id_list:
            payload = {'packageids': item, 'l':'brazilian', 'cc':'br'}
            response_steam_package = requests.get('http://store.steampowered.com/api/packagedetails/', params=payload)
            steam_package_json = response_steam_package.json()

            if steam_package_json[str(item)]['success'] == True:
                steam_package = steam_package_json[str(item)]['data']
                steam_packages_list.append(steam_package)

        return steam_packages_list


    def steamspy_complementary_info(self, app_id: int):
        """Get complementary game info from SteamSpy database, such as 'Owners' and 'Tags'

        Parameters
        ----------
        - app_id : int \\
        [Steam ID of the game to search for]

        Returns
        -------
        - steamspy_game_info : JSON \\
        [Game info found on SteamSpy database as JSON] \\
        [Empty JSON if nothing found on search]
        """

        #Request to 'steamspy.com/api.php?'

        payload = {'request':'appdetails', 'appid':app_id}
        response_steamspy_game_info = requests.get('https://steamspy.com/api.php', params=payload)
        steamspy_game_info = response_steamspy_game_info.json()
        
        # When you request an invalid 'appid' to SteamSpy, the default response are information about CS:GO
        # Handle this scenario to turns it into an empty JSON is required
        if app_id != steamspy_game_info['appid']:
            return {}
        else:
            return steamspy_game_info


# steam = SteamBigPicture()
# print('Iniciando...')
# steam.request_all_games()
# print('Finalizado!')

# steam = SteamBigPicture()
# game_title = input('Game: ')
# steam_games = steam.get_steam_game(game_title)
# steamspy_games_info = [steam.steamspy_complementary_info(app['steam_appid']) for app in steam_games]
# pprint(steamspy_games_info)

# packages = [steam.get_steam_package(app['packages']) for app in steam_games]
# pprint(packages)
# package = steam.get_steam_package(steam_game[0]['packages'])
# print(type(package))
# pprint(package)