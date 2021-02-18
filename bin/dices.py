import os, discord, random, time
from discord.ext import commands

#GLOBAL

#Paths
image_path = './stickers/'

class Dices(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #TODO Tentar colocar no formato Embed
    #Dado (Command) - Invoca o Fujitora e joga um XdY
    @commands.command(name='dado')
    async def dado(self, ctx, dice : str):
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('O formato deve ser [quant. dados]d[lados dos dados]')
            return
        
        await ctx.send(f':octagonal_sign: **FUJITORA FOI INVOCADO** :octagonal_sign: \n\n'
                       f'Lembre-se: \n'
                       f'*JAMAIS QUESTIONE O RESULTADO DOS DADOS!*')
        await ctx.send(file = discord.File(image_path + 'Dado.png'))
        
        time.sleep(1)
        await ctx.send(':three:')
        time.sleep(1)
        await ctx.send(':two:')
        time.sleep(1)
        await ctx.send(':one:')
        time.sleep(1)
        await ctx.send(':exclamation: \n\n')
        time.sleep(0.5)
        
        sum = 0
        result = []
        for r in range(rolls):
            num = random.randint(1, limit)
            result.append(num)
            sum = num + sum
        
        result = ', '.join(str(r) for r in result)
        
        await ctx.send(f'**Resultado** \n :arrow_right: {result} \n')
        await ctx.send(f'\n**Soma**\n :arrow_right: {sum}')


def setup(bot):
    bot.add_cog(Dices(bot))