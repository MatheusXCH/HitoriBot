import aiohttp
import discord

ANILIST_URL = "https://graphql.anilist.co"

_ANIME_QUERY = """
query ($search: String) {
  Page(perPage: 5) {
    media(search: $search, type: ANIME, sort: SEARCH_MATCH) {
      id title { romaji english } status episodes averageScore genres
      description(asHtml: false)
      coverImage { large }
      siteUrl
    }
  }
}
"""

_MANGA_QUERY = """
query ($search: String) {
  Page(perPage: 5) {
    media(search: $search, type: MANGA, sort: SEARCH_MATCH) {
      id title { romaji english } status chapters volumes averageScore genres
      description(asHtml: false)
      coverImage { large }
      siteUrl
    }
  }
}
"""

_CHARACTER_QUERY = """
query ($search: String) {
  Page(perPage: 5) {
    characters(search: $search, sort: SEARCH_MATCH) {
      id name { full }
      image { large }
      siteUrl
      media(type: ANIME, sort: POPULARITY_DESC, perPage: 1) {
        nodes { title { romaji } }
      }
    }
  }
}
"""


async def _query(query: str, variables: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(ANILIST_URL, json={"query": query, "variables": variables}) as resp:
            return await resp.json()


def _truncate(text: str | None, limit: int = 300) -> str:
    if not text:
        return "—"
    clean = text.replace("<br>", "\n").replace("<i>", "").replace("</i>", "")
    return clean[:limit] + "…" if len(clean) > limit else clean


async def search_anime(title: str) -> list[discord.Embed]:
    data = await _query(_ANIME_QUERY, {"search": title})
    results = data.get("data", {}).get("Page", {}).get("media", [])
    embeds = []
    for item in results:
        romaji = item["title"]["romaji"]
        english = item["title"].get("english") or ""
        display = f"{romaji}" + (f" ({english})" if english and english != romaji else "")
        embed = discord.Embed(title=display, url=item.get("siteUrl", ""), color=discord.Color.blue())
        embed.set_thumbnail(url=item.get("coverImage", {}).get("large", ""))
        embed.add_field(name="Status", value=item.get("status", "—"), inline=True)
        embed.add_field(name="Episódios", value=str(item.get("episodes") or "—"), inline=True)
        embed.add_field(name="Nota", value=f"{item.get('averageScore', '—')}/100", inline=True)
        genres = ", ".join(item.get("genres", [])[:4])
        if genres:
            embed.add_field(name="Gêneros", value=genres, inline=False)
        embed.add_field(name="Sinopse", value=_truncate(item.get("description")), inline=False)
        embeds.append(embed)
    return embeds


async def search_manga(title: str) -> list[discord.Embed]:
    data = await _query(_MANGA_QUERY, {"search": title})
    results = data.get("data", {}).get("Page", {}).get("media", [])
    embeds = []
    for item in results:
        romaji = item["title"]["romaji"]
        english = item["title"].get("english") or ""
        display = f"{romaji}" + (f" ({english})" if english and english != romaji else "")
        embed = discord.Embed(title=display, url=item.get("siteUrl", ""), color=discord.Color.orange())
        embed.set_thumbnail(url=item.get("coverImage", {}).get("large", ""))
        embed.add_field(name="Status", value=item.get("status", "—"), inline=True)
        embed.add_field(name="Capítulos", value=str(item.get("chapters") or "—"), inline=True)
        embed.add_field(name="Volumes", value=str(item.get("volumes") or "—"), inline=True)
        embed.add_field(name="Nota", value=f"{item.get('averageScore', '—')}/100", inline=True)
        genres = ", ".join(item.get("genres", [])[:4])
        if genres:
            embed.add_field(name="Gêneros", value=genres, inline=False)
        embed.add_field(name="Sinopse", value=_truncate(item.get("description")), inline=False)
        embeds.append(embed)
    return embeds


async def search_character(name: str) -> list[discord.Embed]:
    data = await _query(_CHARACTER_QUERY, {"search": name})
    results = data.get("data", {}).get("Page", {}).get("characters", [])
    embeds = []
    for item in results:
        full_name = item["name"]["full"]
        media_nodes = item.get("media", {}).get("nodes", [])
        media_title = media_nodes[0]["title"]["romaji"] if media_nodes else "—"
        embed = discord.Embed(title=full_name, url=item.get("siteUrl", ""), color=discord.Color.purple())
        embed.set_thumbnail(url=item.get("image", {}).get("large", ""))
        embed.add_field(name="Aparece em", value=media_title, inline=False)
        embeds.append(embed)
    return embeds
