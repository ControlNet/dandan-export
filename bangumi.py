import json
from pathlib import Path
import aiohttp
from dotenv import load_dotenv
from tqdm.auto import tqdm
import os

load_dotenv()

def read_json(path: str):
    with open(path, "r", encoding="UTF-8") as f:
        return json.load(f)

HOST = "https://api.bgm.tv"
TOKEN = os.getenv("BANGUMI_TOKEN")
USER_ID = os.getenv("BANGUMI_USER_ID")

# collection type
# 1: 想看
# 2: 看过
# 3: 在看
# 4: 搁置
# 5: 抛弃

async def add_collection(details_item: dict, favorite_item: dict, session: aiohttp.ClientSession):
    # add a new collection with given subject_id, initialized with type 3
    subject_id = [int(each["url"].replace("https://bangumi.tv/subject/", ""))
        for each in details_item["onlineDatabases"] if each["name"] == "Bangumi.tv"]
    if len(subject_id) == 0:
        return
    subject_id = subject_id[0]

    data = {
        "private": False,
    }

    if details_item["favoriteStatus"] == "favorited":
        data["type"] = 3
    elif details_item["favoriteStatus"] == "finished":
        data["type"] = 2
    elif details_item["favoriteStatus"] == "abandoned":
        data["type"] = 5

    if favorite_item["episodeTotal"] == favorite_item["episodeWatched"] and favorite_item["episodeTotal"] != 0:
        data["type"] = 2

    if favorite_item["episodeTotal"] == 0:
        data["type"] = 1

    if details_item["userRating"] != 0:
        data["rate"] = details_item["userRating"]

    async with session.post(f"{HOST}/v0/users/-/collections/{subject_id}", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }, json=data) as response:
        await response.read()

    return subject_id


async def get_all_episodes(subject_id: int, session: aiohttp.ClientSession):
    async with session.get(f"{HOST}/v0/users/-/collections/{subject_id}/episodes", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }) as response:
        episodes = (await response.json())["data"]

    # build a map from episode number to episode id
    if episodes is None:
        return None
    return {episode["episode"]["ep"]: episode["episode"]["id"] for episode in episodes}

async def add_episodes(subject_id: int, details_item: dict, session: aiohttp.ClientSession):
    bangumi_episodes = await get_all_episodes(subject_id, session)
    if bangumi_episodes is None:
        return

    update_episodes = []

    for episode in details_item["episodes"]:
        try:
            episode_num = int(episode["episodeNumber"])
        except ValueError:
            # SP, OP, ED, etc
            # ignore
            continue

        if episode["lastWatched"] is not None:
            # update to bangumi
            try:
                episode_id = bangumi_episodes[episode_num]
            except KeyError:
                continue
            update_episodes.append(episode_id)

    if len(update_episodes) == 0:
        return

    # update episodes
    async with session.patch(f"{HOST}/v0/users/-/collections/{subject_id}/episodes", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }, json={
        "episode_id": update_episodes,
        "type": 2
    }) as response:
        return await response.read()

async def main():
    output_path = Path("output")
    favorite = read_json(output_path / "favorite.json")

    async with aiohttp.ClientSession() as session:
        for i, favorite_item in enumerate(tqdm(favorite)):
            dandan_id = favorite_item["animeId"]
            details_item = read_json(output_path / "details" / f"{dandan_id}.json")

            # add empty collection
            subject_id = await add_collection(details_item, favorite_item, session)
            if subject_id is None:
                continue

            # add episodes
            response = await add_episodes(subject_id, details_item, session)

if __name__ == '__main__':
    import asyncio

    asyncio.run(main())