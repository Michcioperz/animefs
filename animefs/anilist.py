import warnings

from asgiref.sync import sync_to_async
import aiohttp
from django.conf import settings
from django.core.cache import cache


async def current():
    query = """
        query($username: String) {
            MediaListCollection(userName: $username, type: ANIME, status: CURRENT) {
                lists {
                    entries {
                        progress
                        media {
                            id
                            title {
                                romaji
                                english
                            }
                        }
                    }
                }
                hasNextChunk
            }
        }
    """
    # TODO: cache session?
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://graphql.anilist.co",
            json={"query": query, "variables": {"username": settings.ANILIST_USERNAME}},
        ) as resp:
            # TODO: raise for status
            data = (await resp.json())["data"]["MediaListCollection"]
            if data["hasNextChunk"]:
                warnings.warn(
                    "Anilist data for this profile require pagination, not currently supported."
                )
            restructured = [
                {
                    "anilist_id": entry["media"]["id"],
                    "romaji_title": entry["media"]["title"]["romaji"],
                    "progress": entry["progress"],
                }
                for coll in data["lists"]
                for entry in coll["entries"]
            ]
            for series in restructured:
                await sync_to_async(cache.set)(
                    f"progress/anilist_id:{series['anilist_id']}", series["progress"]
                )
            return restructured
