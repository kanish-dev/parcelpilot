from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from app.agents.guardrails.guardrail import guardrail_node
from app.agents.nodes.nodes import agent_node, tool_node

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    pending_confirmation: dict
    account_id: str
    user_role: str

def router_after_guardrail(state: AgentState) -> Literal["agent", "__end__"]:
    # If guardrail added an AIMessage (blocking), end.
    if isinstance(state["messages"][-1], AIMessage):
        return "__end__"
    return "agent"

def router_after_agent(state: AgentState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "__end__"

def router_after_tools(state: AgentState) -> Literal["agent", "__end__"]:
    if state.get("pending_confirmation"):
        return "__end__" # Stop graph to get UI confirmation
    return "agent"

# Build Graph
builder = StateGraph(AgentState)
builder.add_node("guardrail", guardrail_node)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

builder.add_edge(START, "guardrail")
builder.add_conditional_edges("guardrail", router_after_guardrail)
builder.add_conditional_edges("agent", router_after_agent)
builder.add_conditional_edges("tools", router_after_tools)

graph = builder.compile()
