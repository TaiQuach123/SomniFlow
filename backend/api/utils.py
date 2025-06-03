import binascii
from typing import AsyncIterable
import os


async def generate_response(query: str, thread_id: str, graph) -> AsyncIterable[str]:
    async for data in graph.astream(
        {"user_input": query, "messageId": binascii.hexlify(os.urandom(7)).decode()},
        {"configurable": {"thread_id": thread_id}},
        stream_mode="custom",
    ):
        yield data
        print("Streaming:", data)
