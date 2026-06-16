import discord
from discord.ext import commands
from discord import app_commands
from core.agent import call_agent, is_rate_limited

ALLOWED_EXTENSIONS = {".mp3", ".m4a", ".wav", ".ogg", ".png", ".jpg", ".jpeg", ".gif", ".webp"}


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if not message.guild:
            return
        if not self.bot.user:
            return
        if self.bot.user not in message.mentions:
            return

        guild_id = message.guild.id
        channel_id = message.channel.id
        pool = self.bot.pool

        ai_enabled = await pool.fetchval(
            "SELECT ai_enabled FROM guild_settings WHERE guild_id = $1", guild_id
        )
        if not ai_enabled:
            return

        if await is_rate_limited(pool, guild_id, channel_id):
            await message.reply("⏳ Muitas mensagens neste canal na última hora. Tente novamente mais tarde.", mention_author=False)
            return

        attachments = [
            {"url": a.url, "filename": a.filename}
            for a in message.attachments
            if any(a.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
        ]

        content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
        if not content and not attachments:
            await message.reply("Olá! Como posso ajudar? 😊", mention_author=False)
            return

        async with message.channel.typing():
            try:
                text_reply, embeds = await call_agent(
                    pool=pool,
                    guild_id=guild_id,
                    channel_id=channel_id,
                    user_message=content,
                    bot=self.bot,
                    attachments=attachments or None,
                )
            except Exception as e:
                await message.reply(f"❌ Erro ao processar sua mensagem: {e}", mention_author=False)
                return

        if embeds and text_reply:
            await message.reply(text_reply, embeds=embeds[:10], mention_author=False)
        elif embeds:
            await message.reply(embeds=embeds[:10], mention_author=False)
        elif text_reply:
            await message.reply(text_reply, mention_author=False)

    @app_commands.command(name="ai-toggle", description="Enable or disable the AI agent in this server")
    @app_commands.default_permissions(administrator=True)
    async def ai_toggle(self, interaction: discord.Interaction) -> None:
        current = await self.bot.pool.fetchval(
            "SELECT ai_enabled FROM guild_settings WHERE guild_id = $1", interaction.guild.id
        )
        new_value = not bool(current)
        await self.bot.pool.execute(
            "UPDATE guild_settings SET ai_enabled = $1 WHERE guild_id = $2", new_value, interaction.guild.id
        )
        state = "ativado" if new_value else "desativado"
        await interaction.response.send_message(f"✅ Agente IA {state} neste servidor.", ephemeral=True)

    @app_commands.command(name="ai-clear", description="Clear the AI conversation context for this channel")
    @app_commands.default_permissions(manage_messages=True)
    async def ai_clear(self, interaction: discord.Interaction) -> None:
        await self.bot.pool.execute(
            "DELETE FROM ai_context WHERE guild_id = $1 AND channel_id = $2",
            interaction.guild.id, interaction.channel.id,
        )
        await interaction.response.send_message("✅ Contexto de conversa limpo para este canal.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
