import asyncio
import json
import math
import os
import pprint
import random
import sys
from pprint import pprint

import asyncpraw
import codes.settings as st  # Get the globals from Settings
import discord
import dotenv
import requests
from discord.ext import commands, tasks
from discord.utils import *
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
reddit = asyncpraw.Reddit(
    client_id=os.getenv("PRAW_CLIENT_ID"),
    client_secret=os.getenv("PRAW_CLIENT_SECRET"),
    username=os.getenv("PRAW_USERNAME"),
    password=os.getenv("PRAW_PASSWORD"),
    user_agent=os.getenv("PRAW_USER_AGENT"),
)
load_dotenv()
CONNECT_STRING = os.getenv("MONGO_CONNECT_STRING")

PLATFORMS = [
    "STEAM",
    "EPIC GAMES",
    "EPICGAMES",
    "GOG",
    "UPLAY",
    "ORIGIN",
    "PC",
    "UBISOFT",
]
CATEGORIES = ["GAME", "DLC", "OTHER", "ALPHA", "BETA", "ALPHA/BETA"]
ICONS_DICT = {
    "STEAM": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/512px-Steam_icon_logo.svg.png",
    "EPIC GAMES": "https://cdn2.unrealengine.com/Epic+Games+Node%2Fxlarge_whitetext_blackback_epiclogo_504x512_1529964470588-503x512-ac795e81c54b27aaa2e196456dd307bfe4ca3ca4.jpg",
    "EPICGAMES": "https://cdn2.unrealengine.com/Epic+Games+Node%2Fxlarge_whitetext_blackback_epiclogo_504x512_1529964470588-503x512-ac795e81c54b27aaa2e196456dd307bfe4ca3ca4.jpg",
    "GOG": "https://static.wikia.nocookie.net/this-war-of-mine/images/1/1a/Logo_GoG.png/revision/latest/scale-to-width-down/220?cb=20160711062658",
    "UPLAY": "https://play-lh.googleusercontent.com/f868E2XQBpfl677hykMnZ4_HlKqrOs0fUhuwy0TC9ZI_PQLn99RtBV2kQ7Z50OtQkw=s180-rw",
    "UBISOFT": "https://play-lh.googleusercontent.com/f868E2XQBpfl677hykMnZ4_HlKqrOs0fUhuwy0TC9ZI_PQLn99RtBV2kQ7Z50OtQkw=s180-rw",
    "ORIGIN": "https://cdn2.iconfinder.com/data/icons/gaming-platforms-logo-shapes/250/origin_logo-512.png",
    "PC": "https://pbs.twimg.com/profile_images/300829764/pc-gamer-avatar.jpg",
}


class Reddit(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.channel_id = 822619833396101163

    def freegames_collection(self):
        client = MongoClient(CONNECT_STRING)
        db = client.get_database(name="discordzada")
        collection = db.get_collection(name="free-game-findings-channels")
        return collection

    @commands.command(name="free-game-channel", hidden=True)
    async def set_channel_id(self, ctx: commands.Context):
        collection = self.freegames_collection()

        try:
            data = {
                "guild_id": ctx.guild.id,
                "guild_name": ctx.guild.name,
                "channel_id": ctx.channel.id,
                "channel_name": ctx.channel.name,
            }
            collection.update_one({"guild_id": data["guild_id"]}, {"$set": data}, upsert=True)
        except:
            await ctx.send(
                "Desculpe, **houve um problema** ao salvar essa informação. Por favor, **tente novamente** em alguns instantes!"
            )
            return

        await ctx.message.delete()
        msg = await ctx.send(
            f"O canal **{ctx.channel.name}** receberá as mensagens de jogos gratuitos a partir de agora! 😉"
        )
        await asyncio.sleep(5)
        await msg.delete()

        collection.database.client.close()

    @tasks.loop()
    async def free_game_findings(self, channel_id=None):
        """ Confere continuamente as postagens no 'r/FreeGamesFindings', obtendo aquelas que atendem aos filtros 
        definidos e enviando-as ao canal selecionado (que corresponde ao ID < channel_id >)

        Parameters
        ----------
        - channel_id : int, optional \\
            [ID do canal para o qual as mensagens devem ser enviadas], by default < self.channel_id >
        """

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

        collection = self.freegames_collection()

        first_entry_flag = True
        subreddit = await reddit.subreddit("FreeGameFindings")
        channel_id_list = [item["channel_id"] for item in collection.find({}, {"channel_id": 1})]
        post = {"title": "", "url": ""}

        while True:
            # Get newest posts
            newest_list = [apply_filters(submission) async for submission in subreddit.new(limit=10)]
            newest_list = [item for item in newest_list if item]  # Clear 'None' from the list
            newest = newest_list[0]

            if newest.title != post["title"]:
                post_stack = []

                if first_entry_flag:
                    post["title"] = newest.title
                    post["url"] = newest.url

                    for channel_id in channel_id_list:
                        text_channel = self.bot.get_channel(id=channel_id)
                        await text_channel.send(
                            "**CONFIRMAÇÃO**: Este canal está recebendo novas postagens de jogos grátis!"
                        )  # Temporário - Apenas durante o período de testes
                    first_entry_flag = False
                else:
                    for submission in newest_list:
                        if submission.title != post["title"]:
                            post_stack.append(submission)
                        else:
                            break

                    while post_stack != []:
                        item = post_stack.pop()
                        post["title"] = item.title
                        post["url"] = item.url
                        icon = "".join(
                            [ICONS_DICT[platform] for platform in PLATFORMS if platform in post["title"].upper()]
                        )

                        embed_post = discord.Embed(title=post["title"], description=post["url"])
                        embed_post.set_thumbnail(url=icon)

                        for channel_id in channel_id_list:
                            text_channel = self.bot.get_channel(id=channel_id)
                            await text_channel.send(embed=embed_post)

            collection.database.client.close()
            await asyncio.sleep(3600)  # Sleep for 1 hour

    @commands.command(name="free-game-start", hidden=True)
    async def free_game_start(self, ctx: commands.Context):
        """Starts the Free-Game-Findings task

        Parameters
        ----------
        ctx : commands.Context
            [Discord command Context]
        """

        await ctx.message.delete()
        self.free_game_findings.start()
        msg = await ctx.send("**FreeGameFindings is RUNNING!**")
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command(name="free-game-stop", hidden=True)
    async def free_game_stop(self, ctx: commands.Context):
        """Stops the Free-Game-Findings task

        Parameters
        ----------
        ctx : commands.Context
            [Discord command Context]
        """

        await ctx.message.delete()
        self.free_game_findings.cancel()
        msg = await ctx.send("**FreeGameFindings has been STOPPED!**")
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command(name="free-game-restart", hidden=True)
    async def free_game_restart(self, ctx: commands.Context):
        """Restarts the Free-Game-Findings task

        Parameters
        ----------
        ctx : commands.Context
            [Discord command Context]
        """

        await ctx.message.delete()
        self.free_game_findings.cancel()
        await asyncio.sleep(3)
        self.free_game_findings.start()
        msg = await ctx.send("**FreeGameFindings has been RESTARTED!**")
        await asyncio.sleep(3)
        await msg.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        self.free_game_findings.start()


def setup(bot):
    bot.add_cog(Reddit(bot))
