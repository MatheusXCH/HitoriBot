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

jikan = Jikan()
translator = google_translator()
hltb = HowLongToBeat()

load_dotenv()
RIOT_KEY = os.getenv('RIOT_KEY')
watcher = LolWatcher(RIOT_KEY)

class dataDragon:
    #Atributos compartilhados entre todas as instâncias de dataDragon
    my_region = 'BR1'
    lang_code = 'pt_BR'
    
    def __init__(self):
        
        #Métodos do construtor
        def get_current_version():
            response = requests.get('https://ddragon.leagueoflegends.com/api/versions.json')
            league_versions = response.json()
            return league_versions[0]
        
        def get_all_champions_json():
            all_champions_url = f'http://ddragon.leagueoflegends.com/cdn/{self.latest_version}/data/{self.lang_code}/champion.json'
            all_response = requests.get(all_champions_url)
            return all_response.json()

        #Atributos do construtor
        self.latest_version = get_current_version()
        self.all_champions = get_all_champions_json()
            
            
    
    #Métodos da classe
    def get_profile_icon(self, iconID: int):
        return f'http://ddragon.leagueoflegends.com/cdn/{self.latest_version}/img/profileicon/{iconID}.png'
        
    def get_champion_name(self, championID: int):
        champion_name = ''
        all_champions = self.all_champions
        for item in all_champions['data']:
            row = all_champions['data'][item]
            if row['key'] == str(championID):
                champion_name = row['name']
        return champion_name
        
        
ob1 = dataDragon()
print(ob1.latest_version)
champ = ob1.get_champion_name(64)
print(champ)

# champion = ob1.get_champion_name(64)
# print(champion)


# name = input('Nome: ')
# Riot_Watcher_Func(name)

#JIKAN Function

# def SearchAnime(title):
#     #Search an Anime
#     search = jikan.search('anime', title, page=1)
#     anime = jikan.anime(search["results"][0]["mal_id"])
#     print(f'TIPO: {type(anime["studios"])}')
    
#     print(f'Dict "ANIME": \n\n')
#     for keys in anime:
#         print(f'{keys}: {anime[keys]}\n')

    # #Search a manga
    # search = jikan.search('manga', title, page=1)
    # manga = jikan.manga(search["results"][0]["mal_id"])
    
    # print(f'Dict "MANGÁ": \n\n')
    # for keys in manga:
    #     print(f'{keys}: {manga[keys]}\n')
    
    # Search a person
    # search = jikan.search('person', title, page=1)
    # print(search)
    # person = jikan.person(search["results"][0]["mal_id"])
    # person = jikan.person(title)
    
   
    
    # print(f'Dict "PERSON": \n\n')
    # for keys in person:
    #     print(f'{keys}: {person[keys]}\n')
    
    
    #Search a character
    # search = jikan.search('character', title, page=1)
    # character = jikan.character(search["results"][0]["mal_id"])
    
    # character_about_list = character["about"].splitlines()
    
    # character_about = []
    # for item in character_about_list:
    #     character_about.append(item.replace('\\n', ''))
    #     about = '\n'.join(character_about)
    # print(character_about)
    
    # for i in range(10):
    #     character_about.append(character_about_list[i].replace('\\n', ''))
    # about = '\n'.join(character_about)
    # print(about)
    
    # print(f'Dict "CHARACTER": \n\n')
    # for keys in character:
    #     print(f'{keys}: {character[keys]}\n')
    # cont = 0
    # for item in search["results"]:
    #     print(f'{item}\n')
    #     cont += 1
    #     if cont == 10: break
    
    # print(f'\n\n{cont}')

# #Anime Main
# pesquisa = (input('Nome: '))
# SearchAnime(pesquisa)


# search = jikan.search('anime', '@@@####$$$$$', page = 1)
# print(search)