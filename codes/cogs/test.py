import mal
from mal import *
from mal import AnimeSearch
from mal import Anime
from jikanpy import Jikan

from google_trans_new import google_translator

jikan = Jikan()
translator = google_translator()

#JIKAN Function

def SearchAnime(title):
    search = jikan.search('anime', title, page=1)
    
    #Search é um Dict com informações gerais da consulta
    #Dentro da info "results" está uma Lista com todas as consultas feitas
    #O índice 0 retorna os valores da primeira consulta, também em forma de Dict
    #anime = search
    
    #print(f'{anime}')
    
    filtro = search["results"][0]
    
    '''
    print(f'Resultado:\n\n')
    for keys in search:
        print(f'{keys} : {search[keys]}\n')
    '''
    
    anime = jikan.anime(filtro["mal_id"])
    print(f'TIPO: {type(anime["studios"])}')
    
    print(f'Dict "ANIME": \n\n')
    for keys in anime:
        print(f'{keys}: {anime[keys]}\n')
    
    
    
#MAL-API Function
'''
def SearchAnime(title):
    search = AnimeSearch(title)
    anime_id = search.results[0].mal_id
    anime = Anime(anime_id)
    
    print(
        f'\nTítulo: {anime.title}',
        f'\nTítulo [EN]: {anime.title_english}',
        f'\nStatus: {anime.status}',
        f'\nEpisódios: {anime.episodes}',
        f'\nScore: {anime.score}',
        f'\nRank: #{anime.rank}',
        f'\nPopularidade: #{anime.popularity}'
    )
    print(f'\n\nRelacionados:')
    for key in anime.related_anime:
        print(f'{key}: {anime.related_anime[key]}\n')
'''

pesquisa = (input('Nome do Anime: '))
print(f'VALOR = {pesquisa}')
SearchAnime(pesquisa)

