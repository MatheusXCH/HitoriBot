import os, discord, codecs
from discord.ext import commands

import codes.settings as st #Get the globals from Settings


# Módulo: Rules
#     - Lista as regras do servidor
#     - As regras estão disponíveis para edição via arquivo .txt, localizado no diretório '/misc/regras/rules.txt'
class Rules(commands.Cog):
    """
    """
    
    def __init__(self, bot):
        self.bot = bot
    
#   !rules 
#         - Lista as regras do servidor!
    @commands.command(name='rules')
    async def rules(self, ctx):
        """"""
        
        with codecs.open(st.rule_path + 'rules.txt', 'r', encoding='utf8') as f:
            text = f.read()
        
        embed = discord.Embed(
            title = f'__**Regras do Servidor**__',
            colour = discord.Colour(0xe82e2e),
            description = "Leia as Regras atentamente"
        )
        
        embed.add_field(name='Regras', value=text, inline=False)
        file = discord.File(st.image_path + 'RH.png', filename='RH.png')
        embed.set_image(url='attachment://RH.png')
        await ctx.send(file=file, embed=embed)
        
def setup(bot):
    bot.add_cog(Rules(bot))