import aiohttp
import discord
from config import settings as cfg

ITAD_BASE = "https://api.isthereanydeal.com"


async def _find_game_id(title: str, session: aiohttp.ClientSession) -> tuple[str, str] | None:
    async with session.get(
        f"{ITAD_BASE}/games/search/v1",
        params={"title": title, "key": cfg.itad_api_key},
    ) as resp:
        data = await resp.json()
    results = data if isinstance(data, list) else data.get("results", [])
    if not results:
        return None
    g = results[0]
    return g["id"], g.get("slug", g["id"])


async def _get_prices(game_id: str, session: aiohttp.ClientSession) -> dict:
    async with session.post(
        f"{ITAD_BASE}/games/prices/v3",
        params={"key": cfg.itad_api_key, "country": "BR"},
        json=[game_id],
    ) as resp:
        data = await resp.json()
    return data[0] if isinstance(data, list) and data else {}


async def get_game_price(title: str) -> discord.Embed:
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        result = await _find_game_id(title, session)
        if not result:
            return discord.Embed(
                title="Jogo não encontrado",
                description=f"Não encontrei **{title}** no IsThereAnyDeal.",
                color=discord.Color.red(),
            )
        game_id, slug = result
        price_data = await _get_prices(game_id, session)

    embed = discord.Embed(
        title=f"💰 Preços — {title}",
        color=discord.Color.green(),
        url=f"https://isthereanydeal.com/game/{slug}/info/",
    )

    history_low = price_data.get("historyLow", {}).get("all", {})
    if history_low:
        embed.add_field(
            name="📉 Menor preço histórico",
            value=f"**{history_low.get('currency', 'USD')} {history_low.get('amount', '?'):.2f}**",
            inline=False,
        )

    deals = price_data.get("deals", [])
    if deals:
        best = sorted(deals, key=lambda d: d.get("price", {}).get("amount", 9999))[:3]
        lines = []
        for d in best:
            price = d.get("price", {})
            shop = d.get("shop", {}).get("name", "?")
            amount = price.get("amount", 0)
            currency = price.get("currency", "BRL")
            cut = d.get("cut", 0)
            line = f"**{shop}:** {currency} {amount:.2f}"
            if cut:
                line += f" (-{cut}%)"
            lines.append(line)
        embed.add_field(name="🛒 Melhores preços atuais", value="\n".join(lines), inline=False)
    else:
        embed.add_field(name="🛒 Preços atuais", value="Sem ofertas encontradas no momento.", inline=False)

    return embed
