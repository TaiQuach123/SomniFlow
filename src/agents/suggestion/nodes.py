import json
import asyncio
import logging
from typing import Literal
from pydantic_ai import Agent, RunContext
from langgraph.config import get_stream_writer
from src.common.llm import create_llm_agent
from src.agents.base import *
from src.agents.suggestion.prompts import *
from src.agents.suggestion.states import SuggestionState
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

logger = get_logger("my_app")
logging.getLogger("httpx").setLevel(logging.WARNING)


def create_suggestion_task_handler_agent() -> Agent:
    task_handler_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash",
        system_prompt=suggestion_task_handler_prompt,
        result_type=TaskHandlerOutput,
        deps_type=TaskHandlerDeps,
    )

    @task_handler_agent.system_prompt
    def add_task_and_feedback(ctx: RunContext[str]):
        return f"Task: {ctx.deps.task}\nFeedback: {ctx.deps.feedback}"

    return task_handler_agent


def create_suggestion_evaluator_agent() -> Agent:
    evaluator_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash",
        system_prompt=suggestion_evaluator_prompt,
        result_type=EvaluatorOutput,
        deps_type=EvaluatorDeps,
    )

    @evaluator_agent.system_prompt
    def add_context(ctx: RunContext[str]):
        context = f"## Original Task: {ctx.deps.task}\n\n## Sub-Queries and Retrieved Contexts:\n"
        for i in range(len(ctx.deps.queries)):
            context += f"{i + 1}. Sub-Query: {ctx.deps.queries[i]}\nRetrieved Context:\n{ctx.deps.contexts[i]}\n\n"

        return context

    return evaluator_agent


def create_suggestion_extractor_agent() -> Agent:
    extractor_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash",
        system_prompt=extractor_agent_prompt,
        result_type=ExtractorOutput,
        deps_type=ExtractorDeps,
    )

    @extractor_agent.system_prompt
    def add_context(ctx: RunContext[str]):
        return f"Task: {ctx.deps.task}\nRetrieved Contexts:\n\n{ctx.deps.contexts}"

    return extractor_agent


def create_suggestion_reflection_agent() -> Agent:
    reflection_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash",
        system_prompt=reflection_agent_prompt,
        result_type=ReflectionOutput,
        deps_type=ReflectionDeps,
    )

    @reflection_agent.system_prompt
    def add_context(ctx: RunContext[str]):
        return f"Task: {ctx.deps.task}\nExtracted Contexts:\n\n{ctx.deps.extracted_contexts}"

    return reflection_agent


async def task_handler_node(state: SuggestionState):
    logger.info("Suggestion Task Handler Node")
    suggestion_task_handler_agent = create_suggestion_task_handler_agent()
    res = await suggestion_task_handler_agent.run(
        "",
        deps=TaskHandlerDeps(
            task=state["suggestion_task"], feedback=state.get("feedback", "")
        ),
        model_settings={"temperature": 0.0},
    )

    return {"queries": res.output.queries}


async def retriever(
    state: SuggestionState,
) -> Command[Literal["context_processor_node", END]]:
    logger.info("Suggestion Retriever Node")
    writer = get_stream_writer()
    writer(json.dumps({"type": "retrievalStart", "data": "Searching RAG"}) + "\n")
    writer(
        json.dumps(
            {
                "type": "retrievalQueries",
                "data": state["queries"],
                "messageId": state["messageId"],
            }
        )
        + "\n"
    )

    rag_results = await retrieve_batch(
        queries=state["queries"],
        collection_name="test",
    )

    rag_sources = get_rag_sources(rag_results, state.get("rag_sources", {}))
    # writer(
    #     json.dumps(
    #         {
    #             "type": "rag_sources",
    #             "data": rag_sources,
    #             "messageId": state["messageId"],
    #         }
    #     )
    #     + "\n"
    # )
    writer(json.dumps({"type": "retrievalSources", "data": rag_sources}) + "\n")
    writer(json.dumps({"type": "retrievalEnd"}) + "\n")
    print("RAG Sources:", rag_sources.keys())
    rag_contexts = format_rag_sources(rag_sources)

    writer(
        json.dumps(
            {
                "type": "step",
                "data": "Local Storage Evaluation",
                "messageId": state["messageId"],
            }
        )
        + "\n"
    )
    suggestion_evaluator = create_suggestion_evaluator_agent()
    evaluator_result = await suggestion_evaluator.run(
        "",
        deps=EvaluatorDeps(
            task=state["suggestion_task"],
            queries=state["queries"],
            contexts=rag_contexts,
        ),
        model_settings={"temperature": 0.0},
    )

    if evaluator_result.output.should_proceed:
        writer(json.dumps({"type": "sources", "data": [rag_sources]}) + "\n")
        writer(
            json.dumps(
                {
                    "type": "taskEnd",
                    "messageId": state["messageId"],
                    "at_node": "retriever",
                }
            )
            + "\n"
        )
        return Command(
            goto=END,
            update={
                "suggestion_context": rag_contexts,
                "rag_sources": {},
            },
        )
    else:
        if evaluator_result.output.new_queries:
            search_queries = evaluator_result.output.new_queries
        else:
            search_queries = state["queries"]

        writer(json.dumps({"type": "webSearchStart", "data": "Searching Web"}) + "\n")
        writer(
            json.dumps(
                {
                    "type": "webSearchQueries",
                    "data": search_queries,
                    "messageId": state["messageId"],
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
        web_contexts = format_web_sources(web_sources, len(rag_sources))

        print("Web Sources: ", web_sources.keys())

        # writer(
        #     json.dumps(
        #         {
        #             "type": "sources",
        #             "data": web_sources,
        #             "messageId": state["messageId"],
        #         }
        #     )
        #     + "\n"
        # )
        writer(json.dumps({"type": "webSearchEnd"}) + "\n")

        merged_contexts = "\n\n".join([rag_contexts, web_contexts])
        return Command(
            goto="context_processor_node",
            update={
                "raw_contexts": merged_contexts,
                "web_sources": web_sources,
                "rag_sources": rag_sources,
            },
        )


async def context_processor_node(
    state: SuggestionState,
) -> Command[Literal["task_handler_node", END]]:
    logger.info("Suggestion Context Processor Node")
    writer = get_stream_writer()
    writer(json.dumps({"type": "step", "data": "Context Processing"}) + "\n")
    extractor_agent = create_suggestion_extractor_agent()
    extractor_result = await extractor_agent.run(
        "",
        deps=ExtractorDeps(
            task=state["suggestion_task"], contexts=state["raw_contexts"]
        ),
        model_settings={"temperature": 0.0},
    )
    extracted_contexts = "\n\n".join(
        [
            f"[{context.reference_number}] {context.title}\nSource: {context.url_or_source}\n{context.content}"
            for context in extractor_result.output.extracted_contexts
        ]
    )

    reflection_agent = create_suggestion_reflection_agent()

    reflection_result = await reflection_agent.run(
        "",
        deps=ReflectionDeps(
            task=state["suggestion_task"], extracted_contexts=extracted_contexts
        ),
        model_settings={"temperature": 0.0},
    )

    if reflection_result.output.should_proceed or state.get("loops", 0) > 1:
        writer(
            json.dumps(
                {
                    "type": "sources",
                    "data": [state["rag_sources"], state["web_sources"]],
                }
            )
            + "\n"
        )
        writer(
            json.dumps(
                {
                    "type": "taskEnd",
                    "messageId": state["messageId"],
                    "at_node": "context_processor",
                }
            )
            + "\n"
        )
        return Command(
            goto=END,
            update={
                "suggestion_context": extracted_contexts,
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
