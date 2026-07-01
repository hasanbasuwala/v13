import asyncio

from pyrogram.errors import (

    FloodWait,

    RPCError
)

from core.encoder.metadata import (
    MetadataExtractor
)


class TelegramUploader:

    MAX_RETRIES = 5

    @classmethod
    async def upload(cls, app, job):

        metadata = MetadataExtractor.probe(
            job.output_file
        )

        for attempt in range(

            cls.MAX_RETRIES
        ):

            try:

                await app.send_video(

                    chat_id=job.user_id,

                    video=str(
                        job.output_file
                    ),

                    thumb=str(
                        job.thumbnail_file
                    ),

                    duration=metadata[
                        "duration"
                    ],

                    supports_streaming=True
                )

                return True

            except FloodWait as e:

                await asyncio.sleep(
                    e.value
                )

            except RPCError:

                await asyncio.sleep(10)

            except Exception:

                await asyncio.sleep(10)

        return False