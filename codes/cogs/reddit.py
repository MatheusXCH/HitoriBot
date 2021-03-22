import os, discord, sys, json, requests, math, asyncio, random, pprint
import codes.settings as st
import dotenv
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.utils import *
from pprint import pprint

import asyncpraw

load_dotenv()
reddit = asyncpraw.Reddit(
                    client_id = os.getenv('PRAW_CLIENT_ID'),
                    client_secret = os.getenv('PRAW_CLIENT_SECRET'),
                    username = os.getenv('PRAW_USERNAME'),
                    password = os.getenv('PRAW_PASSWORD'),
                    user_agent = os.getenv('PRAW_USER_AGENT')    
                    )

PLATFORMS = ['STEAM', 'EPIC GAMES', 'EPICGAMES', 'GOG', 'UPLAY', 'ORIGIN', 'PC', 'UBISOFT']
CATEGORIES = ['GAME', 'DLC']

class Reddit(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = 822619833396101163

    @commands.command(name = 'free-game-channel', hidden = True)
    async def set_channel_id(self, ctx: commands.Context):
        self.channel_id = ctx.message.channel.id
        await ctx.message.delete()
        await ctx.author.send(f'Olá *{ctx.author.name}*!\nO canal **{ctx.message.channel.name}** do servidor **{ctx.message.channel.guild}** receberá as mensagens de jogos gratuitos a partir de agora! 😉')


    # FUNCIONANDO!
    # Após iniciado o Bot, exporadicamente compara o post mais recente com o enviado anteriormente
    # Se eles forem diferentes, envia e atualiza a informação
    # TODO Decidir os filtros (CONST)
    # TODO Selecionar os ícones a serem mostrados para cada uma das plataformas!
    @tasks.loop()
    async def free_game_findings(self, channel_id):
        """ Confere continuamente as postagens no 'r/FreeGamesFindings', obtendo aquelas que atendem aos filtros 
        definidos e enviando-as ao canal selecionado (que corresponde ao ID < channel_id >)

        Parameters
        ----------
        - channel_id : int, optional \\
            [ID do canal para o qual as mensagens devem ser enviadas], by default < self.channel_id >
        """

        channel_id = self.channel_id
        def apply_filters(submission):
            """Apply PLATFORMS and CATEGORIES filters on r/FreeGameFingings submissions

            Parameters
            ----------
            - submission : reddit.subreddit.submission \\
                [Subreddit submission object]

            Returns
            -------
            - submission : reddit.subreddit.submission \\
                [The proper submission if its attends the filters]
            """

            for platform in PLATFORMS:
                if platform in submission.title.upper():
                    for category in CATEGORIES:
                        if category in submission.title.upper():
                            return submission

        first_entry_flag = True
        subreddit = await reddit.subreddit('FreeGameFindings')
        text_channel = self.bot.get_channel(channel_id)
        post = {'title': '', 'url': ''}
        while(True):
            newest_list = [apply_filters(submission) async for submission in subreddit.new(limit = 15)] # Get 15 newest posts
            newest_list = [item for item in newest_list if item] # Clear 'None' from the list
            pprint(newest_list)
            newest = newest_list[0]

            if newest.title != post['title']:
                post_stack = []
                for submission in newest_list:
                    if submission.title != post['title']:
                        post_stack.append(submission)
                    else:
                        break

                while(post_stack != []):
                    if first_entry_flag:
                        await text_channel.send('**CONFIRMAÇÃO**: Este canal está recebendo novas postagens de jogos grátis!')
                        first_entry_flag = False
                        break

                    item = post_stack.pop()
                    post['title'] = item.title
                    post['url'] = item.url
                    embed_post = discord.Embed(title = post['title'], description = post['url'])
                    await text_channel.send(embed = embed_post)

            await asyncio.sleep(3600) # Sleep for 1 hour


    @tasks.loop(seconds = 360)
    async def test(self):
        subreddit = await reddit.subreddit('FreeGameFindings')
        print('TEST:')
        async for submission in subreddit.new(limit = 15):
            print(f'{submission.title}')
        print('\n\n')


    @commands.command(name = 'free-game-start', hidden = True)
    async def free_game_start(self, ctx: commands.Context):
        """Starts the Free-Game-Findings task

        Parameters
        ----------
        ctx : commands.Context
            [Discord command Context]
        """

        await ctx.message.delete()
        self.free_game_findings.start()
        await ctx.author.send('FreeGameFindings> RUNNING!')


    @commands.command(name = 'free-game-stop', hidden = True)
    async def free_game_stop(self, ctx: commands.Context):
        """Stops the Free-Game-Findings task

        Parameters
        ----------
        ctx : commands.Context
            [Discord command Context]
        """

        await ctx.message.delete()
        self.free_game_findings.cancel()
        await ctx.author.send('FreeGameFindings> STOPED!')


    @commands.Cog.listener()
    async def on_ready(self):
        # self.free_game_findings.start()
        # await self.free_game_findings()
        pass


def setup(bot):
    bot.add_cog(Reddit(bot))