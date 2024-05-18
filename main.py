import os
import dotenv
import aiohttp
from tqdm.auto import tqdm
import json
from pathlib import Path

dotenv.load_dotenv()
HOST = os.getenv('HOST')
TOKEN = os.getenv('TOKEN')


async def get_favorite(session: aiohttp.ClientSession):
    async with session.get(f"{HOST}/api/v2/favorite", headers={
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "dandanplay/15.4.0.0 (desktop) anixplayer/15.4.0.0"
    }) as response:
        return await response.json()


async def get_details(session: aiohttp.ClientSession, anime_id: int):
    async with session.get(f"{HOST}/api/v2/bangumi/{anime_id}", headers={
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "dandanplay/15.4.0.0 (desktop) anixplayer/15.4.0.0"
    }) as response:
        return await response.json()


async def main():
    async with aiohttp.ClientSession() as session:
        favorite = await get_favorite(session)

        output_path = Path("output")
        output_path.mkdir(exist_ok=True)

        if favorite["success"] is False:
            print(favorite)
            return

        with open(output_path / "favorite.json", "w", encoding="UTF-8") as f:
            json.dump(favorite, f, indent=4, ensure_ascii=False)

        output_detail_path = output_path / "details"
        output_detail_path.mkdir(exist_ok=True)

        for item in tqdm(favorite["favorites"]):
            anime_id = item["animeId"]
            detail = await get_details(session, anime_id)
            if detail["success"] is False:
                print(detail)
                continue
            with open(output_detail_path / f"{anime_id}.json", "w", encoding="UTF-8") as f:
                json.dump(detail["bangumi"], f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
