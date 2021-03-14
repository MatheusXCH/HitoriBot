import os, discord
from discord.ext import commands

import codes.settings as st #Get the globals from Settings

# Módulo: Stickers
#     - Responsável por todos os comandos relacionados aos stickers disponibilizados pelo PyBOT
#     - Sempre que um dos comandos por chamado, o PyBOT responderá com o sticker (imagem) correspondente
#     - Todos os Stickers está disponível no diretório '/misc/stickers'
class Stickers(commands.Cog):
    """Módulo contendo todos os stickers disponíveis para uso"""
    
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='bebero')
    async def bebero(self, ctx):
        """!bebero"""        
        await ctx.send(file = discord.File(st.image_path + 'Bebero.png'))
    
    @commands.command(name='analise')
    async def analise(self, ctx):
        """!analise"""           
        await ctx.send(file = discord.File(st.image_path + 'Analise.png'))
    
    @commands.command(name='bença')
    async def bença(self, ctx):
        """!bença"""           
        await ctx.send(file = discord.File(st.image_path + 'Bença.png'))
    
    @commands.command(name='broxa')
    async def broxa(self, ctx):
        """!broxa"""           
        await ctx.send(file = discord.File(st.image_path + 'Broxa.png'))
    
    @commands.command(name='entendi')
    async def entendi(self, ctx):
        """!entendi"""           
        await ctx.send(file = discord.File(st.image_path + 'Entendi.png'))
    
    @commands.command(name='perdemoS')
    async def perdemoS(self, ctx): 
        """!perdemoS"""          
        await ctx.send(file = discord.File(st.image_path + 'PerdemoS.png'))
    
    @commands.command(name='pexe')
    async def pexe(self, ctx):  
        """!pexe"""         
        await ctx.send(file = discord.File(st.image_path + 'Pexe.png'))
    
    @commands.command(name='sabo')
    async def sabo(self, ctx):   
        """!sabo"""        
        await ctx.send(file = discord.File(st.image_path + 'Sabo.png'))      
    
    @commands.command(name='sorriso')
    async def sorriso(self, ctx):  
        """!sorriso"""         
        await ctx.send(file = discord.File(st.image_path + 'Sorriso.png'))
        
    @commands.command(name='rh')
    async def rh(self, ctx):   
        """!rh"""        
        await ctx.send(file = discord.File(st.image_path + 'RH.png'))      
    
    @commands.command(name='perdemo')
    async def perdemo(self, ctx): 
        """!perdemo"""          
        await ctx.send(file = discord.File(st.image_path + 'Perdemo.png'))
        
    @commands.command(name='soninho')
    async def soninho(self, ctx):  
        """!soninho"""         
        await ctx.send(file = discord.File(st.image_path + 'Soninho.gif'))

    
def setup(bot):
    bot.add_cog(Stickers(bot))