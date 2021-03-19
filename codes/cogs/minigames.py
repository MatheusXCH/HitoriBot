import sys, os, discord, random, time, asyncio
from discord.ext import commands

import codes.settings as st #Get the globals from Settings

# Módulo: Dices
#     - Contém um minigame no qual o Almirante Fujitora (One Piece!!!) é invocado para tirar a sorte nos dados!
class Minigames(commands.Cog):
    """Possui minigames simples, como rodar dados e cara-corôa"""
    
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='dado')
    async def dado(self, ctx: commands.Context, dice : str):
        """!dado <dado> => Fujitora joga os dados (Ex: !dado 1d6)
        Invoca o Fujitora para tirar a sorte nos dados!
        """
        DICE_EMOJI = '<:dice:818478609806131240>'
        
        try:
            rolls, faces = map(int, dice.split('d'))
        except:
            format_error_embed = discord.Embed(description = 'O formato deve ser <dados>d<lados> (Ex: !dado 1d6)')
            await ctx.send(embed = format_error_embed)
            return
        
        sum = 0
        result = ''
        rolls_results = []
        for r in range(rolls):
            roll = random.randint(1, faces)
            rolls_results.append(roll)
            sum = roll + sum
        result = f' {DICE_EMOJI}\n'.join(str(r) for r in rolls_results) + f' {DICE_EMOJI}'
        
        sum_flag = ':green_circle:'
        if sum <= (rolls * faces)/2:
            sum_flag = ':red_circle:'
        
        #First Embed - Fujitora
        fujitora_embed = discord.Embed(title = f'***FUJITORA FOI INVOCADO!!!***')
        fujitora_embed.add_field(name = 'Lembre-se: ', value = f'JAMAIS QUESTIONE O RESULTADO DOS DADOS!', inline = False)
        file = discord.File(st.image_path + 'Dado.png', filename='Dado.png')
        fujitora_embed.set_image(url = 'attachment://Dado.png')
        
        fujitora_message = await ctx.send(file = file, embed = fujitora_embed)
        
        #Second Embed - Countdown
        dices_embed = discord.Embed()
        dices_embed.add_field(name = f'**Resultados: **', value = '\u200b', inline = False)
        dices_embed.add_field(name = f'**Somatório: **', value = '\u200b', inline = False)
        dices_message = await ctx.send(embed = dices_embed)
        
        dices_embed.set_thumbnail(url = 'https://media0.giphy.com/media/RiEW6mSQqjRiDy51MI/200.gif')
        await dices_message.edit(embed = dices_embed)
        await asyncio.sleep(5)
        
        dices_embed.set_field_at(0, name = f'**Resultados: **', value = f'{result}', inline = False)
        dices_embed.set_field_at(1, name = f'**Somatório: **', value = f'{sum} {sum_flag}', inline = False)
        dices_embed.set_thumbnail(url = '')
        await dices_message.edit(embed = dices_embed)


    @commands.command(name = 'coin')
    async def coin(self, ctx: commands.Context):
        """!coin => Cara ou Corôa
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