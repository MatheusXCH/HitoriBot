import asyncpg
import discord
import asyncpraw
from config import settings as cfg

SUBREDDIT = "FreeGameFindings"
PLATFORMS = {"steam", "epic", "gog", "humble", "itch", "amazon", "prime"}
FLAIR_INCLUDE = {"game", "dlc"}


async def fetch_free_games(reddit_client_id: str, reddit_client_secret: str, reddit_user_agent: str) -> list[dict]:
    reddit = asyncpraw.Reddit(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent=reddit_user_agent,
    )
    results = []
    try:
        sub = await reddit.subreddit(SUBREDDIT)
        async for post in sub.hot(limit=30):
            title_lower = post.title.lower()
            flair = (post.link_flair_text or "").lower()
            if not any(p in title_lower for p in PLATFORMS):
                continue
            if flair and not any(f in flair for f in FLAIR_INCLUDE):
                continue
            results.append({"id": post.id, "title": post.title, "url": post.url, "permalink": f"https://reddit.com{post.permalink}"})
    finally:
        await reddit.close()
    return results


async def get_free_games(pool: asyncpg.Pool) -> discord.Embed:
    rows = await pool.fetch(
        "SELECT reddit_id, title, url FROM freegame_seen ORDER BY seen_at DESC LIMIT 10"
    )
    embed = discord.Embed(title="🎮 Jogos Gratuitos", color=discord.Color.green())
    if not rows:
        embed.description = "Nenhum jogo gratuito detectado recentemente. Os alertas são atualizados automaticamente a cada hora."
        return embed
    for row in rows:
        embed.add_field(name=row["title"], value=f"[Pegar aqui]({row['url']})", inline=False)
    embed.set_footer(text="Fonte: r/FreeGameFindings • Atualizado a cada hora")
    return embed
