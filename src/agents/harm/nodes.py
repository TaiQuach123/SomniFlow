import json
import asyncio
import logging
from typing import Literal
from pydantic_ai import Agent, RunContext
from langgraph.config import get_stream_writer
from src.common.llm import create_llm_agent
from src.agents.base import (
    TaskHandlerDeps,
    EvaluatorDeps,
    ExtractorDeps,
    ReflectionDeps,
    TaskHandlerOutput,
    EvaluatorOutput,
    ExtractorOutput,
    ReflectionOutput,
)
from src.agents.harm.prompts import (
    harm_task_handler_prompt,
    harm_evaluator_prompt,
    extractor_agent_prompt,
    reflection_agent_prompt,
)
from src.agents.harm.states import HarmState
from src.tools.rag.retrieve import retrieve_batch
from src.tools.utils.resource_manager import get_resource_manager
from src.tools.utils.formatters import (
    get_rag_sources,
    format_rag_sources,
    get_web_sources,
    format_web_sources,
)
from langgraph.graph import END
from langgraph.types import Command

from src.common.logging import get_logger

# logger = get_logger("my_app")
# logging.getLogger("httpx").setLevel(logging.WARNING)


def create_harm_task_handler_agent() -> Agent:
    task_handler_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash-lite",
        system_prompt=harm_task_handler_prompt,
        result_type=TaskHandlerOutput,
        deps_type=TaskHandlerDeps,
    )

    @task_handler_agent.system_prompt
    def add_task_and_feedback(ctx: RunContext[str]):
        return f"=== Task ===\n{ctx.deps.task}\n\n=== Feedback (if any) ===\n{ctx.deps.feedback}"

    return task_handler_agent


def create_harm_evaluator_agent() -> Agent:
    evaluator_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash-lite",
        system_prompt=harm_evaluator_prompt,
        result_type=EvaluatorOutput,
        deps_type=EvaluatorDeps,
    )

    @evaluator_agent.system_prompt
    def add_context(ctx: RunContext[str]):
        context = f"=== Task ===\n{ctx.deps.task}\n\n=== Sub-Queries ===\n"
        for i in range(len(ctx.deps.queries)):
            context += f"{i + 1}. {ctx.deps.queries[i]}\n"

        context += f"\n=== Retrieval Results ===\n{ctx.deps.retrieval_results}\n\n=== Previous Filtered Context (if any) ===\n{ctx.deps.previous_filtered_context}"

        return context

    return evaluator_agent


def create_harm_extractor_agent() -> Agent:
    extractor_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash",
        system_prompt=extractor_agent_prompt,
        result_type=ExtractorOutput,
        deps_type=ExtractorDeps,
    )

    @extractor_agent.system_prompt
    def add_context(ctx: RunContext[str]):
        return f"=== Task ===\n{ctx.deps.task}\n\n=== List of Retrieved Contexts ===\n{ctx.deps.contexts}"

    return extractor_agent


def create_harm_reflection_agent() -> Agent:
    reflection_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash-lite",
        system_prompt=reflection_agent_prompt,
        result_type=ReflectionOutput,
        deps_type=ReflectionDeps,
    )

    @reflection_agent.system_prompt
    def add_context(ctx: RunContext[str]):
        return f"=== Task ===\n{ctx.deps.task}\n\n=== Extracted Contexts ===\n{ctx.deps.extracted_contexts}"

    return reflection_agent


async def task_handler_node(state: HarmState):
    # logger.info("Harm Task Handler Node")
    print("=== Harm Task Handler Node ===")
    harm_task_handler_agent = create_harm_task_handler_agent()
    res = await harm_task_handler_agent.run(
        "",
        deps=TaskHandlerDeps(
            task=state["harm_task"], feedback=state.get("feedback", "")
        ),
        model_settings={"temperature": 0.0},
    )

    return {"queries": res.output.queries}


async def retriever(
    state: HarmState,
) -> Command[Literal["context_processor_node", END]]:
    # logger.info("Harm Retriever Node")
    print("=== Harm Retriever Node ===")
    writer = get_stream_writer()
    rag_sources = state.get("rag_sources", {})
    web_sources = state.get("web_sources", {})

    # If not the first loop
    previous_filtered_context = []
    for source in rag_sources:
        if rag_sources[source]["filtered_contexts"]:
            previous_filtered_context.extend(rag_sources[source]["filtered_contexts"])

    for source in web_sources:
        if web_sources[source]["filtered_contexts"]:
            previous_filtered_context.extend(web_sources[source]["filtered_contexts"])

    if len(previous_filtered_context) > 0:
        previous_filtered_context = "\n\n===\n\n".join(previous_filtered_context)
    else:
        previous_filtered_context = ""

    print("Previous Filtered Context: ", previous_filtered_context)

    writer(
        json.dumps({"type": "retrievalStart", "data": "Searching RAG", "agent": "harm"})
        + "\n"
    )
    writer(
        json.dumps(
            {
                "type": "retrievalQueries",
                "data": state["queries"],
                "messageId": state["messageId"],
                "agent": "harm",
            }
        )
        + "\n"
    )

    rag_results = await retrieve_batch(
        queries=state["queries"],
        collection_name="harms",
    )

    rag_sources = get_rag_sources(rag_results, rag_sources)

    writer(
        json.dumps({"type": "retrievalSources", "data": rag_sources, "agent": "harm"})
        + "\n"
    )
    writer(json.dumps({"type": "retrievalEnd", "agent": "harm"}) + "\n")
    print("Harm RAG Sources:", rag_sources.keys())
    rag_contexts = format_rag_sources(rag_sources)

    writer(
        json.dumps(
            {
                "type": "evaluationStart",
                "data": "Local Storage Evaluation",
                "messageId": state["messageId"],
                "agent": "harm",
            }
        )
        + "\n"
    )
    harm_evaluator = create_harm_evaluator_agent()
    evaluator_result = await harm_evaluator.run(
        "",
        deps=EvaluatorDeps(
            task=state["harm_task"],
            queries=state["queries"],
            retrieval_results=rag_contexts,
            previous_filtered_context=previous_filtered_context,
        ),
        model_settings={"temperature": 0.0},
    )

    writer(
        json.dumps(
            {
                "type": "evaluationEnd",
                "data": "Local Storage Evaluation",
                "messageId": state["messageId"],
                "agent": "harm",
            }
        )
        + "\n"
    )

    if evaluator_result.output.should_proceed:
        for source in rag_sources:
            chunks = "\n---\n".join(rag_sources[source]["chunks"])
            rag_sources[source]["filtered_contexts"].append(chunks)

        return Command(
            goto=END,
            update={
                "harm_context": {
                    "rag_sources": rag_sources,
                    "web_sources": web_sources,
                },
                "rag_sources": {},
                "web_sources": {},
            },
        )
    else:
        if evaluator_result.output.new_queries:
            search_queries = evaluator_result.output.new_queries
        else:
            search_queries = state["queries"]

        writer(
            json.dumps(
                {
                    "type": "webSearchStart",
                    "data": "Searching Web",
                    "agent": "harm",
                }
            )
            + "\n"
        )
        writer(
            json.dumps(
                {
                    "type": "webSearchQueries",
                    "data": search_queries,
                    "messageId": state["messageId"],
                    "agent": "harm",
                }
            )
            + "\n"
        )
        ### Web Search
        web_search_pipeline = get_resource_manager().web_search_pipeline

        (
            unique_url_summaries,
            per_query_top_results,
        ) = await web_search_pipeline.gather_top_ranked_urls_for_queries(search_queries)

        writer(
            json.dumps(
                {
                    "type": "webSearchSources",
                    "data": unique_url_summaries,
                    "messageId": state["messageId"],
                    "agent": "harm",
                }
            )
            + "\n"
        )
        scrape_task = asyncio.create_task(
            web_search_pipeline.scrape_unique_urls(per_query_top_results)
        )
        embedding_task = asyncio.create_task(
            web_search_pipeline.get_query_embeddings_for_queries(search_queries)
        )

        url_to_content, query_embeddings = await asyncio.gather(
            scrape_task, embedding_task
        )

        web_results = await web_search_pipeline.extract_relevant_snippets_for_queries(
            search_queries, per_query_top_results, url_to_content, query_embeddings
        )

        # logger.info(f"Web Results: {web_results}")

        web_sources = get_web_sources(web_results, state.get("web_sources", {}))

        print("Harm Web Sources: ", web_sources.keys())

        writer(json.dumps({"type": "webSearchEnd", "agent": "harm"}) + "\n")

        return Command(
            goto="context_processor_node",
            update={
                "web_sources": web_sources,
                "rag_sources": rag_sources,
            },
        )


async def context_processor_node(
    state: HarmState,
) -> Command[Literal["task_handler_node", END]]:
    # logger.info("Harm Context Processor Node")
    print("=== Harm Context Processor Node ===")
    writer = get_stream_writer()
    writer(
        json.dumps(
            {
                "type": "contextExtractionStart",
                "data": "Context Extraction",
                "agent": "harm",
            }
        )
        + "\n"
    )
    extractor_agent = create_harm_extractor_agent()
    rag_sources = state.get("rag_sources", {})
    web_sources = state.get("web_sources", {})
    rag_contexts = format_rag_sources(rag_sources)
    web_contexts = format_web_sources(web_sources, len(rag_sources))
    merged_contexts = "\n\n===\n\n".join([rag_contexts, web_contexts])
    extractor_result = await extractor_agent.run(
        "",
        deps=ExtractorDeps(task=state["harm_task"], contexts=merged_contexts),
        model_settings={"temperature": 0.0},
    )
    # print("Extractor Result: ", extractor_result.output.extracted_contexts)

    for extracted_context in extractor_result.output.extracted_contexts:
        if extracted_context.url_or_source in rag_sources:
            rag_sources[extracted_context.url_or_source]["filtered_contexts"].append(
                extracted_context.extracted_context
            )
        else:
            web_sources[extracted_context.url_or_source]["filtered_contexts"].append(
                extracted_context.extracted_context
            )

    rag_filtered_contexts = "\n\n===\n\n".join(
        [
            "\n---\n".join(rag_sources[source]["filtered_contexts"])
            for source in rag_sources
            if rag_sources[source]["filtered_contexts"]
        ]
    )
    web_filtered_contexts = "\n\n===\n\n".join(
        [
            "\n---\n".join(web_sources[source]["filtered_contexts"])
            for source in web_sources
            if web_sources[source]["filtered_contexts"]
        ]
    )
    merged_filtered_contexts = "\n\n===\n\n".join(
        [rag_filtered_contexts, web_filtered_contexts]
    )
    print("Merged Filtered Contexts: ", merged_filtered_contexts)

    writer(
        json.dumps(
            {
                "type": "contextExtractionEnd",
                "data": "Context Extraction",
                "agent": "harm",
            }
        )
        + "\n"
    )

    writer(
        json.dumps({"type": "reflectionStart", "data": "Reflection", "agent": "harm"})
        + "\n"
    )

    reflection_agent = create_harm_reflection_agent()

    reflection_result = await reflection_agent.run(
        "",
        deps=ReflectionDeps(
            task=state["harm_task"], extracted_contexts=merged_filtered_contexts
        ),
        model_settings={"temperature": 0.0},
    )

    print("Reflection Result: ", reflection_result.output.should_proceed)

    writer(
        json.dumps({"type": "reflectionEnd", "data": "Reflection", "agent": "harm"})
        + "\n"
    )

    if reflection_result.output.should_proceed or state.get("loops", 0) > 1:
        return Command(
            goto=END,
            update={
                "harm_context": {
                    "rag_sources": rag_sources,
                    "web_sources": web_sources,
                },
                "loops": 0,
                "rag_sources": {},
                "web_sources": {},
            },
        )
    else:
        return Command(
            goto="task_handler_node",
            update={
                "feedback": reflection_result.output.feedback_to_task_handler,
                "loops": state.get("loops", 0) + 1,
            },
        )
