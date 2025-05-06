from src.agents.suggestion.states import SuggestionState, SuggestionOutputState
from src.agents.suggestion.nodes import (
    task_handler_node,
    retriever,
    context_processor_node,
)
from langgraph.graph import START, StateGraph


def create_suggestion_subgraph():
    suggestion_subgraph_builder = StateGraph(
        SuggestionState, output=SuggestionOutputState
    )
    suggestion_subgraph_builder.add_node(task_handler_node)
    suggestion_subgraph_builder.add_node(retriever)
    suggestion_subgraph_builder.add_node(context_processor_node)

    suggestion_subgraph_builder.add_edge(START, "task_handler_node")
    suggestion_subgraph_builder.add_edge("task_handler_node", "retriever")
    return suggestion_subgraph_builder
