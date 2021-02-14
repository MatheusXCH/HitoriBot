import os, discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

class Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    #Familia (Command) - Pergunta pro BrTT se isso aqui é uma família    
    @commands.command(name='familia')
    async def familia(self, ctx):
        response = '''Isso aqui não é uma família, é um time!
Se vai deixar morrer, teu irmão???

*CLARO QUE VAI NÉ, PORRA!*'''
        
        await ctx.send(response)
    
    
    #Playlist (Command) - Envia o link com todas as Playlists feitas para o Servidor
    @commands.command(name='playlist')
    async def playlist(self, ctx):
        embed = discord.Embed(
            title=':notes: **Playlists do Servidor** :notes:',
            colour= discord.Colour(0x32a852),
            description='Aqui estão os **links das playlists** elaboradas para este servidor:',
        )
        embed.add_field(name=':play_pause: Animezada:', value= 'https://www.youtube.com/playlist?list=PLlOJh8D_rbtt3u1U3XScS8iL-EvNOf_ap', inline=True)
        embed.add_field(name=':play_pause: Biruta:', value= 'https://www.youtube.com/playlist?list=PLlOJh8D_rbtsYBFZWDPCqG4gqXSSkSj_m', inline=True)
        
        await ctx.send(embed=embed)
    
    
    #Test (Command) - Comando feito exclusivamente para testes práticos
    @commands.command(name='test')
    @has_permissions(administrator=True)
    async def test(self, ctx):
        response = ":smile:"
        await ctx.send(response)
        
def setup(bot):
    bot.add_cog(Messages(bot))