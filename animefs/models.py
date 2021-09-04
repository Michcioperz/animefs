import re

import aiohttp
from asgiref.sync import async_to_sync, sync_to_async
from django.core.cache import cache
from django.db import models
from lxml import etree

from . import anilist


class Series(models.Model):
    romaji_title = models.CharField(max_length=200)
    feed_url = models.URLField(blank=True)
    episode_offset = models.IntegerField(default=0)
    anilist_id = models.IntegerField()
    episode_extracting_regex = models.TextField(blank=True)

    def __str__(self):
        return self.romaji_title

    def progress(self):
        cacher = lambda: cache.get(f"progress/anilist_id:{self.anilist_id}")
        if cacher() is None:
            async_to_sync(anilist.current)()
        return cacher()

    async def episode_urls(self, session):
        urls = []
        if self.feed_url and self.episode_extracting_regex:
            regexp = re.compile(self.episode_extracting_regex)
            progress = (await sync_to_async(self.progress)()) + self.episode_offset
            async with session.get(self.feed_url) as resp:
                # TODO: raise for status
                content = await resp.text()
                root = etree.fromstring(content)
                for item in root.findall(".//item"):
                    title = item.findtext("title")
                    match = regexp.match(title)
                    if match:
                        episode_number = int(match.group("episode"))
                        if episode_number > progress:
                            link = item.findtext("link")
                            urls.append(link)
        return urls
