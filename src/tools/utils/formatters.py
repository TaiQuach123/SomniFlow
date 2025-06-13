from typing import List, Tuple
from qdrant_client.models import QueryResponse
from src.tools.web.scraper.selector import WebPageSnippets


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
                }
            if point.payload["content"] not in source_map[source]["chunks"]:
                source_map[source]["chunks"].append(point.payload["content"])

    return source_map


def format_rag_sources(rag_sources: dict) -> str:
    formatted_sources = []
    for i, (source, data) in enumerate(rag_sources.items()):
        chunks = "\n---\n".join(data["chunks"])
        formatted_sources.append(
            f"[{i + 1}] {data['title']}\nSource: {source}\nRetrieved Content:\n\n{chunks}"
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
            f"[{i + 1}] {data['title']}\nURL: {source}\nDescription: {data['description']}\nRetrieved Content:\n\n{snippets}"
        )
        i += 1

    return "\n\n===\n\n".join(formatted_sources)


def format_web_results_with_prefix(
    web_search_results: List[List[WebPageSnippets]],
    i: int = 0,
    all_source_map: dict = {},
) -> Tuple[str, int, dict]:
    for web_search_result in web_search_results:
        for web_page_result in web_search_result:
            url = web_page_result.url
            if url not in all_source_map:
                all_source_map[url] = {
                    "title": web_page_result.title,
                    "description": web_page_result.description,
                    "contents": [],
                }
                web_page_content = "\n---\n".join(
                    [snippet.content for snippet in web_page_result.snippets]
                )
                all_source_map[url]["contents"].append(web_page_content)

    web_contexts = []
    for source, data in all_source_map.items():
        content_text = "\n---\n".join(data["contents"])
        web_contexts.append(
            f"[{i + 1}] {data['title']}\nURL: {source}\nDescription: {data['description']}\nRetrieved Content:\n\n{content_text}"
        )
        i += 1

    return "\n\n===\n\n".join(web_contexts), i, all_source_map


def format_rag_results_with_prefix(
    rag_results: List[QueryResponse], i: int = 0, all_source_map: dict = {}
) -> Tuple[str, int, dict]:
    for rag_result in rag_results:
        points = rag_result.points
        for point in points:
            source = point.payload["metadata"]["source"]
            if source not in all_source_map:
                all_source_map[source] = {
                    "title": point.payload["metadata"]["title"],
                    "contents": [],
                }
            all_source_map[source]["contents"].append(point.payload["content"])

    rag_contexts = []
    for source, data in all_source_map.items():
        content_text = "\n---\n".join(data["contents"])
        rag_contexts.append(
            f"[{i + 1}] {data['title']}\nSource: {source}\nRetrieved Content:\n\n{content_text}"
        )
        i += 1

    return "\n\n===\n\n".join(rag_contexts), i, all_source_map


def format_rag_result(rag_result: QueryResponse) -> str:
    points = rag_result.points
    source_map = {}

    for point in points:
        source = point.payload["metadata"]["source"]
        if source not in source_map:
            source_map[source] = {
                "title": point.payload["metadata"]["title"],
                "contents": [],
            }
        source_map[source]["contents"].append(point.payload["content"])

    formatted_results = []
    for source, data in source_map.items():
        content_text = "\n---\n".join(data["contents"])
        formatted_text = f"Title: {data['title']}\nSource: {source}\nRetrieved Content:\n\n{content_text}"
        formatted_results.append(formatted_text)

    result = "\n\n===\n\n".join(formatted_results)

    return result


def format_rag_results(rag_results: List[QueryResponse]) -> List[str]:
    final_results = []
    for rag_result in rag_results:
        final_results.append(format_rag_result(rag_result))

    return final_results


# def format_points(points):
#     formatted_results = []
#     for point in points:
#         formatted_text = f"Title: {point.payload['metadata']['title']}\nSource: {point.payload['metadata']['source']}\nChunk Content: {point.payload['content']}"
#         formatted_results.append(formatted_text)

#     result = "\n\n---\n\n".join(formatted_results)

#     return result
