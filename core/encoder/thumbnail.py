import asyncio
from pathlib import Path


class ThumbnailGenerator:

    @staticmethod
    async def generate(video, thumb):

        process = await asyncio.create_subprocess_exec(

            "ffmpeg",

            "-y",

            "-ss",
            "00:00:03",

            "-i",
            str(video),

            "-frames:v",
            "1",

            str(thumb),

            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        await process.communicate()

        return process.returncode == 0