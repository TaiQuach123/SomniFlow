from src.agents.suggestion.states import SuggestionState, SuggestionOutputState
from src.agents.suggestion.nodes import task_handler_node, retriever
from langgraph.graph import START, END, StateGraph


def create_suggestion_subgraph():
    suggestion_subgraph_builder = StateGraph(
        SuggestionState, output=SuggestionOutputState
    )
    suggestion_subgraph_builder.add_node("task_handler_node", task_handler_node)
    suggestion_subgraph_builder.add_node("retriever", retriever)

    suggestion_subgraph_builder.add_edge(START, "task_handler_node")
    suggestion_subgraph_builder.add_edge("task_handler_node", "retriever")
    suggestion_subgraph_builder.add_edge("retriever", END)

    return suggestion_subgraph_builder
