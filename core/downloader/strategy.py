from urllib.parse import urlparse


class DownloadStrategy:

    @staticmethod
    def choose(url):

        domain = urlparse(url).netloc.lower()

        if "youtube.com" in domain:
            return [
                "ytdlp"
            ]

        if "youtu.be" in domain:
            return [
                "ytdlp"
            ]

        if "instagram.com" in domain:
            return [
                "playwright",
                "ytdlp"
            ]

        if "facebook.com" in domain:
            return [
                "playwright",
                "ytdlp"
            ]

        if "twitter.com" in domain:
            return [
                "playwright",
                "ytdlp"
            ]

        return [

            "ytdlp",

            "playwright",

            "http"
        ]