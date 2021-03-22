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

class Reddit(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ESSE BLOCO FUNCIONOU!!! - Printa o título no console toda vez que há algum post novo
    # @tasks.loop(seconds=1)
    # async def meme(self):
    #     subreddit = await reddit.subreddit('meme')
        
    #     async for submission in subreddit.stream.submissions():
    #         print(submission.title)
    
    # Tentar fazer com que a mensagem seja enviada para um canal específico no Discord:
    # FUNCIONA (mas spamma o chat antes de chegar na mensagem mais recente...)
    # @tasks.loop(seconds=1)
    # async def meme(self, channel_id = 822619833396101163):
    #     subreddit = await reddit.subreddit('meme')
    #     text_channel = self.bot.get_channel(channel_id)
        
    #     async for submission in subreddit.stream.submissions():
    #         await text_channel.send(content = submission.title)
    
    # Tentar pegar só os jogos da EPIC e STEAM do FGF
    # FIXME Funcionando +-
    @tasks.loop(seconds=1)
    async def free_game_findings(self, channel_id = 822619833396101163):
        subreddit = await reddit.subreddit('FreeGameFindings')
        text_channel = self.bot.get_channel(channel_id)

        filters = ["EPIC GAMES]", "[STEAM]"]
        async for submission in subreddit.stream.submissions():
            for filt in filters:
                if filt in submission.title.upper():
                    msg_embed = discord.Embed(
                        title = submission.title,
                        description = submission.url
                    )                       
                    await text_channel.send(embed = msg_embed)


    @commands.Cog.listener()
    async def on_ready(self):
        print('START!')
        # self.meme.start()
        # self.free_game_findings.start()

def setup(bot):
    bot.add_cog(Reddit(bot))