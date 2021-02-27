import mal
from mal import *
from mal import AnimeSearch
from mal import Anime
from jikanpy import Jikan

from google_trans_new import google_translator
from howlongtobeatpy import HowLongToBeat

jikan = Jikan()
translator = google_translator()
hltb = HowLongToBeat()

'''
#JIKAN Function

def SearchAnime(title):
    # #Search an Anime
    # search = jikan.search('anime', title, page=1)
    # anime = jikan.anime(search["results"][0]["mal_id"])
    # print(f'TIPO: {type(anime["studios"])}')
    
    # print(f'Dict "ANIME": \n\n')
    # for keys in anime:
    #     print(f'{keys}: {anime[keys]}\n')

    # #Search a manga
    # search = jikan.search('manga', title, page=1)
    # manga = jikan.manga(search["results"][0]["mal_id"])
    
    # print(f'Dict "MANGÁ": \n\n')
    # for keys in manga:
    #     print(f'{keys}: {manga[keys]}\n')
    
    # Search a person
    search = jikan.search('person', title, page=1)
    print(search)
    person = jikan.person(search["results"][0]["mal_id"])
    # person = jikan.person(title)
    
   
    
    print(f'Dict "PERSON": \n\n')
    for keys in person:
        print(f'{keys}: {person[keys]}\n')
    
    
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

#Anime Main
pesquisa = (input('Nome: '))
SearchAnime(pesquisa)
'''

search = jikan.search('anime', '@@@####$$$$$', page = 1)
print(search)