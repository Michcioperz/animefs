import asyncio

import aiohttp
from asgiref.sync import sync_to_async
from django.db.models import Q
from django.http import JsonResponse

from . import anilist
from .models import Series


async def dump_anilist_current(request):
    data = await anilist.current()
    return JsonResponse(data)


async def import_anilist_current(request):
    data = await anilist.current()
    created_count = 0
    for series in data:
        obj, created = await sync_to_async(Series.objects.get_or_create)(
            anilist_id=series["anilist_id"],
            defaults={"feed_url": "", "romaji_title": series["romaji_title"]},
        )
        if created:
            created_count += created
    return JsonResponse(created_count, safe=False)


async def active_episodes():
    series = await sync_to_async(list)(Series.objects.all())
    async with aiohttp.ClientSession() as session:
        episodes = [
            episode
            for feed in await asyncio.gather(
                *[serie.episode_urls(session) for serie in series]
            )
            for episode in feed
        ]
    return episodes


async def dump_active_episodes(request):
    return JsonResponse(await active_episodes(), safe=False)
