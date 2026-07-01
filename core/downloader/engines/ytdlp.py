import asyncio


class YTDLPDownloader:

    @staticmethod
    async def download(job):

        output = str(
            job.work_dir /
            "input.mp4"
        )

        process = await asyncio.create_subprocess_exec(

            "yt-dlp",

            "-f",

            "best",

            "-o",

            output,

            job.url,

            stdout=asyncio.subprocess.PIPE,

            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:

            raise Exception(

                stderr.decode()
            )

        return True