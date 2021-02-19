import os, discord, codecs, time
from discord.ext import commands
from discord import Colour

import codes.settings as st #Get the globals from Settings

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Help (Command) - Mostra o custom help do Servidor    
    @commands.command(name='help')
    async def help(self, ctx):
        with codecs.open(st.help_path + 'gerenciamento.txt', 'r', encoding='utf8') as f:
            gerenciamento = f.read()
        with codecs.open(st.help_path + 'mensagens.txt', 'r', encoding='utf8') as f:
            mensagens = f.read()
        with codecs.open(st.help_path + 'minigames.txt', 'r', encoding='utf8') as f:
            minigames = f.read()
        with codecs.open(st.help_path + 'stickers.txt', 'r', encoding='utf8') as f:
            stickers = f.read()
        
        embed = discord.Embed(
            title = f'__**MANUAL DE USO**__',
            colour = discord.Colour(0x2ee8df),
            description = "Lista de comandos disponíveis no BOT\n OBS: * indica argumento opcional")
        
        embed.add_field(name=":arrow_right: **GERENCIAMENTO**", value = gerenciamento, inline = True)
        embed.add_field(name=":arrow_right: **MENSAGENS**", value = mensagens, inline = True)
        embed.add_field(name=":arrow_right: **MINIGAMES**", value = minigames, inline = True)
        embed.add_field(name=":arrow_right: **STICKERS**", value = stickers, inline = True)
        
        await ctx.send(content = None, embed = embed)

def setup(bot):
    bot.add_cog(Help(bot))