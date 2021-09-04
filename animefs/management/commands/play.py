import asyncio
from pathlib import Path
import subprocess
import tempfile
import time

import aiohttp
from asgiref.sync import async_to_sync, sync_to_async
from django.core.management.base import BaseCommand

from animefs.views import active_episodes


async def download_file(
    session: aiohttp.ClientSession, target_directory: Path, url: str
):
    async with session.get(url) as resp:
        resp.raise_for_status()
        with (target_directory / resp.url.name).open("wb") as f:
            await sync_to_async(f.write)(await resp.read())


async def download_all(target_directory, urls):
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[download_file(session, target_directory, url) for url in urls]
        )


class Command(BaseCommand):
    def handle(self, *args, **options):
        with tempfile.TemporaryDirectory(dir="/dev/shm") as root_path:
            root = Path(root_path)
            mount_dir = root / "mount"
            mount_dir.mkdir()
            torrent_dir = root / "torrent"
            torrent_dir.mkdir()
            download_dir = root / "download"
            download_dir.mkdir()
            async_to_sync(download_all)(torrent_dir, async_to_sync(active_episodes)())
            with subprocess.Popen(
                [
                    "torrentfs",
                    f"-downloadDir={download_dir}",
                    f"-mountDir={mount_dir}",
                    f"-metainfoDir={torrent_dir}",
                ],
                universal_newlines=True,
            ) as torrentfs:
                time.sleep(5)
                subprocess.call("mpv --keep-open *", shell=True, cwd=mount_dir)
