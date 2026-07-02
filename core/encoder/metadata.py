import subprocess
import json


class MetadataExtractor:

    @staticmethod
    def probe(video):

        command = [

            "ffprobe",

            "-v",
            "quiet",

            "-print_format",
            "json",

            "-show_format",

            "-show_streams",

            str(video)
        ]

        result = subprocess.run(

            command,

            capture_output=True,
            text=True
        )

        data = json.loads(
            result.stdout
        )

        duration = int(
            float(
                data["format"]["duration"]
            )
        )

        return {

            "duration": duration
        }
