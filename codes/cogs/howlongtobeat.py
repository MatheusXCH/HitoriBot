import os, discord
from discord.ext import commands
from discord.utils import *

from howlongtobeatpy import HowLongToBeat

hltb = HowLongToBeat()

# Módulo: HowLongToBeat
#    - Integra o PyBOT com o https://howlongtobeat.com/ via howlongtobeatpy
#    - Permite consultar o tempo estimado de término de games, de acordo com os dados disponibilizados pela comunidade do HLTB
#    #### Utiliza: 
#    ##### howlongtobeatpy API (by ScrappyCocco on: https://github.com/ScrappyCocco/HowLongToBeat-PythonAPI)


class HowLongToBeat(commands.Cog):
    """Obtém dados de tempo de jogo dos games cadastrados no 'HowLongToBeat'
    """
    
    def __init__(self, bot):
        self.bot = bot


    # !hltb <game_title>
    # - Procura um jogo no HowLongToBeat e retorna Título, Imagem, Main, Main+Extra e Completionist
    # - Com o painel interativo, é possível avançar por todos os itens encontrados na primeira página do HowLongToBeat!
    @commands.command(pass_context = True, name = 'hltb')
    async def hltb(self, ctx, *, game_title):
        """!hltb <game_title>
        Retorna o resultado da busca no HowLongToBeat
        """  
          
        results = hltb.search(game_title)
        
        def hltb_pages_layout(i):
            embed_hltb = discord.Embed(
                title = results[i].game_name,
                colour = discord.Colour(0x03b1fc),
                url = results[i].game_web_link
            )
            embed_hltb.add_field(name = results[i].gameplay_main_label, 
                             value = f'{results[i].gameplay_main} {results[i].gameplay_main_unit}',
                             inline = False)
        
            embed_hltb.add_field(name = results[i].gameplay_main_extra_label, 
                                value = f'{results[i].gameplay_main_extra} {results[i].gameplay_main_extra_unit}',
                                inline = False)
            
            embed_hltb.add_field(name = results[i].gameplay_completionist_label, 
                                value = f'{results[i].gameplay_completionist} {results[i].gameplay_completionist_unit}',
                                inline = False)
            embed_hltb.set_image(url = f'https://howlongtobeat.com{str(results[i].game_image_url)}')
        
            return embed_hltb

        page = hltb_pages_layout(0)
            
        message = await ctx.send(embed=page)
        await message.add_reaction('⏪')
        await message.add_reaction('◀')
        await message.add_reaction('▶')
        await message.add_reaction('⏩')
        await message.add_reaction('❌')

        def check(reaction, user):
            """ Confere se o click na reação foi feito pelo autor do comando """
            return user == ctx.author

        i = 0
        reaction = None

        while True:
            if str(reaction) == '⏪':
                i = 0
                page = hltb_pages_layout(i)
                await message.edit(embed = page)
                
            elif str(reaction) == '◀':
                if i > 0:
                    i -= 1
                    page = hltb_pages_layout(i)
                    await message.edit(embed = page)
                    
            elif str(reaction) == '▶':
                if i < len(results) - 1:
                    i += 1
                    page = hltb_pages_layout(i)
                    await message.edit(embed = page)
                    
            elif str(reaction) == '⏩':
                i = len(results) - 1
                page = hltb_pages_layout(len(results) - 1)
                await message.edit(embed = page)
                
            elif str(reaction) == '❌':
                await message.clear_reactions()
                await message.delete()

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                await message.remove_reaction(reaction, user)
            except:
                break

        await message.clear_reactions()
    
def setup(bot):
    bot.add_cog(HowLongToBeat(bot))
