import sys, os, discord, random, time
from discord.ext import commands

import codes.settings as st #Get the globals from Settings

class Coin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    #Coin (Command) - Cara ou Coroa
    @commands.command(name = 'coin')
    async def coin(self, ctx):
        coin_flip = random.randint(0, 1)
        if coin_flip:
            embed_cara = discord.Embed()
            file = discord.File(st.minigame_path + "Cara.png", filename = "Cara.png")
            embed_cara.set_image(url = 'attachment://Cara.png')
            await ctx.send(file = file, embed = embed_cara)
            
        else:
            embed_coroa = discord.Embed()
            file = discord.File(st.minigame_path + "Coroa.png", filename = "Coroa.png")
            embed_coroa.set_image(url = 'attachment://Coroa.png')
            await ctx.send(file = file, embed = embed_coroa)

def setup(bot):
    bot.add_cog(Coin(bot))
        