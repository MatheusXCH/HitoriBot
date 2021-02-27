import os, discord, codecs, time
from discord.ext import commands
from discord import Colour

import codes.settings as st #Get the globals from Settings

#TODO Melhorar o !HELP
class Help(commands.Cog):
    """Módulo: Help
    
        - Substituiu o !help padrão, adicionando informações sobre os comandos disponíveis para uso do PyBOT \\
        - Os comandos estão descritos nos arquivos .txt, disponíveis no diretório '/misc/help/*.txt'
    """
    def __init__(self, bot):
        self.bot = bot
  
    @commands.command(name='custom-help')
    async def help(self, ctx):
        """!help 
        - Substitui o help padrão por uma versão personalizada para o PyBOT
        """
        
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