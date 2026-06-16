import aiohttp
import discord

WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"


async def wikipedia_summary(query: str) -> discord.Embed:
    slug = query.replace(" ", "_")
    async with aiohttp.ClientSession() as session:
        async with session.get(WIKI_SUMMARY_URL.format(slug)) as resp:
            if resp.status == 200:
                data = await resp.json()
            else:
                async with session.get(WIKI_SEARCH_URL, params={
                    "action": "query", "list": "search", "srsearch": query,
                    "format": "json", "srlimit": 1,
                }) as search_resp:
                    search_data = await search_resp.json()
                results = search_data.get("query", {}).get("search", [])
                if not results:
                    return discord.Embed(
                        title="Não encontrado",
                        description=f"Nenhum artigo encontrado para **{query}** na Wikipedia.",
                        color=discord.Color.red(),
                    )
                title = results[0]["title"].replace(" ", "_")
                async with session.get(WIKI_SUMMARY_URL.format(title)) as r2:
                    data = await r2.json()

    extract = data.get("extract", "")
    if len(extract) > 500:
        extract = extract[:500] + "…"

    embed = discord.Embed(
        title=data.get("title", query),
        description=extract or "Sem descrição disponível.",
        url=data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        color=discord.Color.light_grey(),
    )
    thumbnail = data.get("thumbnail", {}).get("source")
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text="Fonte: Wikipedia")
    return embed
