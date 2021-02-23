import os, discord
import codes.settings as st
from discord.ext import commands
from discord.utils import *
from jikanpy import Jikan
from google_trans_new import google_translator


jikan = Jikan()
translator = google_translator()

class MyAnimeList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #TODO Adicionar interação com Reactions
    #Anime (Command) - Procura por um anime no MyAnimeList (via JikanAPI) e retorna um Embed com detalhes da obra
    @commands.command(pass_context = True, name = 'anime')
    async def anime(self, ctx, *, title : str = 'Nothing Passed to Command'):
        if title == 'Nothing Passed to Command':
            await ctx.send(f'É preciso passar o nome do anime junto ao comando !anime')
        else:
            search = jikan.search('anime', title, page=1)
            #Search é um Dict com informações gerais da consulta
            #Dentro da info "results" está uma Lista com todas as consultas feitas
            #O índice 0 retorna os valores da primeira consulta, também em forma de Dict
            filtro = search["results"][0]
            
            #Passa o MAL_ID obtido no filtro da pesquisa para o método "jikan.anime", 
            #salvando um objeto do tipo "anime". Este objeto possui informações adicionais, tais como "status"
            #e "title_japanese"
            anime = jikan.anime(filtro["mal_id"])             
            
            embed_anime = discord.Embed(
                title = str(anime["title"]),
                colour = discord.Colour(0xfcba03),
                description = f'*{anime["title_english"]}*\n *{anime["premiered"]}*\n *{anime["status"]}*\n *{anime["type"]}*\n *{anime["episodes"]} episódios*',
                url = anime["url"],
            )
            
            #Pegando todos os estúdios que trabalharam no anime, caso mais de um
            studio_list = []
            for std in anime["studios"]:
                studio_list.append(std["name"])
                studios = ', '.join(studio_list)
            
            embed_anime.add_field(name = '**Nota: **', value = str(anime["score"]),inline = True)   
            embed_anime.add_field(name = '**#Rank: **', value = str(anime["rank"]))
            embed_anime.add_field(name = '**#Popularidade:**', value = anime["popularity"], inline = True)
           
            embed_anime.add_field(name = '**Estudio:**', value = studios, inline = True)
            embed_anime.add_field(name = '**Fonte Original:**', value = anime["source"], inline = True)
            
            embed_anime.set_image(url = str(anime["image_url"]))
            await ctx.send(content = None, embed = embed_anime)

    #TODO Anime Synopsis Command
    @commands.command(pass_context = True, name = 'anime-sin')
    async def anime_sin(self, ctx, *, title: str = 'Nothing Passed to Command'):
        if title == 'Nothing Passed to Command':
            await ctx.send(f'É preciso passar o nome do anime junto ao comando !anime-sin')
        else:
            search = jikan.search('anime', title, page=1)
            #Search é um Dict com informações gerais da consulta
            #Dentro da info "results" está uma Lista com todas as consultas feitas
            #O índice 0 retorna os valores da primeira consulta, também em forma de Dict
            filtro = search["results"][0]
            
            #Passa o MAL_ID obtido no filtro da pesquisa para o método "jikan.anime", 
            #salvando um objeto do tipo "anime". Este objeto possui informações adicionais, tais como "status"
            #e "title_japanese"
            anime = jikan.anime(filtro["mal_id"])   
            
            embed_sin = discord.Embed(
                title = str(anime["title"]),
                colour = discord.Colour(0xfcba03),
                description = translator.translate(anime["synopsis"],lang_src='en', lang_tgt='pt'),
                url = anime["url"],        
            )
            await ctx.send(content = None, embed=embed_sin)

def setup(bot):
    bot.add_cog(MyAnimeList(bot))