from typing import List
import os
import json
import asyncio
import time
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from src.common.llm.agent import create_llm_agent
from docling_core.types.doc import DoclingDocument
from dotenv import load_dotenv

load_dotenv()


generator_prompt = """You are a helpful assistant that generates high-quality and diverse question-answer pairs from scientific articles.

You will be given a research article in markdown format related to insomnia. Your task is to generate up to 5 diverse (query, groundtruth, reference_context) triplets based solely on the content of the document.

Guidelines:
- The queries should focus on insomnia in a broad sense, such as related phenomena, mechanisms, observations, or implications found in the article.
- Include a mix of simple (e.g., factual or definitional) and complex (e.g., reasoning, implication, or comparative) questions to ensure diversity.
- The groundtruth must be a faithful answer to the query and **must be explicitly supported** by the document.
- The reference_context should be a sentence or paragraph **from the document** that provides clear evidence for the answer.
- Do not include questions about author information, affiliations, citations, references, figures, tables, footnotes, or other publication metadata.
- Ensure all queries are natural, informative, and relevant to someone seeking to understand insomnia using the document.

Output a list of up to 5 (query, groundtruth, reference_context) triplets."""


class GeneratorDeps(BaseModel):
    """
    Input schema for the question generation agent.

    The input is a scientific article in markdown format, covering content related to insomnia.
    """

    document: str = Field(
        description="The research article in markdown format, related to insomnia."
    )


class QueryGroundtruthPair(BaseModel):
    """
    A single question-answer pair with reference context from the article.

    - 'query' is a natural-language question about insomnia, inspired by the article.
    - 'groundtruth' is a faithful answer, supported by the document.
    - 'reference_context' is the excerpt from the article that backs up the groundtruth.
    """

    query: str = Field(
        description="A natural question derived from the document, related to insomnia."
    )
    groundtruth: str = Field(
        description="A faithful answer to the query, explicitly supported by the document."
    )
    reference_context: str = Field(
        description="A sentence or paragraph from the document that supports the groundtruth."
    )


class GeneratorOutput(BaseModel):
    """
    The final output containing up to 5 question-answer-reference triplets.
    """

    query_groundtruth_pairs: List[QueryGroundtruthPair] = Field(
        description="A list of up to 5 (query, groundtruth, reference_context) triplets extracted from the document."
    )


def create_generator() -> Agent:
    generator_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash-lite",
        system_prompt=generator_prompt,
        result_type=GeneratorOutput,
        deps_type=GeneratorDeps,
    )

    @generator_agent.system_prompt
    def add_context(ctx: RunContext[str]):
        return f"=== Document Content ===\n{ctx.deps.document}"

    return generator_agent


generator = create_generator()


async def generate_query_groundtruth_index(
    root_dir="./temp_extracted_data",
    output_json="query_groundtruth_index.json",
    processed_json="processed.json",
    max_requests_per_minute=15,
):
    """
    For each aspect and subfolder, load document.json, convert to markdown, run the generator,
    and collect all query-groundtruth-reference_context triplets with aspect and filename.
    Save the results to a JSON file as soon as possible.
    Respects a rate limit of max_requests_per_minute.
    Keeps track of processed subfolders in processed_json to avoid reprocessing.
    """
    aspects = ["suggestions", "harms", "factors"]
    results = []
    tasks = []
    jobs = []
    processed = set()
    # Load processed set if exists
    if os.path.exists(processed_json):
        with open(processed_json, "r") as f:
            try:
                processed = set(json.load(f))
            except Exception:
                processed = set()
    # Open output file in append mode if exists, else create
    if os.path.exists(output_json):
        with open(output_json, "r") as f:
            try:
                results = json.load(f)
            except Exception:
                results = []
    # Gather jobs
    for aspect in aspects:
        aspect_path = os.path.join(root_dir, aspect)
        if not os.path.isdir(aspect_path):
            continue
        for subfolder in os.listdir(aspect_path):
            subfolder_path = os.path.join(aspect_path, subfolder)
            doc_json_path = os.path.join(subfolder_path, "document.json")
            job_id = f"{aspect}/{subfolder}"
            if os.path.isdir(subfolder_path) and os.path.isfile(doc_json_path):
                if job_id in processed:
                    continue
                jobs.append((aspect, subfolder, doc_json_path, job_id))

    semaphore = asyncio.Semaphore(1)
    request_times = []

    async def process_job(aspect, subfolder, doc_json_path, job_id):
        nonlocal request_times, results, processed
        try:
            doc = DoclingDocument.load_from_json(doc_json_path)
            markdown_text = doc.export_to_markdown()
            # Rate limiting logic
            async with semaphore:
                now = time.monotonic()
                request_times = [t for t in request_times if now - t < 60]
                if len(request_times) >= max_requests_per_minute:
                    sleep_time = 60 - (now - request_times[0])
                    if sleep_time > 0:
                        print(f"[RATE LIMIT] Sleeping for {sleep_time:.2f} seconds...")
                        await asyncio.sleep(sleep_time)
                    now = time.monotonic()
                    request_times = [t for t in request_times if now - t < 60]
                request_times.append(time.monotonic())
                output = await generator.run(
                    user_prompt="", deps=GeneratorDeps(document=markdown_text)
                )
            for pair in output.output.query_groundtruth_pairs:
                results.append(
                    {
                        "aspect": aspect,
                        "filename": subfolder,
                        "query": pair.query,
                        "groundtruth": pair.groundtruth,
                        "reference_context": pair.reference_context,
                    }
                )
            # Save results and processed after each job
            with open(output_json, "w") as f:
                json.dump(results, f, indent=2)
            processed.add(job_id)
            with open(processed_json, "w") as f:
                json.dump(list(processed), f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed for {aspect}/{subfolder}: {e}")

    for job in jobs:
        tasks.append(process_job(*job))
    await asyncio.gather(*tasks)
    print(
        f"Generated {len(results)} query-groundtruth-reference_context triplets. Output written to {output_json}"
    )


if __name__ == "__main__":
    print("Starting query-groundtruth dataset generation...")
    asyncio.run(generate_query_groundtruth_index())
    print("Done.")
