# PyBOT - Author: @Matheus Xavier
#
#

import asyncio
import logging
import os
import sys
import time
import traceback

import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot, MissingPermissions, guild_only, has_permissions
from dotenv import load_dotenv
from pretty_help import Navigation, PrettyHelp

import codes.paths as path

sys.path.append("D:\\python-codes\\Discordzada")  # Config the PYTHONPATH to import "codes.settings" without warnings
# Get the globals from Settings

logging.basicConfig(level=logging.INFO)


def clear():
    os.system("cls")


# Carrega todas as intents para uso do Bot
intents = intents = discord.Intents.all()
intents.members = True
intents.reactions = True
intents.voice_states = True

# Carrega os Tokens necessários
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
PREFIX = "!"

startup_extensions = [
    "cogs.administrator",
    "cogs.audioplayer",
    "cogs.bad_words",
    "cogs.freegame",
    "cogs.guild_database",
    "cogs.howlongtobeat",
    "cogs.leagueoflegends",
    "cogs.management",
    "cogs.messages",
    "cogs.minigames",
    "cogs.myanimelist",
    "cogs.playlist",
    "cogs.rules",
    "cogs.settings_database",
    "cogs.stickers",
    "cogs.storesteam",
]

# bot = commands.Bot(command_prefix=PREFIX, help_command=None)
custom_pretty_help = PrettyHelp(
    active_time=60,
    color=discord.Color(0xA632A8),
    index_title="Módulos",
    ending_note="Help - PyBOT",
    sort_commands=True,
    show_index=True,
)

bot = commands.Bot(command_prefix=PREFIX, help_command=custom_pretty_help, intents=intents, case_insensitive=True)

# Evento que dispara quando o bot conecta


@bot.event
async def on_ready():
    """On_Ready
    - Confirma que o Bot está online
    - Retorna a lista de Servidores aos quais o PyBOT está conectado
    - A lista contém:
        - Nome da Guilda
        - ID da Guilda
        - Apelido que o PyBOT possui no servidor
    """
    guild = []
    for g in bot.guilds:
        guild.append(g)

    clear()
    print(
        f"\n--> ESTAMOS ONLINE!!!\n"
        f"{bot.user} conectou-se com sucesso ao Discord!\n"
        f"\n\nConectado aos seguintes servidores:\n"
    )
    for g in guild:
        nickname = g.get_member(bot.user.id)
        nickname = nickname.nick
        print(f"{g.name} (id: {g.id}) como {nickname}")

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=" 👀"))


# Carrega as extensões (Cogs)
if __name__ == "__main__":
    loading_error_flag = 0
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print(f"Failed to load extension {extension}\n{exc}")
            loading_error_flag = 1

    if not loading_error_flag:
        bot.run(TOKEN, bot=True, reconnect=True)
    else:
        print("\n\nLoading_Extension_Error_Flag = 1\n This CMD will close in 5 minutes")
        time.sleep(300)
