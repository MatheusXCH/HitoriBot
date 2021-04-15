import asyncio
import os

# Get the globals from Paths
import codes.paths as path
import discord
import dotenv
import json
import inspect
from pprint import pprint
from discord.ext import commands, tasks
from discord.ext.commands import MissingPermissions, has_permissions
from pymongo import MongoClient
from dotenv import load_dotenv

# # # Módulo: Settings_Database
# # - Responsável por conectar o bot ao database e criar uma interface para que os recursos de configuração dos
# # servidores possam ser corretamente armazenados
# # - Dentre esses recursos estão os dados manipulados através dos módulos "Rules", "Playlist" e "FreeGame"
# # - As informações são atualizadas automaticamente no servidor quando alteradas em quaisquer instâncias,
# # utilizando dos listeners fornecidos pela biblioteca do discord.py

# # # Utiliza:
# # - Discord.py API (by Rapptz on: https://github.com/Rapptz/discord.py)
# # - MongoDB Python Driver [pymongo] (by mongodb on: https://github.com/mongodb/mongo-python-driver)

load_dotenv()
CONNECT_STRING = os.environ.get("MONGODB_URI")


class Settings_Database(commands.Cog):
    """This module handles the guilds settings in MongoDB"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def error_message(self, ctx: commands.Context, error):
        """Defines an default error message"""

        if isinstance(error, MissingPermissions):
            return f"Desculpe {ctx.author.mention}, você não tem permissão para fazer isso!"

    def create_settings_data(self, guild: discord.Guild):
        """Creates and default structure to 'settings_data'

        Parameters
        ----------
        - guild : discord.Guild \\
            [The guild to get information from]

        Returns
        -------
        - settings_data : dict \\
            [The structured data for 'settings_data']
        """
        settings_data = {
            "_id": guild.id,
            "guild": {"guild_id": guild.id, "guild_name": guild.name},
            "settings": {
                "prefix": ["!"],
                "bad_words": [],
                "rules": {"rules_text": "O texto passado ao bot pelo comando '!add-rules' aparecerá aqui!"},
                "playlist": [],
                "freegame_channel": {"channel_id": None, "channel_name": None},
            },
        }

        return settings_data

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Listener that creates a new 'guild_settings' document in MongoDB database when the bot joins a new server"""

        settings_data = self.create_settings_data(guild=guild)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                collection.insert_one(settings_data)
                print(
                    f"GUILDS_SETTINGS >> 'on_guild_join' SUCCESS: As configurações para a guilda ID: {settings_data['_id']} foram INSERIDAS no database."
                )
        except Exception as e:
            print(
                f"GUILDS_SETTINGS >> 'on_guild_join' ERROR: Não foi possível inserir as configurações para a guilda ID: {settings_data['_id']} no database."
            )
            print(e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Listener that removes a 'guild_settings' document in MongoDB database when the bot leaves some guild"""

        settings_data = self.create_settings_data(guild=guild)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                collection.delete_one({"_id": guild.id})
                print(
                    f"GUILDS_SETTINGS >> 'on_guild_remove' SUCCESS: As configurações para a guilda de ID: {settings_data['_id']} foram REMOVIDAS do database."
                )
        except Exception as e:
            print(
                f"GUILDS_SETTINGS >> 'on_guild_remove' ERROR: Não foi possível remover as configurações para a guilda ID: {settings_data['_id']} do database."
            )
            print(e)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        """Listener that updates the guild name everytime it changes"""

        if before.name != after.name:
            try:
                with MongoClient(CONNECT_STRING) as client:
                    collection = client.get_database("discordzada").get_collection("guilds_settings")
                    collection.update_one({"_id": before.id}, {"$set": {"guild.guild_name": after.name}})
                    print(
                        f"GUILDS_SETTINGS >> 'on_guild_update' SUCCESS: O nome da guilda de ID: {before.id} foram ATUALIZADO do database."
                    )
            except Exception as e:
                print(
                    f"GUILDS_SETTINGS >> 'on_guild_update' ERROR: Não foi possível remover as configurações para a guilda ID: {before.id} do database."
                )
                print(e)
        else:
            pass

    @tasks.loop(hours=24)
    async def verify_settings(self):
        """Listener that verifies if any new guild joining event was missed in the past 24 hours"""
        guilds = [guild for guild in self.bot.guilds]

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")

                for guild in guilds:
                    verify = collection.find_one({"_id": guild.id})

                    if verify is None:
                        guild_data = self.create_guild_data(guild)
                        collection.insert_one(guild_data)
                        print(
                            f"GUILDS_SETTINGS >> 'verify_settings': As configurações da Guilda ID: {guild.id} não estavam cadastradas, portanto foram inseridas no database."
                        )

                print(
                    "GUILDS_SETTINGS >> 'verify_settings': As configurações de guilds ausentes no database foram verificadas."
                )
        except Exception as e:
            print(
                "GUILDS_SETTINGS >> 'verify_settings' ERROR: Não foi possível verificar as configurações de guildas não cadastradas no database."
            )
            print(e)

    @commands.Cog.listener()
    async def on_ready(self):
        self.verify_settings.start()

    # # # Commands below are only usable by the bot owner to handle exceptional cases
    #
    #
    #
    #

    @commands.command(name="insert-settings", hidden=True)
    @commands.is_owner()
    async def insert_settings(self, ctx: commands.Context):
        """Owner Only => Forces insert settings data on MongoDB database"""

        settings_data = self.create_settings_data(guild=ctx.guild)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                collection.insert_one(settings_data)
                print(
                    f"GUILDS_SETTINGS >> 'on_guild_join' SUCCESS: As configurações para a guilda ID: {settings_data['_id']} foram INSERIDAS no database."
                )
        except Exception as e:
            print(
                f"GUILDS_SETTINGS >> 'on_guild_join' ERROR: Não foi possível inserir as configurações para a guilda ID: {settings_data['_id']} no database."
            )
            print(e)

    @commands.command(name="delete-settings", hidden=True)
    @commands.is_owner()
    async def delete_data(self, ctx: commands.Context):
        """Owner Only => Forces remove settings data on MongoDB database"""

        settings_data = self.create_settings_data(guild=ctx.guild)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                collection.delete_one({"_id": ctx.guild.id})
                print(
                    f"GUILDS_SETTINGS >> 'on_guild_remove' SUCCESS: As configurações para a guilda de ID: {settings_data['_id']} foram REMOVIDAS do database."
                )
        except Exception as e:
            print(
                f"GUILDS_SETTINGS >> 'on_guild_remove' ERROR: Não foi possível remover as configurações para a guilda ID: {settings_data['_id']} do database."
            )
            print(e)

    @commands.command(name="reset-settings", hidden=True)
    @commands.is_owner()
    async def reset_settings(self, ctx: commands.Context):
        """Owner Only => Forces reset settings data on MongoDB database (done by removing and adding info again)"""

        await ctx.invoke(self.bot.get_command("delete-settings"))
        await ctx.invoke(self.bot.get_command("insert-settings"))


def setup(bot: commands.Bot):
    bot.add_cog(Settings_Database(bot))
