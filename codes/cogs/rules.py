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
from discord.utils import *
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
CONNECT_STRING = os.environ.get("MONGODB_URI")
timeout_limit = 15


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _timeout_message(self, ctx: commands.Context):
        return f"Desculpe {ctx.author.mention}, parece que você demorou demais para informar o que foi solicitado... 😅"

    # TODO: COMMAND >> 'add-rules'
    # TEST
    @commands.command(name="add-rules")
    async def add_rules(self, ctx: commands.Context):
        def check(message):
            return message.author == ctx.message.author

        await ctx.send(f"{ctx.author.mention}, informe o texto de regras para o servidor!")

        try:
            rules_text = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
        except asyncio.TimeoutError:
            return await ctx.send(self._timeout_message(ctx))

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                collection.update_one({"_id": ctx.guild.id}, {"$set": {"settings.rules": {"rules_text": rules_text}}})
                await ctx.send(f"As regras de **{ctx.guild.name}** foram salvas 💾")
        except Exception as e:
            f"""Sinto muito {ctx.author.mention}, houve um problema ao salvar as **regras** no banco de dados.
            Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor em CONTATO."""
            print(
                f"COMMAND >> 'add-rules' ERROR: Não foi possível salvar as Regras da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

    # TODO COMMAND >> 'del-rules'
    # TEST
    @commands.command(name="del-rules")
    async def del_rules(self, ctx: commands.Context):
        def check(message):
            return message.author == ctx.message.author

        def validate_confirm_msg(confirm_msg):
            if confirm_msg.upper() != "SIM" and confirm_msg.upper() != "S" and confirm_msg.upper() != "Y":
                if confirm_msg.upper() != "NÃO" and confirm_msg.upper() != "NAO" and confirm_msg.upper() != "N":
                    return False
            return True

        await ctx.send(f"{ctx.author.mention}, tem certeza que deseja excluir as regras do servidor?(S/N)")

        try:
            confirm_msg = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
        except asyncio.Timeout:
            return await ctx.send(self._timeout_message(ctx))

        if not validate_confirm_msg(confirm_msg):
            return await ctx.send(
                f"Desculpe {ctx.author.mention}, essa opção é inválida! Tente utilizar o comando novamente!"
            )

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                collection.update(
                    {"_id": ctx.guild.id},
                    {
                        "$set": {
                            "settings.rules.rules_text": "O texto passado ao bot pelo comando '!add-rules' aparecerá aqui!"
                        }
                    },
                )
            await ctx.send(f"As regras de **{ctx.guild.name}** foram excluídas ❌")
        except Exception as e:
            f"""Sinto muito {ctx.author.mention}, houve um problema ao excluir as **regras** no banco de dados.
            Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor em CONTATO."""
            print(
                f"COMMAND >> 'del-rules' ERROR: Não foi possível salvar as Regras da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

    # # # NOTE: Need to add a default thumb at 'settings_database.py/create_settings_data' function
    # TODO COMMAND >> 'add-rules-thumb'
    # TODO COMMAND >> 'del-rules-thumb'

    # TODO COMMAND >> 'edit-rules' (???)

    # TODO COMMAND >> 'rules' -> Show Rules
    # TEST
    @commands.command(name="rules")
    async def rules(self, ctx: commands.Context):
        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                document = collection.find_one({"_id": ctx.guild.id}, {"settings.rules.rules_text": 1})
                rules_text = document["settings"]["rules"]["rules_text"]

                # TODO Get the Thumb here
        except Exception as e:
            f"""Sinto muito {ctx.author.mention}, houve um problema ao recupear as **regras** no banco de dados.
            Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor em CONTATO."""
            print(
                f"COMMAND >> 'rules' ERROR: Não foi possível recuperar as Regras da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

        embed = discord.Embed(
            title=f"__**Regras e Diretrizes do Servidor {ctx.guild.name}**__",
            colour=discord.Colour(0xE82E2E),
            description="Leia as Regras e Diretrizes atentamente",
        )
        embed.add_field(name="**Regras**", value=rules_text, inline=False)
        # TODO Add Thumb/Image of the rules embed
        await ctx.send(embed=embed, file=None)

    # TODO Listener >> 'on_member_join(member)'
    # -> Send Rules on member DM or Ask him to use '!rules'


def setup(bot):
    bot.add_cog(Rules(bot))
