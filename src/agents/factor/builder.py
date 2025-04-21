from src.agents.factor.states import FactorState, FactorOutputState
from src.agents.factor.nodes import task_handler_node, retriever
from langgraph.graph import START, END, StateGraph


def create_factor_subgraph():
    factor_subgraph_builder = StateGraph(FactorState, output=FactorOutputState)
    factor_subgraph_builder.add_node("task_handler_node", task_handler_node)
    factor_subgraph_builder.add_node("retriever", retriever)

    factor_subgraph_builder.add_edge(START, "task_handler_node")
    factor_subgraph_builder.add_edge("task_handler_node", "retriever")
    factor_subgraph_builder.add_edge("retriever", END)

    return factor_subgraph_builder
