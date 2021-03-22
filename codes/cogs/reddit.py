import os, discord, sys, json, requests, math, asyncio, random, pprint
import codes.settings as st
import dotenv
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.utils import *
from pprint import pprint

import codes.settings as st #Get the globals from Settings

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
CATEGORIES = ['GAME', 'DLC', 'OTHER', 'ALPHA', 'BETA', 'ALPHA/BETA']
ICONS_DICT = {
    'STEAM' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/512px-Steam_icon_logo.svg.png',
    'EPIC GAMES' : 'https://cdn2.unrealengine.com/Epic+Games+Node%2Fxlarge_whitetext_blackback_epiclogo_504x512_1529964470588-503x512-ac795e81c54b27aaa2e196456dd307bfe4ca3ca4.jpg',
    'EPICGAMES' : 'https://cdn2.unrealengine.com/Epic+Games+Node%2Fxlarge_whitetext_blackback_epiclogo_504x512_1529964470588-503x512-ac795e81c54b27aaa2e196456dd307bfe4ca3ca4.jpg',
    'GOG' : 'https://static.wikia.nocookie.net/this-war-of-mine/images/1/1a/Logo_GoG.png/revision/latest/scale-to-width-down/220?cb=20160711062658',
    'UPLAY' : 'https://play-lh.googleusercontent.com/f868E2XQBpfl677hykMnZ4_HlKqrOs0fUhuwy0TC9ZI_PQLn99RtBV2kQ7Z50OtQkw=s180-rw',
    'UBISOFT' : 'https://play-lh.googleusercontent.com/f868E2XQBpfl677hykMnZ4_HlKqrOs0fUhuwy0TC9ZI_PQLn99RtBV2kQ7Z50OtQkw=s180-rw',
    'ORIGIN' : 'https://cdn2.iconfinder.com/data/icons/gaming-platforms-logo-shapes/250/origin_logo-512.png',
    'PC' : 'https://pbs.twimg.com/profile_images/300829764/pc-gamer-avatar.jpg'
}

class Reddit(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = 822619833396101163


    @commands.command(name = 'free-game-channel', hidden = True)
    async def set_channel_id(self, ctx: commands.Context):
        self.channel_id = ctx.message.channel.id
        await ctx.message.delete()
        await ctx.author.send(f'Olá *{ctx.author.name}*!\nO canal **{ctx.message.channel.name}** do servidor **{ctx.message.channel.guild}** receberá as mensagens de jogos gratuitos a partir de agora! 😉')


    @tasks.loop()
    async def free_game_findings(self, channel_id = None):
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
            newest_list = [apply_filters(submission) async for submission in subreddit.new(limit = 200)] # Get 15 newest posts
            newest_list = [item for item in newest_list if item] # Clear 'None' from the list
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
                    for platform in PLATFORMS:
                        if platform in post['title'].upper():
                            icon = ICONS_DICT[platform]
                    
                    embed_post = discord.Embed(title = post['title'], description = post['url'])
                    embed_post.set_thumbnail(url = icon)
                    await text_channel.send(embed = embed_post)

            await asyncio.sleep(3600) # Sleep for 1 hour


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
        self.free_game_findings.start()
        print('Free-Game-Findings is RUNNING!')


def setup(bot):
    bot.add_cog(Reddit(bot))