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

load_dotenv()
CONNECT_STRING = os.environ.get("MONGODB_URI")


class Settings_Database(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def error_message(self, ctx: commands.Context, error):
        if isinstance(error, MissingPermissions):
            return f"Desculpe {ctx.author.mention}, você não tem permissão para fazer isso!"

    def settings_collection(self):
        client = MongoClient(CONNECT_STRING)
        db = client.get_database("discordzada")
        collection = db.get_collection("guilds_settings")
        return collection

    def create_settings_data(self, guild: discord.Guild):
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

    @tasks.loop(hours=24)
    async def verify_settings(self):
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
        await ctx.invoke(self.bot.get_command("delete-settings"))
        await ctx.invoke(self.bot.get_command("insert-settings"))


def setup(bot: commands.Bot):
    bot.add_cog(Settings_Database(bot))
