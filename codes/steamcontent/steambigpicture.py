import os, dotenv, requests, json, pprint, random, time
from dotenv import load_dotenv
from pprint import pprint
import steam

import codes.settings as st


class SteamBigPicture:
    """Handles GET requests to Steamworks Web API, Steam StorefrontAPI and SteamSpy API to return info about Games or DLCs in JSON format

    Some usefull links:
    - 'Steamworks Web API' Documentation: https://partner.steamgames.com/doc/webapi
    - 'SteamSpy API' Documentation: https://steamspy.com/api.php
    - 'StorefrontAPI' Documentation: https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI
    """

    # EMOJIS
    EMOJI_METACRITIC = "<:metacritic_logo:819722763492261898>"

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

        if source == "steamspy":
            with open(st.steam_data_path + "steam_spy_data.txt", "r") as json_file:
                data = json.load(json_file)
            return data
        elif source == "steam":
            with open(st.steam_data_path + "steam_data.txt", "r") as json_file:
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
        while True:
            try:
                payload = {"request": "all", "page": i}
                response_steamspy_app = requests.get("https://steamspy.com/api.php", params=payload)
                all_steamspy_apps.update(response_steamspy_app.json())

            # ValueError includes 'simplejson.decoder.JSONDecodeError'
            except ValueError:
                break

        with open(st.steam_data_path + "steam_spy_data.txt", "w") as outfile:
            json.dump(all_steamspy_apps, outfile)

        # # # STEAM:
        all_steam_apps = {}
        response_all_steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
        all_steam_apps.update(response_all_steam_apps.json())

        with open(st.steam_data_path + "steam_data.txt", "w") as outfile:
            json.dump(all_steam_apps["applist"]["apps"], outfile)

    def __search_game(self, game_title: str, max_items: int):
        """Implements the 'Precise' and 'Imprecise' search

        - Precise Search = Returns first the exactly key that matches < game_title >
        - Imprecise Search = Returns all the keys that contains the substring < game_title >
        
        The search handles < game_title >, as well as the game database titles, in uppercase. This makes 
        it possible for the user to do a successfull search by even writting "Dota 2", "DOTA 2", "dota 2",
        and so go on.
        
        The searching process start by founding the games on SteamSpy database, because by it's default ordered by 'Owners'.
        After finished this first step, if the search result has less elements than < max_items >, then search for other 
        possible matching items on Steam database directly.

        Parameters
        ----------
        - game_title : str \\
        [Title of the game to search for]
        - max_items : int \\
        [Maximum number of items to return in the result list]

        Returns
        -------
        - search : list \\
        [List of games appids found by 'Precise' or 'Imprecise' search on the select database]\\ 
        [Empty list if nothing is found]
        """

        # Get all games from sources
        spy_all_games_json = self.get_all_games("steamspy")
        steam_all_games_json = self.get_all_games("steam")

        # Uppercase to make a broader search
        game_title = game_title.upper()
        spy_search = []
        steam_search = []
        search = []

        # # # STEAMSPY:
        # # PRECISE SEARCH
        # Case <game_title> matches a game name on the SteamSpy database
        spy_psearch = [item for item in spy_all_games_json if spy_all_games_json[item]["name"].upper() == game_title]
        if spy_psearch == []:
            # # IMPRECISE SEARCH ONLY
            # Case there isn't a game name equal to <game_title>, search only for all items that contais <game_title> as a substring on SteamSpy
            spy_isearch = [
                item for item in spy_all_games_json if game_title in spy_all_games_json[item]["name"].upper()
            ]
        else:
            # # PRECISE + IMPRECISE SEARCH
            # Search for all items that contais <game_title> as a substring on SteamSpy
            spy_isearch = [
                item
                for item in spy_all_games_json
                if game_title in spy_all_games_json[item]["name"].upper()
                if item != spy_psearch[0]
            ]
        # Merge SteamSpy 'Precise' and 'Imprecise'
        spy_search = spy_psearch + spy_isearch

        if len(spy_search) > max_items:
            search = spy_search[:max_items]
            return search

        # # # STEAM:
        # # PRECISE SEARCH
        # Case <game_title> matches a game name on the Steam database
        else:
            if spy_psearch == []:
                # This is needed due the cases wich spy_psearch founds nothing
                spy_psearch = ["_Nothing_Founded_"]
            steam_psearch = [
                item["appid"]
                for item in steam_all_games_json
                if item["name"].upper() == game_title
                if str(item["appid"]) != spy_psearch[0]
            ]
            if steam_psearch == [] and spy_psearch == []:
                # # IMPRECISE SEARCH ONLY (if none of the precises searches has founded something)
                # Case there isn't a game name equal to <game_title>, search for all items that contais <game_title> as a substring on Steam
                steam_isearch = [item["appid"] for item in steam_all_games_json if game_title in item["name"].upper()]
            else:
                # # PRECISE + IMPRECISE SEARCH
                # Search for all items that contais <game_title> as a substring on Steam
                steam_isearch = [
                    item["appid"]
                    for item in steam_all_games_json
                    if game_title in item["name"].upper()
                    if str(item["appid"]) != spy_psearch[0]
                ]
            # Merge Steam 'Precise' and 'Imprecise'
            steam_search = steam_psearch + steam_isearch

        search = spy_search + steam_search

        if len(search) > max_items:
            search = search[:max_items]
            return search
        else:
            return search

    def get_steam_game(self, game_title: str, max_items=5):
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
        [Empty list if nothing is found on search]
        """

        # Call function to search for the game
        search = self.__search_game(game_title, max_items)

        # If no matching item, then the search result is an empty list
        if search == []:
            return search

        # Handles the case which the search length is less then the < max_items >
        if len(search) < max_items:
            max_range = len(search)
        else:
            max_range = max_items

        steam_game_info_list = []
        # GET request for each of the items founded
        for item in range(max_range):
            # Request to 'https://store.steampowered.com/api/appdetails/'
            payload = {"appids": search[item], "l": "brazilian", "cc": "br"}
            response_steam_game_info = requests.get("https://store.steampowered.com/api/appdetails/", params=payload)
            steam_game_info_json = response_steam_game_info.json()

            # If there's an error on the data obtained via GET, ignore and continue to next iterate
            try:
                if steam_game_info_json[str(search[item])]["success"] == True:
                    steam_game_info = steam_game_info_json[str(search[item])]["data"]
            except:
                continue
            steam_game_info_list.append(steam_game_info)

        # Returns the list of founded items, ordered by 'Owners' in case those were obtained on SteamSpy database
        return steam_game_info_list

    def get_steam_package(self, app_id_list: list):

        steam_packages_list = []
        for item in app_id_list:
            payload = {"packageids": item, "l": "brazilian", "cc": "br"}
            response_steam_package = requests.get("http://store.steampowered.com/api/packagedetails/", params=payload)
            steam_package_json = response_steam_package.json()

            if steam_package_json[str(item)]["success"] == True:
                steam_package = steam_package_json[str(item)]["data"]
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
        [Empty JSON if nothing is found on search]
        """

        # Request to 'steamspy.com/api.php?'

        payload = {"request": "appdetails", "appid": app_id}
        response_steamspy_game_info = requests.get("https://steamspy.com/api.php", params=payload)
        steamspy_game_info = response_steamspy_game_info.json()

        # When you request an invalid 'appid' to SteamSpy, the default response are information about CS:GO
        # Handle this scenario to turns it into an empty JSON is required
        if app_id != steamspy_game_info["appid"]:
            return {}
        else:
            return steamspy_game_info