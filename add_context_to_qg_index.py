import json
import asyncio
import logging
import time
import sys
import os

# from src.tools.rag.retrieve import retrieve_batch
from src.common.llm import create_llm_agent
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

load_dotenv()

MAX_REQUESTS_PER_MINUTE = 10
INPUT_JSON = "query_groundtruth_index.json"
CONTEXTS_JSON = "query_groundtruth_index_with_context.json"
OUTPUT_JSON = "query_groundtruth_index_with_context_and_answer.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

response_agent_prompt = (
    "You are the Response Agent in a multi-agent system designed to assist users with questions related to insomnia.\n\n"
    "You are provided with:\n"
    "- The full chat history between the user and the system.\n"
    "- A set of retrieved context chunks.\n\n"
    "Your job is to generate a natural, helpful, well-grounded, and comprehensive response to the user's latest input based on the chat history and the available context.\n\n"
    "Guidelines:\n"
    "1. Carefully read the entire chat history to understand the user's needs and previous interactions.\n"
    "2. If the latest user input is general, conversational (e.g., greetings), or simple (e.g., 'What is insomnia?'), respond directly without using the retrieved context.\n"
    "3. If retrieved contexts are provided, synthesize them to construct a clear, informative, and comprehensive response:\n"
    "   - Address all relevant aspects of the user's query based on the available information.\n"
    "   - Integrate and connect insights from multiple context chunks when appropriate.\n"
    "   - Avoid simply listing content; instead, explain and interpret it to give the user a full understanding.\n"
    "4. Do not fabricate any information. Use only what's present in the chat history, retrieved context, or well-established general knowledge.\n"
    "5. Maintain an empathetic and supportive tone, especially when addressing health-related concerns.\n"
    "6. Do not ask the user follow-up questions or request clarification. Always generate a response based solely on the provided information.\n"
    "7. If no relevant context is available and the user's question is too specific to answer confidently, politely acknowledge the limitation and provide a general response if possible."
)


def get_response_agent() -> Agent:
    response_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.5-flash-lite-preview-06-17",
        result_type=str,
        deps_type=str,
        instructions=response_agent_prompt,
    )

    @response_agent.instructions
    def add_context(ctx: RunContext[str]):
        return f"Retrieved Contexts:\n{ctx.deps}\n"

    return response_agent


response_agent = get_response_agent()


def has_contexts(item):
    return (
        "contexts" in item
        and isinstance(item["contexts"], list)
        and len(item["contexts"]) > 0
        and all(isinstance(ctx, str) and ctx.strip() for ctx in item["contexts"])
    )


async def fill_missing_answers():
    """
    Reads OUTPUT_JSON, fills missing or empty 'answer' fields using response_agent.run,
    batching requests to respect the 30 requests/minute rate limit, and writes back the results.
    """
    # Load data
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    items_to_process = []
    for idx, item in enumerate(data):
        # Skip if 'answer' exists and is not empty
        if (
            "answer" in item
            and isinstance(item["answer"], str)
            and item["answer"].strip()
        ):
            continue
        items_to_process.append((idx, item))

    logger.info(
        f"Found {len(items_to_process)} items to process out of {len(data)} total."
    )

    batch_size = MAX_REQUESTS_PER_MINUTE
    for batch_start in range(0, len(items_to_process), batch_size):
        batch = items_to_process[batch_start : batch_start + batch_size]
        logger.info(
            f"Processing batch {batch_start // batch_size + 1} with {len(batch)} items..."
        )

        tasks = []
        for idx, item in batch:
            contexts = item.get("contexts", [])
            user_input = item.get("question", "")
            # The dependencies (contexts) are passed as deps
            tasks.append(
                response_agent.run(
                    user_prompt=user_input,
                    deps="\n\n".join(contexts) if contexts else "",
                )
            )

        # Await all tasks in the batch
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for (idx, _), result in zip(batch, results):
            if isinstance(result, Exception):
                logger.error(f"Error generating answer for item {idx}: {result}")
                data[idx]["answer"] = ""
            else:
                data[idx]["answer"] = getattr(result, "output", "")

        # Save progress after each batch
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Batch {batch_start // batch_size + 1} completed and saved.")

        # If there are more batches, sleep to respect rate limit
        if batch_start + batch_size < len(items_to_process):
            logger.info("Sleeping for 60 seconds to respect rate limit...")
            time.sleep(60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_context_to_qg_index.py [answers]")
        sys.exit(1)
    mode = sys.argv[1].lower()
    if mode == "answers":
        asyncio.run(fill_missing_answers())
    else:
        print("Invalid mode. Use 'answers'.")
        sys.exit(1)
