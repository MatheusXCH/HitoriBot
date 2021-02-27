import os, discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

import codes.settings as st #Get the globals from Settings

class Messages(commands.Cog):
    """Módulo: Messages
    
        - Contém alguns comandos simples, os quais consitem apenas de algumas mensagens que são exibidas pelo PyBOT
    """

    def __init__(self, bot):
        self.bot = bot
      
    @commands.command(name='familia')
    async def familia(self, ctx):
        """!familia 
        - Pergunta pro BRTT se isso aqui é uma família"""
        
        response = (f'Isso aqui não é uma família, é um time!\n' + 
                    f'Se vai deixar morrer, teu irmão???\n\n' + 
                    f'*CLARO QUE VAI NÉ, PORRA!*'
                   )
        familia_embed = discord.Embed(description = response)
        await ctx.send(embed = familia_embed)
    
    @commands.command(name='playlist')
    async def playlist(self, ctx):
        """!playlist 
        - Envia um Embed com todas as Playlists feitas para o Servidor"""
        
        embed = discord.Embed(
            title=':notes: **Playlists do Servidor** :notes:',
            colour= discord.Colour(0x32a852),
            description='Aqui estão os **links das playlists** elaboradas para este servidor:',
        )
        embed.add_field(name=':play_pause: Animezada:', value= 'https://www.youtube.com/playlist?list=PLlOJh8D_rbtt3u1U3XScS8iL-EvNOf_ap', inline=True)
        embed.add_field(name=':play_pause: Biruta:', value= 'https://www.youtube.com/playlist?list=PLlOJh8D_rbtsYBFZWDPCqG4gqXSSkSj_m', inline=True)
        embed.add_field(name=':play_pause: É o Ericks:', value= 'https://www.youtube.com/playlist?list=PLUou7E06dGsYeCeFykeBHCG7bXgx_VC4e', inline=True)
        
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Messages(bot))