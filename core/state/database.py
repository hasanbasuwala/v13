import sqlite3


DB = sqlite3.connect(
    "jobs.db"
)


def init_db():

    DB.execute(

        """

        CREATE TABLE IF NOT EXISTS jobs(

            job_id TEXT PRIMARY KEY,

            url TEXT,

            stage TEXT

        )

        """
    )

    DB.commit()