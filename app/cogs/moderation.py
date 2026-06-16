import discord
from discord.ext import commands
from discord import app_commands


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ **{member}** foi expulso. Motivo: {reason}", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"✅ **{member}** foi banido. Motivo: {reason}", ephemeral=True)

    @app_commands.command(name="unban", description="Unban a user by ID")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ **{user}** desbanido.", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("❌ Usuário não encontrado ou não está banido.", ephemeral=True)

    @app_commands.command(name="nick", description="Change a member's nickname")
    @app_commands.default_permissions(manage_nicknames=True)
    async def nick(self, interaction: discord.Interaction, member: discord.Member, nickname: str = ""):
        await member.edit(nick=nickname or None)
        msg = f"✅ Apelido de **{member}** alterado para **{nickname}**." if nickname else f"✅ Apelido de **{member}** removido."
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="role-add", description="Add a role to a member")
    @app_commands.default_permissions(manage_roles=True)
    async def role_add(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ Cargo **{role.name}** adicionado a **{member}**.", ephemeral=True)

    @app_commands.command(name="role-remove", description="Remove a role from a member")
    @app_commands.default_permissions(manage_roles=True)
    async def role_remove(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        await member.remove_roles(role)
        await interaction.response.send_message(f"✅ Cargo **{role.name}** removido de **{member}**.", ephemeral=True)

    @app_commands.command(name="role-list", description="List all roles of a member")
    @app_commands.default_permissions(manage_roles=True)
    async def role_list(self, interaction: discord.Interaction, member: discord.Member):
        roles = [r.mention for r in member.roles if r.name != "@everyone"]
        embed = discord.Embed(
            title=f"Cargos de {member.display_name}",
            description=" ".join(roles) if roles else "Nenhum cargo.",
            color=member.color,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="perms", description="Show permissions of a member")
    @app_commands.default_permissions(manage_roles=True)
    async def perms(self, interaction: discord.Interaction, member: discord.Member):
        perms = [p for p, v in member.guild_permissions if v]
        embed = discord.Embed(
            title=f"Permissões de {member.display_name}",
            description="\n".join(f"✅ `{p}`" for p in perms) or "Nenhuma.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clear", description="Delete messages from a specific member (default: bot)")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int = 10, member: discord.Member = None):
        await interaction.response.defer(ephemeral=True)
        target = member or self.bot.user
        deleted = await interaction.channel.purge(limit=amount, check=lambda m: m.author == target)
        await interaction.followup.send(f"✅ {len(deleted)} mensagem(ns) de **{target.display_name}** removida(s).", ephemeral=True)

    @app_commands.command(name="purge", description="Delete the last N messages in the channel")
    @app_commands.default_permissions(administrator=True)
    async def purge(self, interaction: discord.Interaction, amount: int = 20):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ {len(deleted)} mensagem(ns) removida(s).", ephemeral=True)

    @app_commands.command(name="invite", description="Generate a one-time invite link for this server")
    async def invite(self, interaction: discord.Interaction):
        invite = await interaction.channel.create_invite(max_uses=1, unique=True)
        try:
            await interaction.user.send(f"Aqui está seu convite único: {invite.url}")
            await interaction.response.send_message("✅ Convite enviado por DM.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"Convite: {invite.url}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
