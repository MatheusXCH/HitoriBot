import os, discord, codecs, random, asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

import codes.settings as st #Get the globals from Settings

# Módulo: Messages
#     - Contém alguns comandos simples, os quais consitem apenas de algumas mensagens que são exibidas pelo PyBOT
class Messages(commands.Cog):
    """Módulo que contém alguns comandos simples, que retornam apenas mensagens de texto"""
    
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='familia')
    async def familia(self, ctx):
        """!familia => Pergunta pro BRTT se isso é uma família"""

        response = (f'Isso aqui não é uma família, é um time!\n' + 
                    f'Se vai deixar morrer, teu irmão???\n\n' + 
                    f'*CLARO QUE VAI NÉ, PORRA!*'
                    )
        familia_embed = discord.Embed(description = response)
        await ctx.send(embed = familia_embed)
    
    
    @commands.command(name='playlist')
    async def playlist(self, ctx):
        """!playlist => Lista as playlists feitas para o Servidor"""

        embed = discord.Embed(
            title=':notes: **Playlists do Servidor** :notes:',
            colour= discord.Colour(0x32a852),
            description='Aqui estão os **links das playlists** elaboradas para este servidor:',
        )
        embed.add_field(name=':play_pause: Animezada:', value= 'https://www.youtube.com/playlist?list=PLlOJh8D_rbtt3u1U3XScS8iL-EvNOf_ap', inline = False)
        embed.add_field(name=':play_pause: Biruta:', value= 'https://www.youtube.com/playlist?list=PLlOJh8D_rbtsYBFZWDPCqG4gqXSSkSj_m', inline = False)
        embed.add_field(name=':play_pause: É o Ericks:', value= 'https://www.youtube.com/playlist?list=PLUou7E06dGsYeCeFykeBHCG7bXgx_VC4e', inline = False)
        embed.add_field(name=':play_pause: Só o HYPE:', value = 'https://www.youtube.com/playlist?list=PLeOu0isxutGI693o9yg6d3BGSUbPPgU4X', inline = False)

        message = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await message.delete()
    
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener - Diz ao usuário que não é pra dirigir a palavra ao BOT"""
        
        if self.bot.user.mentioned_in(message) and message.author != self.bot.user and not message.mention_everyone:
            await message.channel.send(f'Aí {message.author.mention}, não me dirige a palavra não. Faz favor!')


def setup(bot):
    bot.add_cog(Messages(bot))