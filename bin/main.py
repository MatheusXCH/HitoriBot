#PyBOT - Author: @Matheus Xavier
import os, sys, traceback, discord, logging, time
from dotenv import load_dotenv
from discord.ext import commands
from discord import Member

logging.basicConfig(level=logging.INFO)
clear = lambda: os.system('cls')

#Carrega todas as intents para uso do Bot
intents=intents=discord.Intents.all()
intents.members = True

#Carrega os Tokens necessários
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

PREFIX = '!'

startup_extensions = ["messages",
                      "stickers",
                      "rules",
                      "dices",
                      "management",
                      "help"]

#Prefix = ! e Help Command personalizado
bot = commands.Bot(command_prefix=PREFIX, help_command=None)

#Evento que dispara quando o bot conecta
@bot.event
async def on_ready():
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
            
    await bot.change_presence(activity= discord.Game('no Bicho'))


#Daqui em diante estão os eventos (@bot.event)
#
#
#

#TODO Testar o On Member Join e On Member Remove   
@bot.command(pass_context=True) 
@bot.event
async def on_member_join(member):
    print(f"{member} has joined the server")
    await member.guild.send(f'Deem as boas-vindas a {member.display_name}, o mais novo membro do servidor!')
    await member.create_dm()
    await member.dm_channel.send(f'Seja bem vindo ao servidor, {member.display_name}')

@bot.command(pass_context=True) 
@bot.event
async def on_member_remove(member):
    print(f"{member} has left the server")
    await member.guild.send(f'{member.display_name} deixou o servidor!')      

#Função principal - Carrega as extensões
if __name__ == "__main__":
    loading_error_flag = 0
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
            loading_error_flag = 1

    if(not loading_error_flag):
        bot.run(TOKEN, bot = True, reconnect = True)
    else:
        print('\n\nLoading_Extension_Error_Flag = 1\n This CMD will close in 5 minutes')
        time.sleep(300)