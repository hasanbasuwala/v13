 import random


USER_AGENTS = [

    "Mozilla/5.0 Chrome",

    "Mozilla/5.0 Safari",

    "Mozilla/5.0 Firefox"
]


class SecurityManager:

    @staticmethod
    def get_headers():

        return {

            "User-Agent":
                random.choice(
                    USER_AGENTS
                ),

            "Accept":
                "*/*"
        }

    @staticmethod
    def load_cookies():

        return {}

    @staticmethod
    def rotate_fingerprint():

        return {

            "fingerprint":
                random.randint(
                    10000,
                    99999
                )
        }