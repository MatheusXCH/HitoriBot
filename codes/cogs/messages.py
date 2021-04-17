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

# # # Módulo: Messages
# # - Contém alguns comandos simples, os quais consistem apenas de algumas mensagens que são exibidas pelo Bot

# # # Utiliza:
# # - Discord.py API (by Rapptz on: https://github.com/Rapptz/discord.py)

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
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(
            title=f"Saudações e seja muito bem-vindo à Guilda **{member.guild.name}**, **{member.mention}**!!!",
            description=f"Eu sou {self.bot.nick}, responsável por gerenciar algumas coisas aqui e ali no servidor.\n"
            "Não esqueça de consultar as Regras e Diretrizes da Guilda (utilize `!rules` no servidor para isso), "
            "bem como de consultar no que posso te ajudar com o comando `!help` 😎",
        )

        await member.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        embed = discord.Embed(
            title=f"SAUDAÇÕES À TODOS! 🖖👽\nEu me chamo {self.bot.user.name} e sou o novo Bot do servidor 🤖",
            description=f"Sou um Bot de propósito geral, então... Faço um pouco de tudo, {guild.roles[0]}!",
        )

        embed.add_field(
            name="Dentre as coisas que posso fazer, estão: ",
            value=(
                "🔨 Gerenciar o servidor (Roles, Kick, Palavras proibidas...)\n"
                "🎲 Tomar decisões através de dado, cara ou coroa ou 'escolha um'\n"
                "📖 Consultar informações sobre animes, mangás e personagens!\n"
                "🎮 Consultar informações sobre jogos na Steam em tempo real!\n"
                "⏳ Obter o tempo estimado para terminar um game! (via HowLongToBeat)\n"
                "🤑 Informar os usuários sobre Jogos/DLCs grátis para PC!\n"
                "🧙‍♂️ Informações sobre partidas ao vivo de League of Legends, bem como detalhes dos invocadores!\n"
                "🚀 ... e por aí vai!\n\n"
                "Para maiores detalhes de minhas funcionalidades e como configurá-las, acesse a [documentação](https://github.com/MatheusXCH/Discordzada/wiki).\n"
                "Utilize o `!help` para informações acerca do uso dos comandos.\n\n"
                f"Caso encontrem bugs, por favor, entrem em contato com meu criador pelo {path.dev_contact}."
            ),
            inline=False,
        )

        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(embed=embed)
                break


def setup(bot):
    bot.add_cog(Messages(bot))
