import aiohttp
import discord

STEAM_SEARCH_URL = "https://store.steampowered.com/api/storesearch/"
STEAM_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
STEAMSPY_URL = "https://steamspy.com/api.php"


async def search_game_ids(title: str) -> list[int]:
    async with aiohttp.ClientSession() as session:
        async with session.get(STEAM_SEARCH_URL, params={"term": title, "l": "portuguese", "cc": "BR"}) as resp:
            data = await resp.json()
    return [item["id"] for item in data.get("items", [])[:5]]


async def get_game_details(appid: int) -> dict | None:
    async with aiohttp.ClientSession() as session:
        async with session.get(STEAM_DETAILS_URL, params={"appids": appid, "cc": "BR", "l": "portuguese"}) as resp:
            data = await resp.json()
    entry = data.get(str(appid), {})
    if not entry.get("success"):
        return None
    return entry["data"]


async def get_steamspy_data(appid: int) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(STEAMSPY_URL, params={"request": "appdetails", "appid": appid}) as resp:
            return await resp.json(content_type=None)


def _format_price(price_data: dict | None) -> str:
    if not price_data:
        return "Gratuito"
    if price_data.get("discount_percent", 0) > 0:
        original = price_data["initial"] / 100
        final = price_data["final"] / 100
        return f"~~R$ {original:.2f}~~ → **R$ {final:.2f}** (-{price_data['discount_percent']}%)"
    return f"R$ {price_data.get('final', 0) / 100:.2f}"


async def build_game_embed(appid: int) -> discord.Embed | None:
    details = await get_game_details(appid)
    if not details:
        return None
    spy = await get_steamspy_data(appid)
    price_str = _format_price(details.get("price_overview"))
    genres = ", ".join(g["description"] for g in details.get("genres", [])[:4])
    score = spy.get("positive", 0)
    total = spy.get("positive", 0) + spy.get("negative", 0)
    score_str = f"{round(score / total * 100)}% positivas ({total:,} avaliações)" if total else "Sem avaliações"
    embed = discord.Embed(
        title=details["name"],
        description=details.get("short_description", ""),
        url=f"https://store.steampowered.com/app/{appid}",
        color=discord.Color.from_rgb(27, 40, 56),
    )
    embed.set_thumbnail(url=details.get("header_image", ""))
    embed.add_field(name="💰 Preço (BR)", value=price_str, inline=True)
    embed.add_field(name="⭐ Avaliações", value=score_str, inline=True)
    if genres:
        embed.add_field(name="🎮 Gêneros", value=genres, inline=False)
    publishers = ", ".join(details.get("publishers", [])[:3])
    if publishers:
        embed.add_field(name="🏢 Publisher", value=publishers, inline=True)
    release = details.get("release_date", {}).get("date", "—")
    embed.add_field(name="📅 Lançamento", value=release, inline=True)
    embed.set_footer(text=f"App ID: {appid}")
    return embed


async def search_game(title: str) -> list[discord.Embed]:
    appids = await search_game_ids(title)
    embeds = []
    for appid in appids:
        embed = await build_game_embed(appid)
        if embed:
            embeds.append(embed)
        if len(embeds) >= 3:
            break
    return embeds
