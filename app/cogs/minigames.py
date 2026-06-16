import random
import re
import discord
from discord.ext import commands
from discord import app_commands


class Minigames(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="dice", description="Roll dice in XdY format (e.g. 2d6)")
    async def dice(self, interaction: discord.Interaction, notation: str):
        match = re.fullmatch(r"(\d+)d(\d+)", notation.strip().lower())
        if not match:
            await interaction.response.send_message("❌ Formato inválido. Use `XdY` — ex: `2d6`, `1d20`.", ephemeral=True)
            return
        amount = min(int(match.group(1)), 20)
        sides = min(int(match.group(2)), 1000)
        if amount < 1 or sides < 2:
            await interaction.response.send_message("❌ Valores inválidos.", ephemeral=True)
            return
        rolls = [random.randint(1, sides) for _ in range(amount)]
        total = sum(rolls)
        roll_str = " + ".join(str(r) for r in rolls) if amount > 1 else str(rolls[0])
        color = discord.Color.green() if total >= (amount * sides * 0.7) else discord.Color.red()
        embed = discord.Embed(title=f"🎲 {notation}", color=color)
        embed.add_field(name="Resultados", value=roll_str, inline=False)
        if amount > 1:
            embed.add_field(name="Total", value=f"**{total}**", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coin", description="Flip a coin")
    async def coin(self, interaction: discord.Interaction):
        result = random.choice(["Cara", "Coroa"])
        embed = discord.Embed(
            title="🪙 Cara ou Coroa",
            description=f"**{result}!**",
            color=discord.Color.gold(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="choose", description="Choose randomly between options (comma-separated)")
    async def choose(self, interaction: discord.Interaction, options: str):
        choices = [o.strip() for o in options.split(",") if o.strip()]
        if len(choices) < 2:
            await interaction.response.send_message("❌ Forneça pelo menos 2 opções separadas por vírgula.", ephemeral=True)
            return
        chosen = random.choice(choices)
        embed = discord.Embed(
            title="🎯 Escolha",
            description=f"**{chosen}**",
            color=discord.Color.blurple(),
        )
        embed.set_footer(text=f"Entre {len(choices)} opções")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Minigames(bot))
