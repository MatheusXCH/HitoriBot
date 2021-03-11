import os, discord, sys, json, requests
import codes.settings as st
from discord.ext import commands
from discord.utils import *
from urllib.parse import quote

import steam

sys.path.append("D:\\python-codes\\Discordzada") #Config the PYTHONPATH to import "codes.leaguecontent" without warnings
from codes.steamcontent import steambigpicture

big_picture = steambigpicture.SteamBigPicture()

class StoreSteam(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context = True, name = 'steam-update')
    async def steam_update(self, ctx):
        try:
            msg = await ctx.send(embed = discord.Embed(title = "Aguarde", description = "Atualizando os dados da Steam..."))
            big_picture.get_all_games()
            await msg.edit(embed = discord.Embed(title = "Sucesso!", description = "Base de dados do Steam atualizada!"))
            await asyncio.sleep(5)
            await msg.delete()
        except:
            error_msg = await ctx.send(embed = discord.Embed(title = "Erro", description = "Desculpe, parece que houve um problema ao carregar a base de dados da Steam!\nTente novamente após alguns minutos!"))
            await asyncio.sleep(5)
            await msg.delete()
        
    # TODO Avaliar se é necessário alguma informação adicional (Metacritic?, Distribuidora?)
    # TODO Procurar se é possível pegar info de análises (isto é, "Extremamente Positiva", "Muito Positivas", etc)
    # TODO Continuar editando o layout - Adicionar emojis para melhorar a aparência do Embed
    # TODO Pensar em uma maneira com que a busca não dependa do nome do game ser passado de forma exata (isto é, retornar semelhante caso nome incorreto)
    # TODO Avaliar a necessidade ou não de implementar um Embed interativo (via reactions)
    # TODO Traduzir a descrição
    # BUG Nem todos os jogos possuem o atributo "Metacritc" - É preciso tratar quando isso ocorre
    # BUG Nem todos os jogos possuem o atributo "Legal Notice" - É preciso tratar quando isso ocorre
    # !game - Retorna dados da Steam acerca do game passado como parâmetro
    @commands.command(pass_context = True, name = 'game')
    async def search_game(self, ctx, *, game_title):
        try:
            game_info = big_picture.get_game_info(game_title=game_title)
        except:
            await ctx.send(embed = discord.Embed(description = 'Desculpe, não consegui encontrar esse jogo!'))
        
        steam_game_embed = discord.Embed(
            title = f'{game_info["name"]}',
            description = f'📆**Data de lançamento**: {game_info["release_date"]["date"]}\n\n{game_info["short_description"]}',
            url = f'https://store.steampowered.com/app/{str(game_info["steam_appid"])}/{quote(game_info["name"])}'
        )
        steam_game_embed.set_image(url = f'{game_info["header_image"]}')
        try:
            steam_game_embed.set_footer(text = f'{game_info["legal_notice"]}')
        except:
            steam_game_embed.set_footer(text = f'©{game_info["name"]}')
        
        genres_list = [item['description'] for item in game_info['genres']]
        genres = '\n'.join(genres_list)
        
        developers_list = [item for item in game_info['developers']]
        developers = '\n'.join(developers_list)
        
        publishers_list = [item for item in game_info['publishers']]
        publishers = '\n'.join(publishers_list)
        
        categories_list = [item['description'] for item in game_info['categories']]
        categories = '\n'.join(categories_list)
        
        initial_value = str(game_info["price_overview"]["initial"])
        base_price = f'R$ {initial_value[:-2]},{initial_value[-2:]}'
        
        languages = game_info["supported_languages"]
        type(languages)
        
        try:
            metacritic_score = game_info["metacritic"]["score"]
        except:
            metacritic_score = 'N/A'
        
        steam_game_embed.add_field(name = '📌 Desenvolvedor: ', value = developers, inline = True)
        steam_game_embed.add_field(name = '📌 Publisher: ', value = publishers, inline = True)
        steam_game_embed.add_field(name = '📌 Recursos: ', value = categories, inline = True)
        
        steam_game_embed.add_field(name = '📌 Gêneros: ', value = genres, inline = True)
        steam_game_embed.add_field(name = '📌 Metacritic: ', value = f'✳ Score: {metacritic_score}', inline = True)
            
        # steam_game_embed.add_field(name = 'Idiomas: ', value = languages, inline = True)
        
        steam_game_embed.add_field(name = '**PREÇO**', value = f'🔸 **Base:** {base_price}\n' + 
                                                             f'🔹 **Atual:** {game_info["price_overview"]["final_formatted"]}\n' + 
                                                             f'📉 **Desconto:** {game_info["price_overview"]["discount_percent"]}%\n' ,
                                                             inline = True)
         
        await ctx.send(embed = steam_game_embed)
    
def setup(bot):
    bot.add_cog(StoreSteam(bot))