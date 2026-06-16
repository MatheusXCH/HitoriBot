import discord
from discord.ext import commands
from repositories.guild import get_or_create_guild, delete_guild


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await get_or_create_guild(self.bot.pool, guild.id, guild.name)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        await delete_guild(self.bot.pool, guild.id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            embed = discord.Embed(
                title=f"Bem-vindo ao {member.guild.name}!",
                description="Use `/help` para ver o que posso fazer.",
                color=discord.Color.blurple(),
            )
            await member.send(embed=embed)
        except discord.Forbidden:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
