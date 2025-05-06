from langgraph.graph import START, END, StateGraph
from src.graph.states import MainGraphState
from src.agents.supervisor.nodes import supervisor_node, ask_human
from src.agents.response.nodes import response_node

# Import subgraphs
from src.agents.suggestion.builder import create_suggestion_subgraph
from src.agents.harm.builder import create_harm_subgraph
from src.agents.factor.builder import create_factor_subgraph


def create_main_graph():
    suggestion_subgraph_builder = create_suggestion_subgraph()
    harm_subgraph_builder = create_harm_subgraph()
    factor_subgraph_builder = create_factor_subgraph()

    workflow = StateGraph(state_schema=MainGraphState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("ask_human_node", ask_human)
    workflow.add_node("response_agent", response_node)
    workflow.add_node("suggestion_agent", suggestion_subgraph_builder.compile())
    workflow.add_node("harm_agent", harm_subgraph_builder.compile())
    workflow.add_node("factor_agent", factor_subgraph_builder.compile())

    workflow.add_edge(START, "supervisor")
    workflow.add_edge("ask_human_node", "supervisor")
    workflow.add_edge("suggestion_agent", "response_agent")
    workflow.add_edge("harm_agent", "response_agent")
    workflow.add_edge("factor_agent", "response_agent")
    workflow.add_edge("response_agent", END)

    return workflow
