import asyncio
import codecs
import os
import random

# Get the globals from Settings
import codes.paths as path
import discord
import dotenv
from discord.ext import commands
from discord.ext.commands import MissingPermissions, has_permissions
from pymongo import MongoClient
from dotenv import load_dotenv

# Módulo: Messages
#     - Contém alguns comandos simples, os quais consitem apenas de algumas mensagens que são exibidas pelo PyBOT

load_dotenv()
CONNECT_STRING = os.environ.get("MONGODB_URI")


class Messages(commands.Cog):
    """Módulo que contém alguns comandos simples, que retornam apenas mensagens de texto"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="say")
    async def say(self, ctx: commands.Context, *, text: str):
        """!say <text> => O Bot repete o que for passado para ele como <text>
        Passa um texto para o Bot repetir. A mensagem original enviada é deletada.
        """

        await ctx.message.delete()
        await ctx.send(text)

    @commands.command(name="familia")
    async def familia(self, ctx):
        """!familia => Pergunta pro BRTT se isso é uma família"""

        response = (
            "Isso aqui não é uma família, é um time!\n"
            + "Se vai deixar morrer, teu irmão???\n\n"
            + "*CLARO QUE VAI NÉ, PORRA!*"
        )
        familia_embed = discord.Embed(description=response)
        await ctx.send(embed=familia_embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listener - Diz ao usuário que não é pra dirigir a palavra ao BOT"""

        if self.bot.user.mentioned_in(message) and message.author != self.bot.user and not message.mention_everyone:
            await message.channel.send(f"Aí {message.author.mention}, não me dirige a palavra não. Faz favor!")


def setup(bot):
    bot.add_cog(Messages(bot))
