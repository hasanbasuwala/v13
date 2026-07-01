import aiohttp


class HTTPDownloader:

    @staticmethod
    async def download(job):

        output = (
            job.work_dir /
            "input.mp4"
        )

        async with aiohttp.ClientSession() as session:

            async with session.get(
                job.url
            ) as response:

                if response.status != 200:

                    raise Exception(
                        "HTTP failed"
                    )

                with open(
                    output,
                    "wb"
                ) as f:

                    while True:

                        chunk = await response.content.read(
                            1024 * 1024
                        )

                        if not chunk:
                            break

                        f.write(chunk)

        return True