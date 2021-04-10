import asyncio
import json
import math
import os
import random
import sys
from pprint import pprint

import codes.paths as path
import discord
import dotenv
import requests
from discord.ext import commands, tasks
from discord.ext.commands import MissingPermissions, has_permissions
from discord.utils import *
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
CONNECT_STRING = os.environ.get("MONGODB_URI")
timeout_limit = 30

# TODO Add 'has_permissions' in commands


class BadWords(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def error_message(self, ctx: commands.Context, error):
        if isinstance(error, MissingPermissions):
            return f"Desculpe {ctx.author.mention}, você não tem permissão para fazer isso!"

    def _timeout_message(self, ctx: commands.Context):
        return f"Desculpe {ctx.author.mention}, parece que você demorou demais para informar o que foi solicitado... 😅"

    def _get_all_bad_words(self, collection, ctx: commands.Context):
        bad_words_list = collection.find_one({"_id": ctx.guild.id}, {"settings": {"bad_words": 1}})
        bad_words = " | ".join([word for word in bad_words_list["settings"]["bad_words"]])

        return bad_words

    # WORKING
    @commands.command(name="add-badwords")
    @has_permissions(manage_channels=True, manage_guild=True, manage_roles=True, manage_messages=True)
    async def add_badwords(self, ctx: commands.Context):
        """!add-badwords => Adiciona uma palavra/sentença à lista de proíbidas
        - É necessário ter permissões para gerenciar: canais, guildas, roles e mensagens
        """

        def check(message):
            return message.author == ctx.message.author

        menu_msg = await ctx.send(
            f"{ctx.author.mention}, informe as palavras que deseja adicionar a lista de 'Bad Words'\n"
            "*Para inserir mais de uma palavra, separe-as por vírgulas (,)*"
        )

        try:
            bad_words_message = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
            bad_words_str = bad_words_message.content.upper()
        except asyncio.TimeoutError:
            return await ctx.send(self._timeout_message(ctx))

        bad_words = [word.strip() for word in bad_words_str.split(",")]

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                collection.update_one(
                    {"_id": ctx.guild.id}, {"$addToSet": {"settings.bad_words": {"$each": bad_words}}}
                )
                end_msg = await ctx.send("As palavras foram **inseridas com sucesso** na lista de **'Bad Words'**")
        except Exception as e:
            await ctx.send(
                f"Sinto muito {ctx.author.mention}, houve um problema ao inserir as **Bad Words** no banco de dados."
                f"Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor em {path.dev_contact}."
            )
            print(
                f"COMMAND >> 'add-badwords' ERROR: Não foi possível inserir as palavras na lista de Bad Words da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

        await asyncio.sleep(3)
        await menu_msg.delete()
        await bad_words_message.delete()
        await end_msg.delete()

    @add_badwords.error
    async def add_badwords_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    # WORKING
    @commands.command(name="show-badwords")
    @has_permissions(manage_channels=True, manage_guild=True, manage_roles=True, manage_messages=True)
    async def show_badwords(self, ctx: commands.Context):
        """!show-badwords => Envia a lista com todas as palavras/sentenças proíbidas na DM
        - É necessário ter permissões para gerenciar: canais, guildas, roles e mensagens
        """

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
        except Exception as e:
            f"Sinto muito {ctx.author.mention}, houve um problema ao consultar as **Bad Words** no banco de dados."
            f"Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor em {path.dev_contact}."
            print(
                f"COMMAND >> 'badwords' ERROR: Não foi possível consultar as palavras na lista de Bad Words da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

        bad_words = self._get_all_bad_words(collection, ctx)
        await ctx.author.send(embed=discord.Embed(title=bad_words))

    @show_badwords.error
    async def show_badwords_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    # WORKING
    @commands.command(name="del-badwords")
    @has_permissions(manage_channels=True, manage_guild=True, manage_roles=True, manage_messages=True)
    async def del_badwords(self, ctx: commands.Context):
        """!del-badwords => Deleta uma palavra/sentença da lista de proíbidas
        - É necessário ter permissões para gerenciar: canais, guildas, roles e mensagens
        """

        def check(message):
            return message.author == ctx.message.author

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                bad_words = self._get_all_bad_words(collection, ctx)

            menu_msg = await ctx.send(
                "Abaixo estão listadas as palavras salvas. Informe quais deseja excluir:\n"
                "*Para inserir mais de uma palavra, separe-as por vírgulas (,)*"
            )
            show_msg = await ctx.send(embed=discord.Embed(title=bad_words))

            try:
                bad_words_to_delete_message = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
                bad_words_to_delete = bad_words_to_delete_message.content.upper()
            except asyncio.TimeoutError:
                return await ctx.send(self._timeout_message(ctx))

            bad_words_to_delete_list = [word.strip() for word in bad_words_to_delete.split(",")]

            try:
                query_result = collection.find_one_and_update(
                    {"_id": ctx.guild.id}, {"$pull": {"settings.bad_words": {"$in": bad_words_to_delete_list}}}
                )

                if query_result is not None:
                    end_msg = await ctx.send("As 'Bad Words' foram excluídas com sucesso! 👌")
                else:
                    end_msg = await ctx.send(
                        f"Hmmm... {ctx.author.mention}, parece que as palavras não existem na lista 🙃"
                    )

            except Exception as e:
                print(e)

            await asyncio.sleep(3)
            await menu_msg.delete()
            await show_msg.delete()
            await bad_words_to_delete.delete()
            await end_msg.delete()

        except Exception as e:
            await ctx.send(
                f"Sinto muito {ctx.author.mention}, houve um problema ao consultar as **Bad Words** no banco de dados"
                f"Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor em {path.dev_contact}."
            )
            print(
                f"COMMAND >> 'del-badwords' ERROR: Não foi possível consultar as palavras na lista de Bad Words da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

    @del_badwords.error
    async def del_badwords_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    # WORKING
    @commands.command(name="reset-badwords")
    @has_permissions(manage_channels=True, manage_guild=True, manage_roles=True, manage_messages=True)
    async def reset_badwords(self, ctx: commands.Context):
        """!reset-badwords => Retorna a lista de palavras/sentenças proíbidas ao seu valor padrão
        - É necessário ter permissões para gerenciar: canais, guildas, roles e mensagens
        """

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")

                collection.update({"_id": ctx.guild.id}, {"$set": {"settings.bad_words": []}})
                await ctx.send("As 'Bad Words' foram resetadas com sucesso! 👌")

        except Exception as e:
            await ctx.send(
                f"Sinto muito {ctx.author.mention}, houve um problema ao consultar as **Bad Words** no banco de dados"
                f"Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor em {path.dev_contact}."
            )
            print(
                f"COMMAND >> 'reset-badwords' ERROR: Não foi possível resetar as palavras na lista de Bad Words da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

    @reset_badwords.error
    async def reset_badwords_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    # WORKING
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        message_uppercase = message.content.upper()
        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")

                query_result = collection.find_one({"_id": message.guild.id}, {"settings": {"bad_words": 1}})
                bad_words = query_result["settings"]["bad_words"]

                for word in bad_words:
                    if message_uppercase.count(word) > 0:
                        await message.channel.purge(limit=1)
                        msg = await message.channel.send(f"**Mensagem deletada** [{message.author.mention}].")
                        await asyncio.sleep(5)
                        await msg.delete()
                        break

        except Exception as e:
            print(e)


def setup(bot: commands.Bot):
    bot.add_cog(BadWords(bot))
