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

    # TEST (probably WORKING)
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

    # TEST (probably WORKING)
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

    # # # Comandos abaixo são, pelo menos inicialmente, para fins de TEST e DEBUG
    #
    #
    #
    #
    #
    #
    #
    #

    @commands.command(name="insert-settings", hidden=True)
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
    async def reset_settings(self, ctx: commands.Context):
        await ctx.invoke(self.bot.get_command("delete-settings"))
        await ctx.invoke(self.bot.get_command("insert-settings"))


def setup(bot: commands.Bot):
    bot.add_cog(Settings_Database(bot))
