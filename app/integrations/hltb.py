import asyncio
import discord
from howlongtobeatpy import HowLongToBeat


async def get_completion_time(title: str) -> discord.Embed | None:
    results = await asyncio.get_event_loop().run_in_executor(
        None, lambda: HowLongToBeat().search(title)
    )
    if not results:
        return None
    game = max(results, key=lambda r: r.similarity)

    def _fmt(hours: float | None) -> str:
        if hours is None or hours <= 0:
            return "—"
        return f"{hours:.1f}h"

    embed = discord.Embed(
        title=f"⏱️ {game.game_name}",
        url=f"https://howlongtobeat.com/game/{game.game_id}",
        color=discord.Color.blurple(),
    )
    embed.set_thumbnail(url=f"https://howlongtobeat.com{game.game_image_url}" if game.game_image_url else "")
    embed.add_field(name="🎯 Campanha", value=_fmt(game.main_story), inline=True)
    embed.add_field(name="➕ Campanha + Extras", value=_fmt(game.main_extra), inline=True)
    embed.add_field(name="🏆 Completionist", value=_fmt(game.completionist), inline=True)
    return embed
