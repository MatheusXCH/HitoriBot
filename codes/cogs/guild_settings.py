import asyncio
import os

# Get the globals from Settings
import codes.settings as st
import discord
import dotenv
import json
import pprint
import inspect
from pprint import pprint
from discord.ext import commands
from discord.ext.commands import MissingPermissions, has_permissions
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
CONNECT_STRING = os.environ.get("MONGODB_URI")


class Guild_Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def freegames_collection(self):
        client = MongoClient(CONNECT_STRING)
        db = client.get_database("discordzada")
        collection = db.get_collection("free-game-findings-channels")
        return collection

    def guilds_settings_collection(self):
        client = MongoClient(CONNECT_STRING)
        db = client.get_database("discordzada")
        collection = db.get_collection("guilds_settings")
        return collection

    def get_text_channel_data(self, text_channel: discord.TextChannel):
        try:
            category = text_channel.category.name
        except:
            category = None

        text_channel_data = {
            "channel_id": text_channel.id,
            "channel_name": text_channel.name,
            "channel_category": category,
        }

        return text_channel_data

    def get_voice_channel_data(self, voice_channel: discord.VoiceChannel):
        try:
            category = voice_channel.category.name
        except:
            category = None

        voice_channel_data = {
            "channel_id": voice_channel.id,
            "channel_name": voice_channel.name,
            "channel_category": category,
        }

        return voice_channel_data

    def get_role_data(self, role: discord.Role):
        roles_data = {
            "role_name": role.name,
            "role_id": role.id,
            "permissions": [perm[0] for perm in role.permissions if perm[1]],
        }

        return roles_data

    def get_member_data(self, member: discord.Member):
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

    def get_config_data(self, guild: discord.Guild):
        prefix = "!"
        free_game = {"channel_id": None, "channel_name": None}
        config_data = {"prefix": prefix, "free_game": free_game}

        return config_data

    def create_guild_data(self, guild: discord.Guild):
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
                "config": self.get_config_data(guild),
            },
        }

        return guild_data

    # WORKING
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        guild_data = self.create_guild_data(guild)

        try:
            collection = self.guilds_settings_collection()
            collection.insert_one(guild_data)
            collection.database.client.close()
            print(f"'on_guild_join' SUCCESS: A Guilda com ID:{guild_data['_id']} foi INSERIDO no database")
        except:
            print(f"'on_guild_join' ERROR: Houve um erro ao inserir a Guilda ID:{guild.id} no database.")

    # WORKING
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        guild_data = self.create_guild_data(guild)

        try:
            collection = self.guilds_settings_collection()
            collection.delete_one({"_id": guild.id})
            collection.database.client.close()
            print(f"'on_guild_remove' SUCCESS: A Guilda ID:{guild_data['_id']} foi EXCLUÍDO do database")
        except:
            print(f"on_guild_remove' ERROR: Houve um erro ao excluir a Guilda ID:{guild.id} do database")

    # WORKING
    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):

        try:
            collection = self.guilds_settings_collection()
            collection.update_one(
                {"_id": after.id}, {"$set": {"guild.guild_name": after.name, "guild.guild_id": after.id}}
            )
            collection.database.client.close()
            print(f"'on_guild_update' SUCCESS: A Guilda ID:{after.id} foi ATUALIZADA no database")
        except Exception as e:
            print(f"'on_guild_update' ERROR: Houve um erro ao atualizar a Guilda ID:{after.id}")
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        guild = channel.guild

        if str(channel.type) == "text":
            try:
                collection = self.guilds_settings_collection()
                text_channel_data = self.get_text_channel_data(channel)
                collection.update_one(
                    {"_id": guild.id},
                    {"$push": {"guild.channels_info.text_channels": text_channel_data}},
                )
                collection.database.client.close()
                print(
                    f"'on_guild_channel_create' SUCCESS: O Canal de Texto ID:{text_channel_data['channel_id']} foi INSERIDO no database"
                )
            except Exception as e:
                print(
                    f"'on_guild_channel_create' ERROR: Houve um erro ao inserir o Canal de Texto de ID: {text_channel_data['channel_id']}"
                )
                print(e)

        elif str(channel.type) == "voice":
            try:
                collection = self.guilds_settings_collection()
                voice_channel_data = self.get_voice_channel_data(channel)
                collection.update_one(
                    {"_id": guild.id},
                    {"$push": {"guild.channels_info.voice_channels": voice_channel_data}},
                )
                collection.database.client.close()
                print(
                    f"'on_guild_channel_create' SUCCESS: O Canal de Voz ID:{voice_channel_data['channel_id']} foi INSERIDO no database"
                )
            except Exception as e:
                print(
                    f"'on_guild_channel_create' ERROR: Houve um erro ao inserir o Canal de Voz de ID: {voice_channel_data['channel_id']}"
                )
                print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        guild = channel.guild

        if str(channel.type) == "text":
            try:
                collection = self.guilds_settings_collection()
                text_channel_data = self.get_text_channel_data(channel)
                collection.update_one(
                    {"_id": guild.id},
                    {"$pull": {"guild.channels_info.text_channels": text_channel_data}},
                )
                collection.database.client.close()
                print(
                    f"'on_guild_channel_delete' SUCCESS: O Canal de Texto ID:{text_channel_data['channel_id']} foi REMOVIDO no database"
                )
            except Exception as e:
                print(
                    f"'on_guild_channel_delete' ERROR: Houve um erro ao remover o Canal de Texto ID:{text_channel_data['channel_id']}"
                )
                print(e)

        elif str(channel.type) == "voice":
            try:
                collection = self.guilds_settings_collection()
                voice_channel_data = self.get_voice_channel_data(channel)
                collection.update_one(
                    {"_id": guild.id},
                    {"$pull": {"guild.channels_info.voice_channels": voice_channel_data}},
                )
                collection.database.client.close()
                print(
                    f"'on_guild_channel_delete' SUCCESS: O Canal de Voz ID:{voice_channel_data['channel_id']} foi REMOVIDO no database"
                )
            except Exception as e:
                print(
                    f"'on_guild_channel_delete' ERROR: Houve um erro ao remover o Canal de Voz ID:{voice_channel_data['channel_id']}"
                )
                print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        guild = after.guild

        if str(after.type) == "text":
            try:
                collection = self.guilds_settings_collection()
                text_channel_after_data = self.get_text_channel_data(after)
                collection.update_one(
                    {"_id": guild.id, "guild.channels_info.text_channels.channel_id": after.id},
                    {"$set": {"guild.channels_info.text_channels.$": text_channel_after_data}},
                )
                collection.database.client.close()
                print(
                    f"'on_guild_channel_update' SUCCESS: O Canal de Texto ID:{text_channel_after_data['channel_id']} foi ATUALIZADO no database"
                )
            except Exception as e:
                print(
                    f"'on_guild_channel_update' ERROR: Houve um erro ao atualizar o Canal de Texto ID:{text_channel_after_data['channel_id']}"
                )
                print(e)
        elif str(after.type) == "voice":
            try:
                collection = self.guilds_settings_collection()
                voice_channel_after_data = self.get_voice_channel_data(after)
                collection.update_one(
                    {"_id": guild.id, "guild.channels_info.voice_channels.channel_id": after.id},
                    {"$set": {"guild.channels_info.voice_channels.$": voice_channel_after_data}},
                )
                collection.database.client.close()
                print(
                    f"'on_guild_channel_update' SUCCESS: O Canal de Voz ID:{voice_channel_after_data['channel_id']} foi ATUALIZADO no database"
                )
            except Exception as e:
                print(
                    f"'on_guild_channel_update' ERROR: Houve um erro ao atualizar o Canal de Voz ID:{voice_channel_after_data['channel_id']}"
                )
                print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        guild = role.guild
        role_data = self.get_role_data(role)
        pprint(role_data)
        try:
            collection = self.guilds_settings_collection()
            collection.update_one({"_id": guild.id}, {"$push": {"guild.roles_info": role_data}})
            collection.database.client.close()
            print(f"'on_guild_role_create' SUCCESS: A role de ID:{role_data['role_id']} foi INSERIDA no database")
        except Exception as e:
            print(f"'on_guild_role_create' ERROR: Houve um erro ao inserir a role de ID:{role_data['role_id']}")
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        guild = role.guild
        role_data = self.get_role_data(role)

        try:
            collection = self.guilds_settings_collection()
            collection.update_one({"_id": guild.id}, {"$pull": {"guild.roles_info": role_data}})
            collection.database.client.close()
            print(f"'on_guild_role_delete' SUCCESS: A role de ID:{role_data['role_id']} foi REMOVIDA no database")
        except Exception as e:
            print(f"'on_guild_role_delete' ERROR: Houve um erro ao remover a role de ID:{role_data['role_id']}")
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        guild = after.guild
        role_data = self.get_role_data(after)

        try:
            collection = self.guilds_settings_collection()
            collection.update_one(
                {"_id": guild.id, "guild.roles_info.role_id": after.id}, {"$set": {"guild.roles_info.$": role_data}}
            )
            collection.database.client.close()
            print(f"'on_guild_role_update' SUCCESS: A role de ID:{role_data['role_id']} foi ATUALIZADA no database")
        except Exception as e:
            print(f"'on_guild_role_update' ERROR: Houve um erro ao atualizar a role de ID:{role_data['role_id']}")
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        member_data = self.get_member_data(member)

        try:
            collection = self.guilds_settings_collection()
            collection.update_one({"_id": guild.id}, {"$inc": {"guild.members_info.members_count": 1}})
            collection.update_one({"_id": guild.id}, {"$push": {"guild.members_info.members": member_data}})
            collection.database.client.close()
            print(
                f"'on_member_join' SUCCESS: Um novo membro de ID:{member_data['member_id']} foi INSERIDO no database"
            )
        except Exception as e:
            print(
                f"'on_member_join' ERROR: Houve um erro ao inserir um novo membro no documento de ID:{member_data['member_id']} no database"
            )
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        member_data = self.get_member_data(member)

        try:
            collection = self.guilds_settings_collection()
            collection.update_one({"_id": guild.id}, {"$inc": {"guild.members_info.members_count": -1}})
            collection.update_one({"_id": guild.id}, {"$pull": {"guild.members_info.members": member_data}})
            collection.database.client.close()
            print(f"'on_member_remove' SUCCESS: Um membro de ID:{member_data['member_id']} foi REMOVIDO do database")
        except Exception as e:
            print(
                f"'on_member_remove' ERROR: Houve um erro ao remover um membro do documento de ID:{member_data['member_id']} no database"
            )
            print(e)

    # WORKING
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        guild = after.guild
        member_after_data = self.get_member_data(after)

        try:
            collection = self.guilds_settings_collection()
            collection.update_one(
                {"_id": guild.id, "guild.members_info.members.member_id": after.id},
                {"$set": {"guild.members_info.members.$": member_after_data}},
            )
            collection.database.client.close()
            print(f"'on_member_update' SUCCESS: O membro de ID:{member_after_data['member_id']} foi ATUALIZADO!")
        except Exception as e:
            print(
                f"'on_member_update' ERROR: Houve um erro ao atualizar o membro de ID:{member_after_data['member_id']}!"
            )
            print(e)

    # TODO Elaborar uma task que, exporadicamente, atualiza TODAS as informações de TODAS as guildas cadastradas no banco
    # TODO 'all_guilds_update'

    # # Comandos abaixo são, pelo menos inicialmente, para fins de TEST e DEBUG
    #
    #
    #
    #
    #
    #
    #
    #

    @commands.command(name="insert-data", hidden=True)
    async def insert_data(self, ctx: commands.Context):
        guild_data = self.create_guild_data(guild=ctx.guild)

        with open("guild_config.json", "w") as outfile:
            json.dump(guild_data, outfile, indent=4, default=str)

        try:
            collection = self.guilds_settings_collection()
            collection.insert_one(guild_data)
            collection.database.client.close()
            print(f"'on_guild_join' SUCCESS: O objeto com ID:{guild_data['_id']} foi inserido no database")
        except Exception as e:
            print(f"'on_guild_join' ERROR: Houve um erro ao inserir o objeto ID:{ctx.guild.id} no database")
            print(e)

    @commands.command(name="delete-data", hidden=True)
    async def delete_data(self, ctx: commands.Context):
        guild_data = self.create_guild_data(guild=ctx.guild)

        try:
            collection = self.guilds_settings_collection()
            collection.delete_one({"_id": ctx.guild.id})
            collection.database.client.close()
            print(
                f"'on_guild_remove' SUCCESS: O objeto com ID:{guild_data['_id']} foi excluído com sucesso do database"
            )
        except Exception as e:
            print(f"on_guild_remove' ERROR: Houve um erro ao excluir o objeto ID:{ctx.guild.id} do database")
            print(e)

    @commands.command(name="reset-data", hidden=True)
    async def reset_data(self, ctx: commands.Context):
        await ctx.invoke(self.bot.get_command("delete-data"))
        await ctx.invoke(self.bot.get_command("insert-data"))

    @commands.command(name="get-data", hidden=True)
    async def get_data(self, ctx: commands.Context):
        with open("guild_config.json", "r") as json_file:
            data = json.load(json_file)
            pprint(data)


def setup(bot: commands.Bot):
    bot.add_cog(Guild_Settings(bot))