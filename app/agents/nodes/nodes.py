from langchain_core.messages import ToolMessage
from langchain_groq import ChatGroq
from app.services.tools import tools, execute_escalation

from langchain_core.messages import SystemMessage

def agent_node(state):
    """Call the LLM with tools."""
    # Ensure pending_confirmation is cleared if we are back in agent
    llm = ChatGroq(model="openai/gpt-oss-120b").bind_tools(tools)
    
    role = state.get("user_role", "Customer")
    account_id = state.get("account_id", "")
    
    if role == "Support Agent":
        sys_msg = SystemMessage(content="You are a Support Agent. You have full permission to look up orders and details across all customer accounts. DO NOT ask the user for an account ID. If the user asks about an order, ticket, or issue, IMMEDIATELY use the lookup_record tool and leave the account_id field empty to perform a global search.")
    else:
        sys_msg = SystemMessage(content=f"You are a helpful assistant talking to a Customer. The customer's account ID is {account_id}. You must use this account ID for looking up records. Do not ask the user for their account ID, you already know it.")
        
    messages = [sys_msg] + list(state["messages"])
    response = llm.invoke(messages)
    
    return {"messages": [response], "pending_confirmation": None}

def tool_node(state):
    """Execute tools."""
    last_message = state["messages"][-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {"messages": []}
    
    from app.services.tools import search_policies, lookup_record
    tool_map = {"search_policies": search_policies, "lookup_record": lookup_record}
    
    responses = []
    for tool_call in last_message.tool_calls:
        # State-changing action intercept
        if tool_call["name"] == "escalate_ticket":
            pending = {
                "status": "PENDING_CONFIRMATION",
                "action": "escalate_ticket",
                "details": tool_call["args"],
                "tool_call_id": tool_call["id"]
            }
            return {"pending_confirmation": pending}
            
        # Execute normal tools
        if tool_call["name"] in tool_map:
            # Enforce access control for lookup
            if tool_call["name"] == "lookup_record":
                if state.get("user_role") == "Customer":
                    tool_call["args"]["account_id"] = state.get("account_id", "")
                
            res = tool_map[tool_call["name"]].invoke(tool_call["args"])
            responses.append(ToolMessage(content=res, tool_call_id=tool_call["id"]))
            
    return {"messages": responses}
