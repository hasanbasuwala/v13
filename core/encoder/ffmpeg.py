import asyncio
from pathlib import Path


class FFmpegEncoder:

    @staticmethod
    async def encode(input_file: Path, output_file: Path):

        process = await asyncio.create_subprocess_exec(

            "ffmpeg",

            "-y",

            "-i",
            str(input_file),

            "-c:v",
            "libx264",

            "-preset",
            "medium",

            "-crf",
            "23",

            "-c:a",
            "aac",

            str(output_file),

            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:

            raise Exception(
                stderr.decode()
            )

        return True