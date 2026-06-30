# core/state/queues.py
import asyncio

download_queue = asyncio.Queue()
encode_queue = asyncio.Queue()
upload_queue = asyncio.Queue()
