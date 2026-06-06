import pandas as pd
import aiohttp
import asyncio
import re
from urllib.parse import quote

API_KEY = "18e2cbb353f6e9e61304fb49d3566eb4"
movies = pd.read_csv("movies.csv")

def clean_title(title):
    return re.sub(r"\(\d{4}\)", "", title).strip()

async def fetch_tmdb(session, title, movieId):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={quote(title)}"
    async with session.get(url) as resp:
        data = await resp.json()
        results = data.get("results", [])
        if results:
            return {"movieId": movieId, "title": title, "tmdbId": results[0]["id"]}
        else:
            return {"movieId": movieId, "title": title, "tmdbId": None}

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _, row in movies.iterrows():
            title = clean_title(str(row["title"]))
            tasks.append(fetch_tmdb(session, title, row["movieId"]))
        results = await asyncio.gather(*tasks)

        pd.DataFrame(results).to_csv("ml_to_tmdb.csv", index=False)
        print("✅ Async mapping complete with", len(results), "entries")

if __name__ == "__main__":
    asyncio.run(main())
