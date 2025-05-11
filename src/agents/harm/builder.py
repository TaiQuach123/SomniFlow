from src.agents.harm.states import HarmState, HarmOutputState
from src.agents.harm.nodes import (
    task_handler_node,
    retriever,
    context_processor_node,
)
from langgraph.graph import START, StateGraph


def create_harm_subgraph():
    harm_subgraph_builder = StateGraph(HarmState, output=HarmOutputState)
    harm_subgraph_builder.add_node(task_handler_node)
    harm_subgraph_builder.add_node(retriever)
    harm_subgraph_builder.add_node(context_processor_node)

    harm_subgraph_builder.add_edge(START, "task_handler_node")
    harm_subgraph_builder.add_edge("task_handler_node", "retriever")
    return harm_subgraph_builder
