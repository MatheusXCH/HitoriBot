import asyncio
import os

# Get the globals from Paths
import codes.paths as path
import discord
import dotenv
import json
import inspect
import schedule
from pprint import pprint
from datetime import datetime
from discord.ext import commands, tasks
from discord.ext.commands import MissingPermissions, has_permissions
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
CONNECT_STRING = os.environ.get("MONGODB_URI")


class Guild_Database(commands.Cog):
    """This module handles the guilds information in MongoDB"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def error_message(self, ctx: commands.Context, error):
        """Defines an default error message"""

        if isinstance(error, MissingPermissions):
            return f"Desculpe {ctx.author.mention}, você não tem permissão para fazer isso!"

    def get_text_channel_data(self, text_channel: discord.TextChannel):
        """Creates and default structure to 'text_channel_data'

        Parameters
        ----------
        - text_channel : discord.TextChannel \\
            [The text channel to get information from]

        Returns
        -------
        - text_channel_data : dict \\
            [The structured data for 'text_channel_data']
        """

        try:
            category = text_channel.category.name
        except Exception:
            category = None

        text_channel_data = {
            "channel_id": text_channel.id,
            "channel_name": text_channel.name,
            "channel_category": category,
        }

        return text_channel_data

    def get_voice_channel_data(self, voice_channel: discord.VoiceChannel):
        """Creates and default structure to 'voice_channel_data'

        Parameters
        ----------
        - voice_channel : discord.VoiceChannel \\
            [The voice channel to get information from]

        Returns
        -------
        - voice_channel_data : dict \\
            [The structured data for 'voice_channel_data']
        """

        try:
            category = voice_channel.category.name
        except Exception:
            category = None

        voice_channel_data = {
            "channel_id": voice_channel.id,
            "channel_name": voice_channel.name,
            "channel_category": category,
        }

        return voice_channel_data

    def get_role_data(self, role: discord.Role):
        """Creates and default structure to 'roles_data'

        Parameters
        ----------
        - role : discord.Role \\
            [The role to get information from]

        Returns
        -------
        - roles_data : dict \\
            [The structured data for 'roles_data']
        """

        roles_data = {
            "role_name": role.name,
            "role_id": role.id,
            "permissions": [perm[0] for perm in role.permissions if perm[1]],
        }

        return roles_data

    def get_member_data(self, member: discord.Member):
        """Creates and default structure to 'members_data'

        Parameters
        ----------
        - member : discord.Member \\
            [The member to get information from]

        Returns
        -------
        - members_data : dict \\
            [The structured data for 'members_data']
        """

        member_data = {
            "member_name": member.name,
            "member_id": member.id,
            "member_is_bot": member.bot,
            "member_nick": member.nick,
            "member_joined_at": member.joined_at,
            "member_roles": {
                "top_role": member.top_role.name,
                "roles": [role.name for role in member.roles],
            },
        }

        return member_data

    def create_guild_data(self, guild: discord.Guild):
        """Creates and default structure to 'guild_data'

        Parameters
        ----------
        - guild : discord.Guild \\
            [The guild to get information from]

        Returns
        -------
        - guild_data : dict \\
            [The structured data for 'guild_data']
        """

        guild_data = {
            "_id": guild.id,
            "guild": {
                "guild_id": guild.id,
                "guild_name": guild.name,
                "channels_info": {
                    "text_channels": [
                        self.get_text_channel_data(text_channel) for text_channel in guild.text_channels
                    ],
                    "voice_channels": [
                        self.get_voice_channel_data(voice_channel) for voice_channel in guild.voice_channels
                    ],
                },
                "roles_info": [self.get_role_data(role) for role in guild.roles],
                "members_info": {
                    "members_count": guild.member_count,
                    "members": [self.get_member_data(member) for member in guild.members],
                },
            },
        }

        return guild_data

    # WORKING
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Listener that creates a new 'guild_info' document in MongoDB database when the bot joins a new server"""

        guild_data = self.create_guild_data(guild)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")
                collection.insert_one(guild_data)
                collection.database.client.close()
                print(
                    f"GUILDS_INFO >> 'on_guild_join' SUCCESS: A Guilda com ID:{guild_data['_id']} foi INSERIDO no database."
                )
        except Exception as e:
            print(
                f"GUILDS_INFO >> 'on_guild_join' ERROR: Não foi possível inserir a Guilda ID:{guild.id} no database."
            )
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Listener that removes a 'guild_info' document in MongoDB database when the bot joins a new server"""

        guild_data = self.create_guild_data(guild)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")
                collection.delete_one({"_id": guild.id})
                collection.database.client.close()
                print(
                    f"GUILDS_INFO >> 'on_guild_remove' SUCCESS: A Guilda ID:{guild_data['_id']} foi EXCLUÍDO do database."
                )
        except Exception as e:
            print(
                f"GUILDS_INFO >> on_guild_remove' ERROR: Não foi possível excluir a Guilda ID:{guild.id} do database."
            )
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        """Listener that updates a 'guild_info' document in MongoDB database when the bot leaves the server"""

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")
                collection.update_one(
                    {"_id": after.id}, {"$set": {"guild.guild_name": after.name, "guild.guild_id": after.id}}
                )
                collection.database.client.close()
                print(f"GUILDS_INFO >> 'on_guild_update' SUCCESS: A Guilda ID:{after.id} foi ATUALIZADA no database.")
        except Exception as e:
            print(f"GUILDS_INFO >> 'on_guild_update' ERROR: Não foi possível atualizar a Guilda ID:{after.id}.")
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        """Listener that creates a 'guild_info' document in MongoDB database when a new channel is created on the server

        The channel can be even a "TextChannel" or "VoiceChannel"
        """

        guild = channel.guild

        if str(channel.type) == "text":
            try:
                with MongoClient(CONNECT_STRING) as client:
                    collection = client.get_database("discordzada").get_collection("guilds_info")
                    text_channel_data = self.get_text_channel_data(channel)
                    collection.update_one(
                        {"_id": guild.id},
                        {"$push": {"guild.channels_info.text_channels": text_channel_data}},
                    )
                    collection.database.client.close()
                    print(
                        f"GUILDS_INFO >> 'on_guild_channel_create' SUCCESS: O Canal de Texto ID:{text_channel_data['channel_id']} da Guilda ID: {guild.id} foi INSERIDO no database."
                    )
            except Exception as e:
                print(
                    f"GUILDS_INFO >> 'on_guild_channel_create' ERROR: Não foi possível inserir o Canal de Texto de ID:{text_channel_data['channel_id']} da Guilda ID: {guild.id}."
                )
                print(e)

        elif str(channel.type) == "voice":
            try:
                with MongoClient(CONNECT_STRING) as client:
                    collection = client.get_database("discordzada").get_collection("guilds_info")
                    voice_channel_data = self.get_voice_channel_data(channel)
                    collection.update_one(
                        {"_id": guild.id},
                        {"$push": {"guild.channels_info.voice_channels": voice_channel_data}},
                    )
                    collection.database.client.close()
                    print(
                        f"GUILDS_INFO >> 'on_guild_channel_create' SUCCESS: O Canal de Voz ID:{voice_channel_data['channel_id']} da Guilda ID: {guild.id} foi INSERIDO no database"
                    )
            except Exception as e:
                print(
                    f"GUILDS_INFO >> 'on_guild_channel_create' ERROR: Não foi possível inserir o Canal de Voz de ID:{voice_channel_data['channel_id']} da Guilda ID: {guild.id}."
                )
                print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        """Listener that removes a 'guild_info' document in MongoDB database when a channel is removed from the server

        The channel can be even a "TextChannel" or "VoiceChannel"
        """

        guild = channel.guild

        if str(channel.type) == "text":
            try:
                with MongoClient(CONNECT_STRING) as client:
                    collection = client.get_database("discordzada").get_collection("guilds_info")
                    text_channel_data = self.get_text_channel_data(channel)
                    collection.update_one(
                        {"_id": guild.id},
                        {"$pull": {"guild.channels_info.text_channels": text_channel_data}},
                    )
                    collection.database.client.close()
                    print(
                        f"GUILDS_INFO >> 'on_guild_channel_delete' SUCCESS: O Canal de Texto ID:{text_channel_data['channel_id']} da Guilda ID: {guild.id} foi REMOVIDO no database."
                    )
            except Exception as e:
                print(
                    f"GUILDS_INFO >> 'on_guild_channel_delete' ERROR: Não foi possível remover o Canal de Texto ID:{text_channel_data['channel_id']} da Guilda ID: {guild.id}."
                )
                print(e)

        elif str(channel.type) == "voice":
            try:
                with MongoClient(CONNECT_STRING) as client:
                    collection = client.get_database("discordzada").get_collection("guilds_info")
                    voice_channel_data = self.get_voice_channel_data(channel)
                    collection.update_one(
                        {"_id": guild.id},
                        {"$pull": {"guild.channels_info.voice_channels": voice_channel_data}},
                    )
                    collection.database.client.close()
                    print(
                        f"GUILDS_INFO >> 'on_guild_channel_delete' SUCCESS: O Canal de Voz ID:{voice_channel_data['channel_id']} da Guilda ID: {guild.id} foi REMOVIDO no database."
                    )
            except Exception as e:
                print(
                    f"GUILDS_INFO >> 'on_guild_channel_delete' ERROR: Não foi possível remover o Canal de Voz ID:{voice_channel_data['channel_id']} da Guilda ID: {guild.id}."
                )
                print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        """Listener that updates a 'guild_info' document in MongoDB database when a channel is updated on the server

        The channel can be even a "TextChannel" or "VoiceChannel"
        """

        guild = after.guild

        if str(after.type) == "text":
            try:
                with MongoClient(CONNECT_STRING) as client:
                    collection = client.get_database("discordzada").get_collection("guilds_info")
                    text_channel_after_data = self.get_text_channel_data(after)
                    collection.update_one(
                        {"_id": guild.id, "guild.channels_info.text_channels.channel_id": after.id},
                        {"$set": {"guild.channels_info.text_channels.$": text_channel_after_data}},
                    )
                    collection.database.client.close()
                    print(
                        f"GUILDS_INFO >> 'on_guild_channel_update' SUCCESS: O Canal de Texto ID:{text_channel_after_data['channel_id']} da Guilda ID: {guild.id} foi ATUALIZADO no database."
                    )
            except Exception as e:
                print(
                    f"GUILDS_INFO >> 'on_guild_channel_update' ERROR: Não foi possível atualizar o Canal de Texto ID:{text_channel_after_data['channel_id']} da Guilda ID: {guild.id}"
                )
                print(e)
        elif str(after.type) == "voice":
            try:
                with MongoClient(CONNECT_STRING) as client:
                    collection = client.get_database("discordzada").get_collection("guilds_info")
                    voice_channel_after_data = self.get_voice_channel_data(after)
                    collection.update_one(
                        {"_id": guild.id, "guild.channels_info.voice_channels.channel_id": after.id},
                        {"$set": {"guild.channels_info.voice_channels.$": voice_channel_after_data}},
                    )
                    collection.database.client.close()
                    print(
                        f"GUILDS_INFO >> 'on_guild_channel_update' SUCCESS: O Canal de Voz ID:{voice_channel_after_data['channel_id']} da Guilda ID:{guild.id} foi ATUALIZADO no database."
                    )
            except Exception as e:
                print(
                    f"GUILDS_INFO >> 'on_guild_channel_update' ERROR: Não foi possível atualizar o Canal de Voz ID:{voice_channel_after_data['channel_id']} da Guilda ID:{guild.id}."
                )
                print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        """Listener that creates a 'guild_info' document in MongoDB database when a new role is created on the server"""

        guild = role.guild
        role_data = self.get_role_data(role)
        pprint(role_data)
        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")
                collection.update_one({"_id": guild.id}, {"$push": {"guild.roles_info": role_data}})
                collection.database.client.close()
                print(
                    f"GUILDS_INFO >> 'on_guild_role_create' SUCCESS: A role de ID:{role_data['role_id']} da Guilda ID:{guild.id} foi INSERIDA no database."
                )
        except Exception as e:
            print(
                f"GUILDS_INFO >> 'on_guild_role_create' ERROR: Não foi possível inserir a role de ID:{role_data['role_id']} da Guilda ID:{guild.id}."
            )
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        """Listener that removes a 'guild_info' document in MongoDB database when a role is removed from the server"""

        guild = role.guild
        role_data = self.get_role_data(role)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")
                collection.update_one({"_id": guild.id}, {"$pull": {"guild.roles_info": role_data}})
                collection.database.client.close()
                print(
                    f"GUILDS_INFO >> 'on_guild_role_delete' SUCCESS: A role de ID:{role_data['role_id']} da Guilda ID:{guild.id} foi REMOVIDA no database."
                )
        except Exception as e:
            print(
                f"GUILDS_INFO >> 'on_guild_role_delete' ERROR: Não foi possível remover a role de ID:{role_data['role_id']} da Guilda ID:{guild.id}."
            )
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        """Listener that updates a 'guild_info' document in MongoDB database when role is updated on the server"""

        guild = after.guild
        role_data = self.get_role_data(after)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")
                collection.update_one(
                    {"_id": guild.id, "guild.roles_info.role_id": after.id},
                    {"$set": {"guild.roles_info.$": role_data}},
                )
                collection.database.client.close()
                print(
                    f"GUILDS_INFO >> 'on_guild_role_update' SUCCESS: A role de ID:{role_data['role_id']} da Guilda ID:{guild.id} foi ATUALIZADA no database."
                )
        except Exception as e:
            print(
                f"GUILDS_INFO >> 'on_guild_role_update' ERROR: Não foi possível atualizar a role de ID:{role_data['role_id']} da Guilda ID:{guild.id}."
            )
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Listener that creates a 'guild_info' document in MongoDB database when a new member joins the server"""

        guild = member.guild
        member_data = self.get_member_data(member)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")
                collection.update_one({"_id": guild.id}, {"$inc": {"guild.members_info.members_count": 1}})
                collection.update_one({"_id": guild.id}, {"$push": {"guild.members_info.members": member_data}})
                collection.database.client.close()
                print(
                    f"GUILDS_INFO >> 'on_member_join' SUCCESS: Um novo membro de ID:{member_data['member_id']} da Guilda ID:{guild.id} foi INSERIDO no database."
                )
        except Exception as e:
            print(
                f"GUILDS_INFO >> 'on_member_join' ERROR: Não foi possível inserir um novo membro no documento de ID:{member_data['member_id']} da Guilda ID:{guild.id}."
            )
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Listener that removes a 'guild_info' document in MongoDB database when a member leaves the server"""

        guild = member.guild
        member_data = self.get_member_data(member)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")
                collection.update_one({"_id": guild.id}, {"$inc": {"guild.members_info.members_count": -1}})
                collection.update_one({"_id": guild.id}, {"$pull": {"guild.members_info.members": member_data}})
                collection.database.client.close()
                print(
                    f"GUILDS_INFO >> 'on_member_remove' SUCCESS: Um membro de ID:{member_data['member_id']} da Guilda ID:{guild.id} foi REMOVIDO do database."
                )
        except Exception as e:
            print(
                f"GUILDS_INFO >> 'on_member_remove' ERROR: Não foi possível remover um membro do documento de ID:{member_data['member_id']} da Guilda ID:{guild.id}."
            )
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Listener that updates a 'guild_info' document in MongoDB database when a member updates its information on the server"""

        if (
            before.name != after.name
            or before.nick != after.nick
            or before.top_role != after.top_role
            or before.roles != after.roles
        ):
            member_after_data = self.get_member_data(after)

            try:
                with MongoClient(CONNECT_STRING) as client:
                    collection = client.get_database("discordzada").get_collection("guilds_info")
                    collection.update_one(
                        {"_id": after.guild.id, "guild.members_info.members.member_id": after.id},
                        {"$set": {"guild.members_info.members.$": member_after_data}},
                    )
                    collection.database.client.close()
                    print(
                        f"GUILDS_INFO >> 'on_member_update' SUCCESS: O membro de ID:{member_after_data['member_id']} da Guilda ID:{after.guild.id} foi ATUALIZADO!"
                    )
            except Exception as e:
                print(
                    f"GUILDS_INFO >> 'on_member_update' ERROR: Não foi possível atualizar o membro de ID:{member_after_data['member_id']} da Guilda ID:{after.guild.id}."
                )
                print(e)
        else:
            pass

    @tasks.loop(hours=24)
    async def all_guilds_update(self):
        """Listener that, once a day, update all the infos about the guilds registered in the MongoDB database"""
        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")
                guild_data_list = [
                    self.create_guild_data(self.bot.get_guild(guild["guild"]["guild_id"]))
                    for guild in collection.find({}, {"guild.guild_id": 1})
                ]

                for guild_data in guild_data_list:
                    print(
                        f"GUILDS_INFO >> 'all_guilds_update': Atualizando informações da Guilda ID: {guild_data['_id']}"
                    )
                    collection.update_one({"_id": guild_data["_id"]}, {"$set": {"guild": guild_data["guild"]}})
                collection.database.client.close()
                print("GUILDS_INFO >> 'all_guilds_update':Todas as informações foram atualizadas com sucesso!")
        except Exception as e:
            print(
                "GUILDS_INFO >> 'all_guilds_update' ERROR: Não foi possível atualizar as informações das guildas cadastradas no database."
            )
            print(e)

    @tasks.loop(hours=24)
    async def verify_guilds(self):
        """Listener that verifies if any new guild joining event was missed in the past 24 hours"""

        guilds = [guild for guild in self.bot.guilds]

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")

                for guild in guilds:
                    verify = collection.find_one({"_id": guild.id})

                    if verify is None:
                        guild_data = self.create_guild_data(guild)
                        collection.insert_one(guild_data)
                        print(
                            f"GUILDS_INFO >> 'verify_guilds': A Guilda ID: {guild.id} não estava cadastrada, portanto foi inserida no database."
                        )

                print("GUILDS_INFO >> 'verify_guilds': As guildas ausentes no database foram verificadas.")
        except Exception as e:
            print(
                "GUILDS_INFO >> 'verify_guilds' ERROR: Não foi possível verificar as guildas não cadastradas no database."
            )
            print(e)

    @commands.Cog.listener()
    async def on_ready(self):
        self.all_guilds_update.start()
        self.verify_guilds.start()

    # # # Commands below are only usable by the bot owner to handle exceptional cases
    #
    #
    #
    #

    @commands.command(name="insert-data", hidden=True)
    @commands.is_owner()
    async def insert_data(self, ctx: commands.Context):
        """Owner Only => Forces insert guild data on MongoDB database"""

        guild_data = self.create_guild_data(guild=ctx.guild)

        with open("guild_config.json", "w") as outfile:
            json.dump(guild_data, outfile, indent=4, default=str)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")
                collection.insert_one(guild_data)
                collection.database.client.close()
                print(
                    f"GUILDS_INFO >> 'on_guild_join' SUCCESS: O objeto com ID:{guild_data['_id']} da Guilda ID:{ctx.guild.id} foi INSERIDO no database"
                )
        except Exception as e:
            print(
                f"GUILDS_INFO >> 'on_guild_join' ERROR: Não foi possível inserir o objeto ID:{ctx.guild.id} da Guilda ID:{ctx.guild.id}."
            )
            print(e)

    @commands.command(name="delete-data", hidden=True)
    @commands.is_owner()
    async def delete_data(self, ctx: commands.Context):
        """Owner Only => Forces remove guild data on MongoDB database"""

        guild_data = self.create_guild_data(guild=ctx.guild)

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_info")
                collection.delete_one({"_id": ctx.guild.id})
                collection.database.client.close()
                print(
                    f"GUILDS_INFO >> 'on_guild_remove' SUCCESS: O objeto com ID:{guild_data['_id']} da Guilda ID:{ctx.guild.id} foi REMOVIDO do database."
                )
        except Exception as e:
            print(
                f"on_guild_remove' ERROR: Não foi possível excluir o objeto ID:{ctx.guild.id} da Guilda ID:{ctx.guild.id}."
            )
            print(e)

    @commands.command(name="reset-data", hidden=True)
    @commands.is_owner()
    async def reset_data(self, ctx: commands.Context):
        """Owner Only => Forces reset guild data on MongoDB database"""

        await ctx.invoke(self.bot.get_command("delete-data"))
        await ctx.invoke(self.bot.get_command("insert-data"))


def setup(bot: commands.Bot):
    bot.add_cog(Guild_Database(bot))
