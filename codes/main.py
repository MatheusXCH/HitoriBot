#PyBOT - Author: @Matheus Xavier
#
#

import os, sys, traceback, discord, logging, time, asyncio
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext.commands import Bot, guild_only
from discord import Member
from pretty_help import PrettyHelp
from pretty_help import Navigation

sys.path.append("D:\\python-codes\\Discordzada") #Config the PYTHONPATH to import "codes.settings" without warnings
import codes.settings as st #Get the globals from Settings

logging.basicConfig(level=logging.INFO)
clear = lambda: os.system('cls')

#Carrega todas as intents para uso do Bot
intents=intents=discord.Intents.all()
intents.members = True
intents.reactions = True
intents.voice_states = True

#Carrega os Tokens necessários
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PREFIX = '!'

startup_extensions = [
                    "cogs.administrator",
                    "cogs.messages",
                    "cogs.stickers",
                    "cogs.management",
                    "cogs.minigames",
                    "cogs.myanimelist",
                    "cogs.howlongtobeat",
                    "cogs.leagueoflegends",
                    "cogs.storesteam",
                    "cogs.audioplayer"
                    ]

#bot = commands.Bot(command_prefix=PREFIX, help_command=None)
custom_pretty_help = PrettyHelp(
    active_time = 60,
    color = discord.Color(0xa632a8),
    index_title = f'Módulos',
    ending_note = f'Help - PyBOT',
    sort_commands = True,
    show_index = True,
)

bot = commands.Bot(command_prefix=PREFIX, help_command = custom_pretty_help)

#Evento que dispara quando o bot conecta
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
        f'\n--> ESTAMOS ONLINE!!!\n'
        f'{bot.user} conectou-se com sucesso ao Discord!\n'
        f'\n\nConectado aos seguintes servidores:\n'
    )
    for g in guild:
            nickname = g.get_member(bot.user.id)
            nickname = nickname.nick
            print(f'{g.name} (id: {g.id}) como {nickname}')
            
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "o Yuki no banho"))

#Carrega as extensões (Cogs)
if __name__ == "__main__":
    loading_error_flag = 0
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print(f'Failed to load extension {extension}\n{exc}')
            loading_error_flag = 1

    if(not loading_error_flag):
        bot.run(TOKEN, bot = True, reconnect = True)
    else:
        print('\n\nLoading_Extension_Error_Flag = 1\n This CMD will close in 5 minutes')
        time.sleep(300)