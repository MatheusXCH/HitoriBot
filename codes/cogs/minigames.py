import sys, os, discord, random, time
from discord.ext import commands

import codes.settings as st #Get the globals from Settings

# Módulo: Dices
#     - Contém um minigame no qual o Almirante Fujitora (One Piece!!!) é invocado para tirar a sorte nos dados!
class Minigames(commands.Cog):
    """Possui minigames simples, como rodar dados e cara-corôa
    """
    
    def __init__(self, bot):
        self.bot = bot


    #TODO Tentar colocar no formato Embed
    # !dado [MdN]
    #     - Invoca o Fujitora para tirar a sorte nos dados!
    #     - Argumentos: dice (type str) 
    #     ##### Ex: !dado 3d6 -> Joga 3 dados de 6 faces
    @commands.command(name='dado')
    async def dado(self, ctx, dice : str):
        """!dado <dado> (Ex: !dado 1d6)
        Invoca o Fujitora para tirar a sorte nos dados!
        """
        
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('O formato deve ser [quant. dados]d[lados dos dados]')
            return
        
        await ctx.send(f':octagonal_sign: **FUJITORA FOI INVOCADO** :octagonal_sign: \n\n'
                       f'Lembre-se: \n'
                       f'*JAMAIS QUESTIONE O RESULTADO DOS DADOS!*')
        await ctx.send(file = discord.File(st.image_path + 'Dado.png'))
        
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


    # !coin
    #     - Cara ou Corôa
    @commands.command(name = 'coin')
    async def coin(self, ctx):
        """!coin
        Retorna o resultado de um lance de cara ou corôa
        """
        
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
    bot.add_cog(Minigames(bot))