import asyncio
import logging

from core.downloader.strategy import DownloadStrategy

from core.downloader.engines.ytdlp_engine import (
    YTDLPDownloader
)

from core.downloader.engines.playwright_engine import (
    PlaywrightDownloader
)

from core.downloader.engines.http_engine import (
    HTTPDownloader
)


logger = logging.getLogger(__name__)


class DownloaderManager:

    MAX_RETRIES = 4

    ENGINE_MAP = {

        "ytdlp": YTDLPDownloader,

        "playwright": PlaywrightDownloader,

        "http": HTTPDownloader
    }

    @classmethod
    async def download(cls, job):

        engines = DownloadStrategy.choose(
            job.url
        )

        for attempt in range(

            cls.MAX_RETRIES
        ):

            for engine_name in engines:

                try:

                    logger.info(

                        f"{engine_name} attempt "
                        f"{attempt+1}"
                    )

                    engine = cls.ENGINE_MAP[
                        engine_name
                    ]

                    success = await engine.download(
                        job
                    )

                    if success:
                        return True

                except Exception as e:

                    logger.warning(

                        f"{engine_name} failed {e}"
                    )

            delay = 2 ** attempt

            logger.warning(

                f"Retry in {delay}s"
            )

            await asyncio.sleep(delay)

        return False