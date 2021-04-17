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

        embed.set_thumbnail(
            url="https://lh3.googleusercontent.com/UjwwvH1Luh8ue76YXo9tlejaqxZ3vMGmf8C6t72XPfh0JqKc3cvzBwWXFTX02W9ku_TSWrxNQISXQ_o6I--TwATi4g-D6d1K_FLftWFmfQreEK95KiK1RXGV1S7aPRL86H35w5pPAyB12QAYjU2ZXQmvWjkKGdle2peESa05Ff9pCXj3RQD44-pIM8XmxksQMT7dILoJjAPKKntJZR82Aq4Wb-alZP-XSKc-PFESaKk_RnBIMx1YMsNbgZSTO1tnNAq9u1ci3jxgRXSip4VE12EKcnFbu1b1Lg9VhTSWeiA9PgPdLmjnKCbIEztybwwDp6In8wW_pfOZsg8zoxoNmOmJP0FzQRxD6A-gJrm5su-IXA-vnDE0PohLP5C3kdtPnsRThqyaQV8fMA-1SuCTjsr9ptsn-uIBhGBggFfapYdEhtl19wtsQ5JoYYB6tfpWtENbnTpfxvZv0LHcX5DPRFCRpiT49CAOvrzwjCYMA_qFMJ2ikeKZhFbwsdJ6P1l0SwAEyraqDoCmPzoswtl9D8y1S0F36qvTRESUUwofjDe3BGDvFqRODhHtlBL_be8Eq3AdDTfgeP1nv8WbrAbGyzt8IArYJTTg8hp6rx6q9o6m_a9uUdYTqbY5QzGgVLO5oekez33pVJ2A8tKPdkTa9y7D2FXicFOt4OGw2TH3UDUBGiV_PGUrAkIHhqP8dCDniNym2F87E2gXVzQkwTMnyyI=s977-no?authuser=0"
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
        embed.set_image(
            url="https://lh3.googleusercontent.com/XdUm4T1bQguPBtDyk_YbpekdOQwWAJ3M1TpILMTYXAXIqwa73Y-qDbpUnddRs_Ag-4QW1bNVlLWKUDpwsPVkh0kcjswDSKTMCEX350MFT0s4ZjJR2iL_jMaWSbfp_-ux27Y-jCF5y23uNupiflKOnjcyMGiZYfsFP3un3j62R0eNtm-rbUF4LD35avm5AOEBvMo4np-hVABCfBbSd9pIuI82-_p7byKuPndncZGWV2ET03yGJprOWSbzpAIow3ANrXC0vVKR1l2fULYq0evF9CZRn07-d9GNRBA-824H9r0gaZcoxRTCR08fkGyBoNOs7whYPCNeIy81hmySFUrLDcHI4mWb2bCWCJTV6R00Eyssnz27QnOAPtRBfTQgOTXk5y3RYTr9S6-EC1yujkWYJkOMqiKsr4LRrvZSf4vSpkI3-7Ik-ZS4CwN2o0TnuJlfr5RZNSD2XoJhNejRtqlGC7myfMiL5gK4eX6J7m-v2eHkdXSoc9RA6eZsp00z59BiUZVhZIx4bdCSZixk5iaW6ZKoQF-aMHso_qP5X9oK2dhUkerkDcHo6UuKZ1jD6fPXJL4H7uXO2SY5yybJmMC5YdMNeYH0GigclXehz5X6Lat9nzqC4tB0qgrn2HkzZhkF_ClXaF9ULuf0X7jypZ2jfAI8D_BUshuIxbYuTFfI1VOoSSAgOSC7DJjbDGOyBSNbUji9rzPcG-f1iGLMEMD0WZE=w1466-h977-no?authuser=0"
        )

        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(embed=embed)
                break


def setup(bot):
    bot.add_cog(Messages(bot))
