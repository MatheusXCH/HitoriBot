import asyncio
import aiohttp
import discord
from config import settings as cfg

ITAD_BASE = "https://api.isthereanydeal.com"


async def _find_game_id(title: str, session: aiohttp.ClientSession) -> str | None:
    async with session.get(f"{ITAD_BASE}/games/search/v1", params={"title": title, "key": cfg.itad_api_key}) as resp:
        data = await resp.json()
    results = data if isinstance(data, list) else data.get("results", [])
    return results[0]["id"] if results else None


async def _get_lowest_price(game_id: str, session: aiohttp.ClientSession) -> dict | None:
    async with session.get(
        f"{ITAD_BASE}/games/historylow/v1",
        params={"key": cfg.itad_api_key, "id": game_id, "country": "BR"},
    ) as resp:
        data = await resp.json()
    return data[0] if isinstance(data, list) and data else None


async def _get_current_prices(game_id: str, session: aiohttp.ClientSession) -> list:
    async with session.get(
        f"{ITAD_BASE}/games/prices/v3",
        params={"key": cfg.itad_api_key, "id": game_id, "country": "BR"},
    ) as resp:
        data = await resp.json()
    if isinstance(data, list) and data:
        return data[0].get("deals", [])
    return []


async def get_game_price(title: str) -> discord.Embed:
    async with aiohttp.ClientSession() as session:
        game_id = await _find_game_id(title, session)
        if not game_id:
            return discord.Embed(
                title="Jogo não encontrado",
                description=f"Não encontrei preços para **{title}** no IsThereAnyDeal.",
                color=discord.Color.red(),
            )
        lowest, deals = await asyncio.gather(
            _get_lowest_price(game_id, session),
            _get_current_prices(game_id, session),
        )

    embed = discord.Embed(
        title=f"💰 Preços — {title}",
        color=discord.Color.green(),
        url=f"https://isthereanydeal.com/game/{game_id}/info/",
    )
    if lowest:
        low_price = lowest.get("price", {})
        embed.add_field(
            name="📉 Menor preço histórico",
            value=f"**R$ {low_price.get('amount', '?'):.2f}** em {lowest.get('shop', {}).get('name', '?')} ({lowest.get('recorded', '?')[:10]})",
            inline=False,
        )
    if deals:
        best = sorted(deals, key=lambda d: d.get("price", {}).get("amount", 9999))[:3]
        lines = [
            f"**{d.get('shop', {}).get('name', '?')}:** R$ {d.get('price', {}).get('amount', 0):.2f}"
            + (f" (-{d.get('cut', 0)}%)" if d.get("cut") else "")
            for d in best
        ]
        embed.add_field(name="🛒 Melhores preços atuais", value="\n".join(lines), inline=False)
    else:
        embed.add_field(name="🛒 Preços atuais", value="Sem ofertas encontradas no momento.", inline=False)
    return embed
