import os, dotenv, requests, json, pprint, random, time
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


    def get_all_games(self):
        """Read data from 'steam_spy_data.txt'"""
        
        with open(st.steam_data_path + 'steam_spy_data.txt', 'r') as json_file:
            data = json.load(json_file)
        return data


    def request_all_games(self):
        """Requests new data from SteamSpy and update the '.txt' file"""
        
        all_steamspy_apps = {}
        
        #Page 0 to 43 - 1000 itens por página, ordenados por mais comprados da Steam, segundo o SteamSpy
        for i in range(44):
            payload = {'request': 'all', 'page':i}
            response_all_steamspy_apps = requests.get('https://steamspy.com/api.php', params=payload)

            if i == 0:
                all_steamspy_apps = response_all_steamspy_apps.json()
            else:
                all_steamspy_apps.update(response_all_steamspy_apps.json())
            
        with open(st.steam_data_path + 'steam_spy_data.txt', 'w') as outfile:
            json.dump(all_steamspy_apps, outfile)


    # FIXME Por usar os dados do SteamSpy, a função atualmente NÃO RETORNA:
        # Jogos cadastrados na Steam, porém ainda não lançados
        # Jogos muito recentes (Database do SteamSpy ainda não atualizou)
        # Jogos muito impopulares
        
    # TODO Corrigir o problema parcialmente, fazendo com que "Caso não encontrado, procurar direto na base de dados da Steam".
    # Isso possuirá algumas limitações, mas o objetivo é que os casos de resposta pós pesquisa via SteamSpy mal-sucedida sejam:
        # Nome do jogo passado CORRETAMENTE ("Precise Search"):
            # Encontrar o jogo solicitado;
            # Ainda não encontrar o jogo, mesmo ele existindo no site da Steam (problemas de atualizações dos dados da plataforma);
        
        # Nome do jogo passado INCOMPLETO ("Imprecise Search"):
            # Encontrar o jogo na base de dados da Steam (Funcionará melhor quanto mais preciso for a string de entrada);
            # Encontrar o jogo errado na base de dados da Steam ("Imprecise Search" não funciona tão bem nos dados da Steam pois obter métricas é muito custoso);
            # Ainda não encontrar o jogo, mesmo ele existindo no site da Steam (problemas de atualizações dos dados da plataforma);
        
        # Nome do jogo passado ERRADO:
            # Não encontrar o jogo solicitado, pois este não pode ser encontrado;
        
    def get_steam_game(self, game_title: str):
        '''Get detailed information about games\n
        If a correpondent key value is passed as <game_title>, returns info about this game. Otherwise, requests information
        of a list of games that the key matches the substring <game_title>'''
        
        all_games_json = self.get_all_games()

        # # PRECISE SEARCH
        # Inicialmente, pesquisa exatamente por <Game Title>
        search = [item for item in all_games_json if all_games_json[item]['name'] == game_title]

        if search != []:
            pass
        else:
            # # IMPRECISE SEARCH
            # Caso a pesquisa exata não encontre nada, procura por itens que contém a string de entrada
            search = [item for item in all_games_json if game_title in all_games_json[item]['name']]

        if len(search) < 10: 
            max_range = len(search)
        else: 
            max_range = 10

        steam_game_info_list = []
        # Faz requisição para cada um dos itens
        for item in range(max_range):
            #Request to https://store.steampowered.com/api/appdetails/'
            payload = {'appids' : search[item], 'l':'brazilian', 'cc':'br'}
            response_steam_game_info = requests.get('https://store.steampowered.com/api/appdetails/', params=payload)
            steam_game_info_json = response_steam_game_info.json()
            
            #Caso ocorra um erro no dado obtido via GET, ignora e continua para o próximo loop
            try:
                steam_game_info = steam_game_info_json[str(search[item])]['data']
            except:
                pass
            steam_game_info_list.append(steam_game_info)

        return steam_game_info_list[0]  # Retorna apenas o primeiro elemento que, por padrão, é sempre o mais popular
                                        # (Devido ao fato dos dados do SteamSpy serem ordenados por "Owners")


    def get_steamspy_info(self, game_title: str):
        """Get <game_title> data from SteamSpy database"""

        all_games_steamspy_json = self.get_all_games()
        app_id_steamspy = next((item for item in all_games_steamspy_json if all_games_steamspy_json[item]['name'] == game_title), None)

        #Request to steamspy.com/api.php?
        payload = {'request':'appdetails', 'appid':app_id_steamspy}
        response_steamspy_game_info = requests.get('https://steamspy.com/api.php', params=payload)
        game_info_steamspy = response_steamspy_game_info.json()

        return game_info_steamspy



# # REQUEST TIME AND RESULT TEST:
# steam = SteamBigPicture()
# search_input = input('Game Title: ')
# start_time = time.time()
# game = steam.get_game_info(search_input, 'steam')
# print(f"name: {game['name']}, id: {game['steam_appid']}")
# print('\n\n\n')
# print(f'Tempo da Busca = {time.time() - start_time} segundos')

# # # Steam_Spy_Data GET:
# steam = SteamBigPicture()
# steam.request_all_games(source='steamspy')
# print('\nFINALIZADO!')
