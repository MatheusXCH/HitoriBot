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

# # # Módulo: Rules
# # - Fornece aos moderadores dos servidores um conjunto de comandos para gerenciar e disponibilizar as regras 
# # do servidor
# # - Os comandos permitem adicionar/remover/mostrar as regras, dadas as restrições de permissões impostas por 
# # cada tipo de comando
# # - Cada servidor possuí sua própria instância das playlists, administrado via database

# # # Utiliza:
# # - Discord.py API (by Rapptz on: https://github.com/Rapptz/discord.py)
# # - MongoDB Python Driver [pymongo] (by mongodb on: https://github.com/mongodb/mongo-python-driver)

load_dotenv()
CONNECT_STRING = os.environ.get("MONGODB_URI")
timeout_limit = 60


class Rules(commands.Cog):
    """Fornece comandos para administrar as regras do servidor"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def error_message(self, ctx: commands.Context, error):
        if isinstance(error, MissingPermissions):
            return f"Desculpe {ctx.author.mention}, você não tem permissão para fazer isso!"

    def _timeout_message(self, ctx: commands.Context):
        return f"Desculpe {ctx.author.mention}, parece que você demorou demais para informar o que foi solicitado... 😅"

    @commands.command(name="add-rules")
    @has_permissions(administrator=True)
    async def add_rules(self, ctx: commands.Context):
        """!add-rules => Adiciona um texto para as regras do servidor
        - É preciso ser **administrador**
        """

        def check(message):
            return message.author == ctx.message.author

        await ctx.send(f"{ctx.author.mention}, informe o texto de regras para o servidor!")

        try:
            rules_text_message = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
            rules_text = rules_text_message.content
        except asyncio.TimeoutError:
            return await ctx.send(self._timeout_message(ctx))

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                collection.update_one({"_id": ctx.guild.id}, {"$set": {"settings.rules": {"rules_text": rules_text}}})
                await ctx.send(f"As regras de **{ctx.guild.name}** foram salvas 💾")
        except Exception as e:
            await ctx.send(
                f"Sinto muito {ctx.author.mention}, houve um problema ao salvar as **regras** no banco de dados."
                f"Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor em {path.dev_contact}."
            )
            print(
                f"COMMAND >> 'add-rules' ERROR: Não foi possível salvar as Regras da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

    @add_rules.error
    async def add_rules_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    @commands.command(name="del-rules")
    @has_permissions(administrator=True)
    async def del_rules(self, ctx: commands.Context):
        """!del-rules => Deleta as regras atuais do servidor
        - É preciso ser **administrador**
        """

        def check(message):
            return message.author == ctx.message.author

        def validate_confirm_msg(confirm_msg):
            if confirm_msg.upper() != "SIM" and confirm_msg.upper() != "S" and confirm_msg.upper() != "Y":
                if confirm_msg.upper() != "NÃO" and confirm_msg.upper() != "NAO" and confirm_msg.upper() != "N":
                    return False
            return True

        await ctx.send(f"{ctx.author.mention}, tem certeza que deseja excluir as regras do servidor?(S/N)")

        try:
            confirm_msg_message = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
            confirm_msg = confirm_msg_message.content
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
            f"Sinto muito {ctx.author.mention}, houve um problema ao excluir as **regras** no banco de dados."
            f"Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor em {path.dev_contact}."
            print(
                f"COMMAND >> 'del-rules' ERROR: Não foi possível salvar as Regras da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

    @del_rules.error
    async def del_rules_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    @commands.command(name="rules")
    async def rules(self, ctx: commands.Context):
        """!rules => Envia as regras do servidor na DM do usuário"""

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                document = collection.find_one({"_id": ctx.guild.id}, {"settings.rules.rules_text": 1})
                rules_text = document["settings"]["rules"]["rules_text"]

        except Exception as e:
            await ctx.send(
                f"Sinto muito {ctx.author.mention}, houve um problema ao recupear as **regras** no banco de dados."
                f"Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor em {path.dev_contact}."
            )
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
        file = discord.File(path.image_path + "RH.png", filename="RH.png")
        embed.set_image(url="attachment://RH.png")
        await ctx.author.send(embed=embed, file=file)


def setup(bot):
    bot.add_cog(Rules(bot))
