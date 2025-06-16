from typing import List
from qdrant_client.models import QueryResponse
from src.tools.web.scraper.selector import WebPageSnippets


def merge_rag_sources(*rag_sources_dicts: dict) -> dict:
    merged = {}
    for sources in rag_sources_dicts:
        for source, data in sources.items():
            if source not in merged:
                merged[source] = {
                    "title": data.get("title", ""),
                    "description": data.get("description", ""),
                    "chunks": list(data.get("chunks", [])),
                    "filtered_contexts": list(data.get("filtered_contexts", [])),
                }
            else:
                merged[source]["chunks"] = list(
                    set(merged[source]["chunks"]) | set(data.get("chunks", []))
                )
                merged[source]["filtered_contexts"] = list(
                    set(merged[source]["filtered_contexts"])
                    | set(data.get("filtered_contexts", []))
                )
    return merged


def get_rag_sources(rag_results: List[QueryResponse], source_map: dict = {}) -> dict:
    for rag_result in rag_results:
        points = rag_result.points
        for point in points:
            source = point.payload["metadata"]["source"]
            if source not in source_map:
                source_map[source] = {
                    "title": point.payload["metadata"].get("title", ""),
                    "description": point.payload["metadata"].get("description", ""),
                    "chunks": [],
                    "filtered_contexts": [],
                }
            if point.payload["content"] not in source_map[source]["chunks"]:
                source_map[source]["chunks"].append(point.payload["content"])

    return source_map


def format_rag_sources(rag_sources: dict) -> str:
    formatted_sources = []
    for i, (source, data) in enumerate(rag_sources.items()):
        chunks = "\n---\n".join(data["chunks"])
        formatted_sources.append(
            f"[{i + 1}] {data['title']}\nSource: {source}\nRetrieved Context:\n\n{chunks}"
        )

    return "\n\n===\n\n".join(formatted_sources)


def get_web_sources(
    web_search_results: List[List[WebPageSnippets]], source_map: dict = {}
) -> dict:
    for search_results in web_search_results:
        for web_page_result in search_results:
            url = web_page_result.url
            if url not in source_map:
                source_map[url] = {
                    "title": web_page_result.title,
                    "description": web_page_result.description,
                    "snippets": [],
                    "filtered_contexts": [],
                }

            for snippet in web_page_result.snippets:
                if snippet.content not in source_map[url]["snippets"]:
                    source_map[url]["snippets"].append(snippet.content)

    return source_map


def format_web_sources(web_sources: dict, i: int = 0) -> str:
    formatted_sources = []
    for source, data in web_sources.items():
        snippets = "\n---\n".join(data["snippets"])
        formatted_sources.append(
            f"[{i + 1}] {data['title']}\nURL: {source}\nDescription: {data['description']}\nRetrieved Context:\n\n{snippets}"
        )
        i += 1

    return "\n\n===\n\n".join(formatted_sources)


def merge_web_sources(*web_sources_dicts: dict) -> dict:
    merged = {}
    for sources in web_sources_dicts:
        for url, data in sources.items():
            if url not in merged:
                merged[url] = {
                    "title": data.get("title", ""),
                    "description": data.get("description", ""),
                    "snippets": list(data.get("snippets", [])),
                    "filtered_contexts": list(data.get("filtered_contexts", [])),
                }
            else:
                merged[url]["snippets"] = list(
                    set(merged[url]["snippets"]) | set(data.get("snippets", []))
                )
                merged[url]["filtered_contexts"] = list(
                    set(merged[url]["filtered_contexts"])
                    | set(data.get("filtered_contexts", []))
                )
    return merged


def format_merged_rag_sources(rag_sources: dict) -> str:
    formatted_sources = []
    for i, (source, data) in enumerate(rag_sources.items()):
        filtered_contexts = "\n---\n".join(data["filtered_contexts"])
        if not filtered_contexts:
            continue
        formatted_sources.append(
            f"[{i + 1}] {data['title']}\nSource: {source}\nRetrieved Filtered Contexts:\n\n{filtered_contexts}"
        )
    return "\n\n===\n\n".join(formatted_sources)


def format_merged_web_sources(web_sources: dict, i: int = 0) -> str:
    formatted_sources = []
    for source, data in web_sources.items():
        filtered_contexts = "\n---\n".join(data["filtered_contexts"])
        if not filtered_contexts:
            continue
        formatted_sources.append(
            f"[{i + 1}] {data['title']}\nURL: {source}\nDescription: {data['description']}\nRetrieved Filtered Contexts:\n\n{filtered_contexts}"
        )
        i += 1
    return "\n\n===\n\n".join(formatted_sources)
