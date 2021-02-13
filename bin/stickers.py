import os, discord
from discord.ext import commands

#GLOBAL
#Path no qual estão armazenados os stickerss
image_path = './bin/stickers/'

class Stickers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Stickers - Daqui em diante, estão listados todos os Stickers do Servidor
    #
    #
    @commands.command(name='bebero')
    async def bebero(self, ctx):        
        await ctx.send(file = discord.File(image_path + 'Bebero.png'))
    
    @commands.command(name='analise')
    async def analise(self, ctx):        
        await ctx.send(file = discord.File(image_path + 'Analise.png'))
    
    @commands.command(name='bença')
    async def bença(self, ctx):        
        await ctx.send(file = discord.File(image_path + 'Bença.png'))
    
    @commands.command(name='broxa')
    async def broxa(self, ctx):        
        await ctx.send(file = discord.File(image_path + 'Broxa.png'))
    
    @commands.command(name='entendi')
    async def entendi(self, ctx):        
        await ctx.send(file = discord.File(image_path + 'Entendi.png'))
    
    @commands.command(name='perdemoS')
    async def perdemoS(self, ctx):        
        await ctx.send(file = discord.File(image_path + 'PerdemoS.png'))
    
    @commands.command(name='pexe')
    async def pexe(self, ctx):        
        await ctx.send(file = discord.File(image_path + 'Pexe.png'))
    
    @commands.command(name='sabo')
    async def sabo(self, ctx):        
        await ctx.send(file = discord.File(image_path + 'Sabo.png'))      
    
    @commands.command(name='sorriso')
    async def sorriso(self, ctx):        
        await ctx.send(file = discord.File(image_path + 'Sorriso.png'))
        
    @commands.command(name='rh')
    async def rh(self, ctx):        
        await ctx.send(file = discord.File(image_path + 'RH.png'))      
    
    @commands.command(name='perdemo')
    async def perdemo(self, ctx):        
        await ctx.send(file = discord.File(image_path + 'Perdemo.png'))

    
def setup(bot):
    bot.add_cog(Stickers(bot))