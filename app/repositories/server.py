import asyncpg
import aiohttp
import discord
from pathlib import Path
from config import settings


# ── Read tools ────────────────────────────────────────────────────────────────

async def get_server_rules(pool: asyncpg.Pool, guild_id: int) -> discord.Embed:
    row = await pool.fetchrow("SELECT rules_text FROM guild_settings WHERE guild_id = $1", guild_id)
    rules = row["rules_text"] if row and row["rules_text"] else "Nenhuma regra cadastrada. Use `/rule-set` para configurar."
    return discord.Embed(title="📋 Regras do Servidor", description=rules, color=discord.Color.gold())


async def get_server_info(pool: asyncpg.Pool, guild_id: int, bot) -> discord.Embed:
    guild = bot.get_guild(guild_id)
    sounds_count = await pool.fetchval("SELECT COUNT(*) FROM guild_sounds WHERE guild_id = $1", guild_id)
    stickers_count = await pool.fetchval("SELECT COUNT(*) FROM guild_stickers WHERE guild_id = $1", guild_id)
    playlists_count = await pool.fetchval("SELECT COUNT(*) FROM guild_playlists WHERE guild_id = $1", guild_id)

    embed = discord.Embed(title=f"ℹ️ {guild.name if guild else 'Servidor'}", color=discord.Color.blurple())
    if guild:
        embed.add_field(name="Membros", value=str(guild.member_count), inline=True)
    embed.add_field(name="🔊 Sons", value=str(sounds_count), inline=True)
    embed.add_field(name="🖼️ Stickers", value=str(stickers_count), inline=True)
    embed.add_field(name="🎵 Playlists", value=str(playlists_count), inline=True)
    embed.set_footer(text="Use /sound-list, /sticker-list ou /playlists para ver os itens cadastrados.")
    return embed


async def get_sounds_library(pool: asyncpg.Pool, guild_id: int) -> discord.Embed:
    rows = await pool.fetch("SELECT name FROM guild_sounds WHERE guild_id = $1 ORDER BY name", guild_id)
    embed = discord.Embed(title="🔊 Sons disponíveis", color=discord.Color.blurple())
    embed.description = " • ".join(f"`{r['name']}`" for r in rows) if rows else "Nenhum som cadastrado."
    return embed


async def get_stickers_library(pool: asyncpg.Pool, guild_id: int) -> discord.Embed:
    rows = await pool.fetch("SELECT name FROM guild_stickers WHERE guild_id = $1 ORDER BY name", guild_id)
    embed = discord.Embed(title="🖼️ Stickers disponíveis", color=discord.Color.blurple())
    embed.description = " • ".join(f"`{r['name']}`" for r in rows) if rows else "Nenhum sticker cadastrado."
    return embed


async def get_playlists(pool: asyncpg.Pool, guild_id: int) -> discord.Embed:
    rows = await pool.fetch("SELECT name, url FROM guild_playlists WHERE guild_id = $1 ORDER BY name", guild_id)
    embed = discord.Embed(title="🎵 Playlists do servidor", color=discord.Color.green())
    if rows:
        for row in rows:
            embed.add_field(name=row["name"], value=row["url"], inline=False)
    else:
        embed.description = "Nenhuma playlist cadastrada."
    return embed


# ── Write tools ───────────────────────────────────────────────────────────────

async def _download_attachment(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            dest.write_bytes(await resp.read())


async def register_sound(pool: asyncpg.Pool, guild_id: int, name: str, attachment_url: str, filename: str) -> str:
    name = name.lower().strip()
    dest = Path(settings.sounds_path) / str(guild_id) / filename
    await _download_attachment(attachment_url, dest)
    await pool.execute(
        "INSERT INTO guild_sounds (guild_id, name, file_path) VALUES ($1, $2, $3) "
        "ON CONFLICT (guild_id, name) DO UPDATE SET file_path = $3",
        guild_id, name, str(dest),
    )
    return f"✅ Som **{name}** cadastrado com sucesso."


async def delete_sound(pool: asyncpg.Pool, guild_id: int, name: str) -> str:
    name = name.lower().strip()
    row = await pool.fetchrow(
        "SELECT file_path FROM guild_sounds WHERE guild_id = $1 AND name = $2", guild_id, name
    )
    if not row:
        return f"❌ Som **{name}** não encontrado."
    Path(row["file_path"]).unlink(missing_ok=True)
    await pool.execute("DELETE FROM guild_sounds WHERE guild_id = $1 AND name = $2", guild_id, name)
    return f"✅ Som **{name}** removido."


async def register_sticker(pool: asyncpg.Pool, guild_id: int, name: str, attachment_url: str, filename: str) -> str:
    name = name.lower().strip()
    dest = Path(settings.stickers_path) / str(guild_id) / filename
    await _download_attachment(attachment_url, dest)
    await pool.execute(
        "INSERT INTO guild_stickers (guild_id, name, file_path) VALUES ($1, $2, $3) "
        "ON CONFLICT (guild_id, name) DO UPDATE SET file_path = $3",
        guild_id, name, str(dest),
    )
    return f"✅ Sticker **{name}** cadastrado com sucesso."


async def delete_sticker(pool: asyncpg.Pool, guild_id: int, name: str) -> str:
    name = name.lower().strip()
    row = await pool.fetchrow(
        "SELECT file_path FROM guild_stickers WHERE guild_id = $1 AND name = $2", guild_id, name
    )
    if not row:
        return f"❌ Sticker **{name}** não encontrado."
    Path(row["file_path"]).unlink(missing_ok=True)
    await pool.execute("DELETE FROM guild_stickers WHERE guild_id = $1 AND name = $2", guild_id, name)
    return f"✅ Sticker **{name}** removido."


async def register_playlist(pool: asyncpg.Pool, guild_id: int, name: str, url: str) -> str:
    name = name.strip()
    await pool.execute(
        "INSERT INTO guild_playlists (guild_id, name, url) VALUES ($1, $2, $3) "
        "ON CONFLICT (guild_id, name) DO UPDATE SET url = $3",
        guild_id, name, url,
    )
    return f"✅ Playlist **{name}** cadastrada."


async def delete_playlist(pool: asyncpg.Pool, guild_id: int, name: str) -> str:
    name = name.strip()
    result = await pool.execute(
        "DELETE FROM guild_playlists WHERE guild_id = $1 AND name = $2", guild_id, name
    )
    if result == "DELETE 0":
        return f"❌ Playlist **{name}** não encontrada."
    return f"✅ Playlist **{name}** removida."
