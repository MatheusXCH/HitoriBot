import asyncio
import os
import random
import sys
import time

# Get the globals from Settings
import codes.paths as path
import discord
from discord.ext import commands

# # # Módulo: Minigames
# # - Contém um conjunto de minigames, como rolar de dados, cara-corôa e 'escolha um'!

# # # Utiliza:
# # - Discord.py API (by Rapptz on: https://github.com/Rapptz/discord.py)


class Minigames(commands.Cog):
    """Possui minigames simples, como rodar dados, cara-corôa e 'escolha um'"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="dado")
    async def dado(self, ctx: commands.Context, dice: str):
        """!dado <dado> => Fujitora joga os dados (Ex: !dado 1d6)
        - Invoca o Fujitora para tirar a sorte nos dados!
        """

        DICE_EMOJI = "<:dice:818478609806131240>"

        try:
            rolls, faces = map(int, dice.split("d"))
        except Exception:
            format_error_embed = discord.Embed(description="O formato deve ser <dados>d<lados> (Ex: !dado 1d6)")
            await ctx.send(embed=format_error_embed)
            return

        sum = 0
        result = ""
        rolls_results = []
        for r in range(rolls):
            roll = random.randint(1, faces)
            rolls_results.append(roll)
            sum = roll + sum
        result = f" {DICE_EMOJI}\n".join(str(r) for r in rolls_results) + f" {DICE_EMOJI}"

        sum_flag = ":green_circle:"
        if sum <= (rolls * faces) / 2:
            sum_flag = ":red_circle:"

        # First Embed - Fujitora
        fujitora_embed = discord.Embed(title="***FUJITORA FOI INVOCADO!!!***")
        fujitora_embed.add_field(
            name="Lembre-se: ",
            value="JAMAIS QUESTIONE O RESULTADO DOS DADOS!",
            inline=False,
        )
        file = discord.File(path.image_path + "Dado.png", filename="Dado.png")
        fujitora_embed.set_image(url="attachment://Dado.png")

        await ctx.send(file=file, embed=fujitora_embed)

        # Second Embed - Countdown
        dices_embed = discord.Embed()
        dices_embed.add_field(name="**Resultados: **", value="\u200b", inline=False)
        dices_embed.add_field(name="**Somatório: **", value="\u200b", inline=False)
        dices_message = await ctx.send(embed=dices_embed)

        dices_embed.set_thumbnail(url="https://media0.giphy.com/media/RiEW6mSQqjRiDy51MI/200.gif")
        await dices_message.edit(embed=dices_embed)
        await asyncio.sleep(5)

        dices_embed.set_field_at(0, name="**Resultados: **", value=f"{result}", inline=False)
        dices_embed.set_field_at(1, name="**Somatório: **", value=f"{sum} {sum_flag}", inline=False)
        dices_embed.set_thumbnail(url="")
        await dices_message.edit(embed=dices_embed)

    @commands.command(name="coin")
    async def coin(self, ctx: commands.Context):
        """!coin => Cara ou Corôa
        - Retorna o resultado de um lance de cara ou corôa
        """

        coin_flip = random.randint(0, 1)
        if coin_flip:
            embed_cara = discord.Embed()
            file = discord.File(path.minigame_path + "Cara.png", filename="Cara.png")
            embed_cara.set_image(url="attachment://Cara.png")
            await ctx.send(file=file, embed=embed_cara)

        else:
            embed_coroa = discord.Embed()
            file = discord.File(path.minigame_path + "Coroa.png", filename="Coroa.png")
            embed_coroa.set_image(url="attachment://Coroa.png")
            await ctx.send(file=file, embed=embed_coroa)

    @commands.command(name="choose")
    async def choose(self, ctx: commands.Context, *, input: str):
        """!choose <input> => O Bot escolhe entre as opções dadas. Separe as opções por vírgula!"""

        options = input.split(",")
        options = [item.strip().title() for item in options]
        choice = random.choice(options)
        await ctx.send(content=f"Hmmm... Eu escolho **{choice}**!")


def setup(bot):
    bot.add_cog(Minigames(bot))
