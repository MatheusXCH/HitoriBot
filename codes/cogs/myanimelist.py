import os, discord
import codes.settings as st
from discord.ext import commands
from discord.utils import *
from jikanpy import Jikan
from jikanpy import exceptions
from google_trans_new import google_translator

jikan = Jikan()
translator = google_translator()

class MyAnimeList(commands.Cog):
    """Módulo: MyAnimeList
        - Integra os resultados de busca do MyAnimeList com o Bot, via jikanpy API 
        - Utiliza da API 'google_trans_new' para fazer automaticamente traduções necessárias de 'EN/PT-BR' 
        - Os comandos listados abaixo buscam fornecer informações, em forma de Embed interativos, sobre animes, mangás, suas sinopses e personagens das obras
        #### Utiliza:
        ##### JikanPY API (by abhinavk99 on: https://github.com/abhinavk99/jikanpy) 
        ##### Google_Trans_New API (by lushan88a on: https://github.com/lushan88a/google_trans_new)
    """
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True, name = 'anime')
    async def anime(self, ctx, *, anime_title : str = 'Nothing Passed to Command'):
        """!anime [title]
            - Procura por um anime no MyAnimeList e obtém as infos: 
                - Título, Lançamento, Status, Tipo, Episódios, URL, Nota, Rank, Popularidade, Estudio, Fonte Original e Imagem
            - Retorna um Embed interativo com os dados obtidos
        """
        
        if anime_title == 'Nothing Passed to Command':
            nothing_passed_embed = discord.Embed(description = f'É preciso passar o nome do anime junto ao comando !anime' )
            await ctx.send(embed = nothing_passed_embed)
        else:
            search = jikan.search('anime', anime_title, page=1)
            
            #Trata caso onde não há resultado algum
            if(search["results"] == []):
                no_results_embed = discord.Embed(title = 'OPS!', description = 'Desculpe, mas parece que a consulta feita não retornou nada!')
                await ctx.send(embed = no_results_embed)
                return
            
            def anime_pages_layout(i):
                anime = jikan.anime(search["results"][i]["mal_id"])
                embed_anime = discord.Embed(
                    title = str(anime["title"]),
                    colour = discord.Colour(0x04d197),
                    description = f'*{anime["title_english"]}*\n *{anime["premiered"]}*\n *{anime["status"]}*\n *{anime["type"]}*\n *{anime["episodes"]} episódios*',
                    url = anime["url"],
                )
                studio_list = []
                studios = ''
                for std in anime["studios"]:
                    studio_list.append(std["name"])
                studios = ', '.join(studio_list)
                if studios == '': studios = 'Unknown'
                
                genres_list = []
                genres = ''
                label_count = 0
                for genre in anime["genres"]:
                    label_count += 1
                    genres_list.append(genre["name"])
                    if label_count == 3:
                        genres_list.append('line_feed')
                        label_count = 0
                genres = ', '.join(genres_list)
                if genres == '': genres = 'Unknown'
                #Tratando os 'Enters'
                genres = genres.replace('line_feed,', '\n')
                genres = genres.replace(', line_feed', '\n') #Caso o valor seja múltiplo de 3, apaga o último line_feed
                
                
                embed_anime.add_field(name = '**Nota: **', value = str(anime["score"]),inline = True)   
                embed_anime.add_field(name = '**#Rank: **', value = str(anime["rank"]))
                embed_anime.add_field(name = '**#Popularidade:**', value = anime["popularity"], inline = True)
            
                embed_anime.add_field(name = '**Estudio:**', value = studios, inline = True)
                embed_anime.add_field(name = '**Fonte Original:**', value = anime["source"], inline = True)
                embed_anime.add_field(name = '**Gêneros: **', value = genres, inline = False)
                
                embed_anime.set_footer(text = f'Clique em 📄 para ver a sinopse')
                embed_anime.set_image(url = str(anime["image_url"]))
                
                return embed_anime
            
            page = anime_pages_layout(0)
            
            message = await ctx.send(embed = page)
            await message.add_reaction('⏪')
            await message.add_reaction('◀')
            await message.add_reaction('▶')
            await message.add_reaction('⏩')
            await message.add_reaction('📄')
            
            def check(reaction, user):
                return user == ctx.author
                
                #BUG Quando todos, exceto o bot, podem editar, ocorre um bug no qual o último botão do layout é apagado e 
                # o painel muda sozinho para o último valor possível da pesquisa
                # return user != self.bot 

            i = 0
            reaction = None
            try:
                while True:
                    if str(reaction) == '⏪':
                        i = 0
                        page = anime_pages_layout(i)
                        await message.edit(embed = page)
                    elif str(reaction) == '◀':
                        if i > 0:
                            i -= 1
                            page = anime_pages_layout(i)
                            await message.edit(embed = page)
                    elif str(reaction) == '▶':
                        if i < len(search) - 1:
                            i += 1
                            page = anime_pages_layout(i)
                            await message.edit(embed = page)
                    elif str(reaction) == '⏩':
                        i = len(search) - 1
                        page = anime_pages_layout(len(search) - 1)
                        await message.edit(embed = page)
                    elif str(reaction) == '📄':
                        await ctx.invoke(self.bot.get_command('anime-sin'), anime_sin_title = page.title)

                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout = 30.0, check = check)
                        await message.remove_reaction(reaction, user)
                    except:
                        break
            except:
                error_embed = discord.Embed(title = 'Erro:', description = 'Desculpe, o limite de consultas por minuto ao MyAnimeList foi atingido!\nPor favor, aguarde um pouco e tente novamente!')
                await ctx.send(embed = error_embed)
            await message.clear_reactions()

    @commands.command(pass_context = True, name = 'anime-sin')
    async def anime_sin(self, ctx, *, anime_sin_title: str = 'Nothing Passed to Command'):
        """!anime-sin [title]
            - Procura por um anime no MyAnimeList e obtém a sua sinopse
            - Retorna um Embed com o título da obra encontrada e sua sinopse traduzida para PT-BR
        """
        
        if anime_sin_title == 'Nothing Passed to Command':
            nothing_passed_embed = discord.Embed(description = f'É preciso passar o nome do anime junto ao comando !anime-sin' )
            await ctx.send(embed = nothing_passed_embed)
        else:
            search = jikan.search('anime', anime_sin_title, page=1)
            
            #Trata caso onde não há resultado algum
            if(search["results"] == []):
                no_results_embed = discord.Embed(title = 'OPS!', description = 'Desculpe, mas parece que a consulta feita não retornou nada!')
                await ctx.send(embed = no_results_embed)
                return
            
            anime = jikan.anime(search["results"][0]["mal_id"])
            embed_anime_sin = discord.Embed(
                title = str(anime["title"]),
                colour = discord.Colour(0x04d197),
                description = translator.translate(anime["synopsis"],lang_src='en', lang_tgt='pt'),
                url = anime["url"]
            )
            await ctx.send(content = None, embed=embed_anime_sin)

    @commands.command(pass_context = True, name = 'manga')
    async def manga(self, ctx, *, manga_title : str = 'Nothing Passed to Command'):
        """!manga [title]
        - Procura por um mangá no MyAnimeList e obtém as infos: 
            - Título, Status, Tipo, Capítulos, Volumes, URL, Nota, Rank, Popularidade, Autor, Revista e Imagem
        - Retorna um Embed interativo com os dados obtidos
        """
        
        if manga_title == 'Nothing Passed to Command':
            nothing_passed_embed = discord.Embed(description = f'É preciso passar o nome do mangá junto ao comando !manga' )
            await ctx.send(embed = nothing_passed_embed)
        else:
            search = jikan.search('manga', manga_title, page = 1)
            
            #Trata caso onde não há resultado algum
            if(search["results"] == []):
                no_results_embed = discord.Embed(title = 'OPS!', description = 'Desculpe, mas parece que a consulta feita não retornou nada!')
                await ctx.send(embed = no_results_embed)
                return
            
            def manga_pages_layout(i):
                manga = jikan.manga(search["results"][i]["mal_id"])
                
                embed_manga = discord.Embed(
                    title = manga["title"],
                    colour = discord.Colour(0xfc7b03),
                    description = f'*{manga["title_english"]}*\n*{manga["status"]}*\n *{manga["type"]}*\n *{manga["chapters"]} capítulos*\n *{manga["volumes"]} volumes*',
                    url = manga["url"],
                )
                #Pegando todos os autores e revistas que publicam o mangá, caso mais de um
                authors_list = []
                author = ""
                for std in manga["authors"]:
                    authors_list.append(std["name"])
                author = '; '.join(authors_list)
                if author == "": author = 'Unknown' #É preciso tratar, pois o caso no qual
                                                    #author == "" gera um erro no discord.Embed
                
                magazines_list = []            
                magazine = ""
                for std in manga["serializations"]:
                    magazines_list.append(std["name"])
                magazine = '; '.join(magazines_list)
                if magazine == "": magazine = 'Unknown'
                
                genres_list = []
                genres = ''
                label_count = 0
                for genre in manga["genres"]:
                    label_count += 1
                    genres_list.append(genre["name"])
                    if label_count == 3:
                        genres_list.append('line_feed')
                        label_count = 0
                genres = ', '.join(genres_list)
                if genres == '': genres = 'Unknown'
                #Tratando os 'Enters'
                genres = genres.replace('line_feed,', '\n')
                genres = genres.replace(', line_feed', '\n') #Caso o valor seja múltiplo de 3, apaga o último line_feed
                
                embed_manga.add_field(name = '**Nota: **', value = str(manga["score"]),inline = True)   
                embed_manga.add_field(name = '**#Rank: **', value = str(manga["rank"]))
                embed_manga.add_field(name = '**#Popularidade:**', value = manga["popularity"], inline = True)
            
                embed_manga.add_field(name = '**Autor:**', value = author, inline = True)
                embed_manga.add_field(name = '**Revista:**', value = magazine, inline = False)
                embed_manga.add_field(name = '**Gêneros:**', value = genres, inline = False)
                
                embed_manga.set_footer(text = f'Clique em 📄 para ver a sinopse')
                embed_manga.set_image(url = str(manga["image_url"]))

                return embed_manga
            
            page = manga_pages_layout(0)
            
            message = await ctx.send(embed = page)
            await message.add_reaction('⏪')
            await message.add_reaction('◀')
            await message.add_reaction('▶')
            await message.add_reaction('⏩')
            await message.add_reaction('📄')
            
            def check(reaction, user):
                return user == ctx.author
                
                #BUG Quando todos, exceto o bot, podem editar, ocorre um bug no qual o último botão do layout é apagado e 
                # o painel muda sozinho para o último valor possível da pesquisa
                # return user != self.bot 
            
            i = 0
            reaction = None
            
            try: 
                while True:
                    if str(reaction) == '⏪':
                        i = 0
                        page = manga_pages_layout(i)
                        await message.edit(embed = page)
                    elif str(reaction) == '◀':
                        if i > 0:
                            i -= 1
                            page = manga_pages_layout(i)
                            await message.edit(embed = page)
                    elif str(reaction) == '▶':
                        if i < len(search) - 1:
                            i += 1
                            page = manga_pages_layout(i)
                            await message.edit(embed = page)
                    elif str(reaction) == '⏩':
                        i = len(search) - 1
                        page = manga_pages_layout(len(search) - 1)
                        await message.edit(embed = page)
                    elif str(reaction) == '📄':
                        await ctx.invoke(self.bot.get_command('manga-sin'), manga_sin_title = page.title)

                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout = 30.0, check = check)
                        await message.remove_reaction(reaction, user)
                    except:
                        break
            except:
                error_embed = discord.Embed(title = 'Erro:', description = 'Desculpe, o limite de consultas por minuto ao MyAnimeList foi atingido!\nPor favor, aguarde um pouco e tente novamente!')
                await ctx.send(embed = error_embed)
            await message.clear_reactions()

    @commands.command(pass_context = True, name = 'manga-sin')
    async def manga_sin(self, ctx, *, manga_sin_title: str = 'Nothing Passed to Command'):
        """!manga-sin [title]
            - Procura por um mangá no MyAnimeList e obtém sua sinopse 
            - Retorna um Embed com o título da obra encontrada e sua sinopse
        """
        
        if manga_sin_title == 'Nothing Passed to Command':
            nothing_passed_embed = discord.Embed(description = f'É preciso passar o nome do mangá junto ao comando !anime-sin' )
            await ctx.send(embed = nothing_passed_embed)
        else:
            search = jikan.search('manga', manga_sin_title, page=1)
            
            #Trata caso onde não há resultado algum
            if(search["results"] == []):
                no_results_embed = discord.Embed(title = 'OPS!', description = 'Desculpe, mas parece que a consulta feita não retornou nada!')
                await ctx.send(embed = no_results_embed)
                return
            
            manga = jikan.manga(search["results"][0]["mal_id"])
            
            embed_sin = discord.Embed(
                title = str(manga["title"]),
                colour = discord.Colour(0xfc7b03),
                description = translator.translate(manga["synopsis"],lang_src='en', lang_tgt='pt'),
                url = manga["url"],        
            )
            await ctx.send(content = None, embed=embed_sin)

    #TODO Arrumar problemas - Os personagens mostrados não são os mais populares. Algumas vezes é preciso escrever o nome completo deles, o que não é ideal
    @commands.command(pass_context = True, name = 'mal-char')
    async def mal_char(self, ctx, *, char_name : str = 'Nothing Passed to Command'):
        """!mal-char [name]
            - Procura por um personagem no MyAnimeList e obtém as infos: 
                - Nome, Anime, Manga/Light Novel, URL e Imagem
            - Retorna um Embed com os dados obtidos
            
            #### Limitações:
            - Devido a forma como o MAL busca por personagens, ao passar o nome incompleto a API nem sempre retorna o resultado mais popular
            - Diante disso, buscando amenizar a situação, essa função busca os 10 primeiros resultados e retorna o mais popular deles
                - Ainda assim, nem sempre é garantido que o resultado mais popular de todo o MAL estará entre os 10 primeiros
        """
        
        if char_name == 'Nothing Passed to Command':
            nothing_passed_embed = discord.Embed(description = f'É preciso passar o nome do personagem junto ao comando !mal-char' )
            await ctx.send(embed = nothing_passed_embed)
        else:
            try:
                search = jikan.search('character', char_name, page=1)
                
                members_favorites_list = []
                size_of_search = 0
                if len(search["results"]) < 10:
                    size_of_search = len(search["results"])
                else:
                    size_of_search = 10
                
                print(size_of_search) #DEBUG
                
                for i in range (size_of_search):
                    print(f'CHEGOU AQUI {i} VEZES!') #DEBUG
                    character_aux = jikan.character(search["results"][i]["mal_id"])
                    members_favorites_list.append(character_aux["member_favorites"])
                    print(f'Membros{i}: {members_favorites_list}') #DEBUG

                index = members_favorites_list.index(max(members_favorites_list))
                members_favorites_list.clear()
                character = jikan.character(search["results"][index]["mal_id"])    
                
            except exceptions.APIException:
                char_error_embed = discord.Embed(title = 'Erro', description = f'Hmm... Não consegui encontrar este personagem no MyAnimeList!\nEspere alguns segundos e tente novamente!')
                await ctx.send(embed = char_error_embed)
                return

            japan_voice_list = []
            voice = ''
            for dub in character["voice_actors"]:
                if dub["language"] == 'Japanese':
                    japan_voice_list.append(dub["name"])
            voice = '; '.join(japan_voice_list)
            if voice == '': voice = 'Unknown'

            #Tratando possíveis erros na descrição
            #Esses erros podem acontecer pois os itens "animeography" e "mangaography" podem ser listas vazias
            descrição = ""
            try:
                descrição += f'**Anime:** *{character["animeography"][0]["name"]}* \n'
            except:
                descrição += "None \n"
            try:
                descrição += f'**Mangá/Light Novel:** *{character["mangaography"][0]["name"]}* \n'
            except:
                descrição += "None \n"
            try:
                descrição += f'**Dublador:** *{voice}* \n'
            except:
                descrição += "None \n"
            
            page = discord.Embed(
                title = str(character["name"]),
                colour = discord.Colour(0xc9002c),
                description = descrição,
                url = character["url"],
            )
            
            page.set_image(url = str(character["image_url"]))
           
            await ctx.send(content = None, embed = page)
    
    #TODO Fazer um comando para pesquisar pelos TOP anime ou mangá

def setup(bot):
    bot.add_cog(MyAnimeList(bot))