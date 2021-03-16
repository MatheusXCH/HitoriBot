import os, discord, sys, json, requests, math, asyncio, random, pprint
import codes.settings as st
import dotenv
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import *
from urllib.parse import quote
from pprint import pprint

import steam

sys.path.append("D:\\python-codes\\Discordzada") #Config the PYTHONPATH to import "codes.leaguecontent" without warnings
from codes.steamcontent import steambigpicture

load_dotenv()
my_steam_id = '76561198058563121'
steam_key = os.getenv('STEAM_KEY')
big_picture = steambigpicture.SteamBigPicture()

class StoreSteam(commands.Cog):
    """Módulo que permite a conexão do PyBOT com a Steam-BR"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context = True, name = 'steam-update')
    async def steam_update(self, ctx):
        """!steam-update => Atualiza a base de dados da Steam"""
        
        try:
            msg = await ctx.send(embed = discord.Embed(title = "Aguarde", description = "Atualizando os dados da Steam..."))
            big_picture.request_all_games()
            await msg.edit(embed = discord.Embed(title = "Sucesso!", description = "Base de dados do Steam atualizada!"))
            await asyncio.sleep(5)
            await msg.delete()
        except:
            error_msg = await ctx.send(embed = discord.Embed(title = "Erro", description = "Desculpe, parece que houve um problema ao carregar a base de dados da Steam!\nTente novamente após alguns minutos!"))
            await asyncio.sleep(5)
            await msg.delete()
        
    # TODO Avaliar a necessidade ou não de implementar um Embed interativo (via reactions)
    # TODO Informação "Packages" (apareceria juntamente ao Price_Overview em um segundo Embed, sendo este interativo)

    @commands.command(pass_context = True, name = 'steam')
    async def search_game(self, ctx, *, game_title):
        """!game <game_title> => Retorna informações sobre um jogo na Steam"""
        
        steam_game_list = []
        steam_game = {}
        steamspy_info = {}
        try:
            steam_game_list = big_picture.get_steam_game(game_title = game_title)
            steam_game = steam_game_list[0] # Get only the first item
            steamspy_info = big_picture.steamspy_complementary_info(app_id = steam_game['steam_appid'])
            
            if steam_game == []:
                raise Exception
        except:
            await ctx.send(embed = discord.Embed(title = 'Desculpe', description = f'Não consegui encontrar esse jogo!\nCaso seja a primeira consulta do dia, considere executar o comando "!steam-update" para atualizar os dados'))
            return
            
        steam_game_embed = discord.Embed(
            title = f'{steam_game["name"]}',
            colour = discord.Colour(random.randint(0, 0xFFFFFF)),
            description = f'📆 **Data de lançamento:** {steam_game["release_date"]["date"]}\n' + 
                        f'🏷 **Tipo:** {steam_game["type"].upper()}\n'
                        f'{steam_game["short_description"]}',
            url = f'https://store.steampowered.com/app/{str(steam_game["steam_appid"])}/{quote(steam_game["name"])}'
        )
        steam_game_embed.set_image(url = f'{steam_game["header_image"]}')
        try:
            steam_game_embed.set_footer(text = f'{steam_game["legal_notice"]}')
            if steam_game_embed.footer.__len__ > 2048:
                raise Exception
        except:
            steam_game_embed.set_footer(text = f'©{steam_game["name"]}')
        
        def get_reviews_label(reviews_perc):
            if 0 <= reviews_perc <= 19: return '⛔ Muito negativas'
            if 20 <= reviews_perc <= 39: return '⛔ Levemente negativas'
            if 40 <= reviews_perc <= 69: return '⏹ Neutras'
            if 70 <= reviews_perc <= 79: return '☑ Levemente positivas'
            if 80 <= reviews_perc <= 94: return '✅ Muito positivas'
            if 95 <= reviews_perc <= 100: return '✅ Extremamente positivas'
        
        try:
            tags_list = steamspy_info['tags']
            tags_dict = dict(sorted(tags_list.items(), key = lambda item: item[1])[-5:])
            tags = '\n'.join([tag for tag in tags_dict])
            if tags == '':
                raise Exception
        except:
            tags = 'N/A'
        
        try:
            developers_list = [item for item in steam_game['developers']]
            developers = '\n'.join(developers_list)
            if developers == '':
                raise Exception
        except:
            developers = 'N/A'
        
        try:
            publishers_list = [item for item in steam_game['publishers']]
            publishers = '\n'.join(publishers_list)
            if publishers == '':
                raise Exception
        except:
            publishers = 'N/A'
        
        try:
            categories_list = [item['description'] for item in steam_game['categories']]
            categories_list_filtered = [item for item in categories_list if (item == 'Um jogador' or item == 'Multijogador' or 
                                                                            item == 'Cooperativo' or item == 'Cooperativo online' or 
                                                                            item == 'Conquistas Steam' or item == 'Compatibilidade total com controle' or
                                                                            item == 'Remote Play Together' or item == 'Cartas Colecionáveis Steam' or
                                                                            item == 'Multijogador entre plataformas' or item == 'Compatibilidade parcial com controle' or
                                                                            item == 'JxJ' or item == 'JxJ online')]
            categories = '\n'.join(categories_list_filtered)
            if categories == '':
                raise Exception
        except:
            categories = 'N/A'
        
        #TODO Arrumar os problemas possíveis de ocorrer no parâmetro 'Price_Overview'
        if not steam_game['is_free']:
            try:
                initial_value = str(steam_game["price_overview"]["initial"])
                base_price = f'R$ {initial_value[:-2]},{initial_value[-2:]}'
                final_price = steam_game["price_overview"]["final_formatted"]
                discount = f'{steam_game["price_overview"]["discount_percent"]}%'
            except:
                base_price = 'N/A'
                final_price = 'N/A'
                discount = 'N/A'
        
        try:
            reviews_perc = math.floor((steamspy_info['positive']/(steamspy_info['positive'] + steamspy_info['negative']))* 100)
            reviews_label = get_reviews_label(reviews_perc)
            reviews_dict = {'score': f'({reviews_perc}%)', 'label': reviews_label}
        except:
            reviews_dict = {'score': '\u200b', 'label': 'N/A'}
        
        try:
            languages_list = steamspy_info["languages"].split(', ')
            languages_list_filtered = [lang for lang in languages_list if (lang == 'English' or lang == 'Japanese' or lang == 'Portuguese - Brazil' or lang == 'Spanish - Spain')]
            languages = '\n'.join(languages_list_filtered)
        except:
            languages = 'N/A'
        
        try:
            metacritic_score = steam_game["metacritic"]["score"]
        except:
            metacritic_score = '---'
        
        steam_game_embed.add_field(name = '📌 Desenvolvedor: ', value = developers, inline = True)
        steam_game_embed.add_field(name = '📌 Publisher: ', value = publishers, inline = True)
        steam_game_embed.add_field(name = '📌 Tags: ', value = tags, inline = True)
        
        steam_game_embed.add_field(name = '📌 Avaliações: ', value = f'{big_picture.EMOJI_METACRITIC} {metacritic_score}\n\n' + 
                                                                    f'{reviews_dict["label"]}\n {reviews_dict["score"]}', inline = True)
        steam_game_embed.add_field(name = '📌 Idiomas: ', value = languages, inline = True)
        steam_game_embed.add_field(name = '📌 Recursos: ', value = categories, inline = True)
        
        if not steam_game['is_free']:
            steam_game_embed.add_field(name = '**PREÇO**', value = 
                                                                    f'🔸 **Base:** {base_price}\n' + 
                                                                    f'🔹 **Atual:** {final_price}\n' + 
                                                                    f'📉 **Desconto:** {discount}\n' ,
                                                                    inline = True)
        else:
            steam_game_embed.add_field(name = '**PREÇO**', value = f'💸 Gratuito para Jogar')

        await ctx.send(embed = steam_game_embed)
    
def setup(bot):
    bot.add_cog(StoreSteam(bot))