from src.graph.builder import create_main_graph
from langgraph.checkpoint.memory import MemorySaver
import asyncio

workflow = create_main_graph()
graph = workflow.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "1"}}


async def main():
    while True:
        query = input("Enter query: ")
        if query == "q":
            break
        async for data in graph.astream(
            {"user_input": query}, config, stream_mode="custom"
        ):
            print(data.replace("TOKEN: ", ""), end="")


if __name__ == "__main__":
    asyncio.run(main())
