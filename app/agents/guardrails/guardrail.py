from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq

def guardrail_node(state):
    """Check if query is safe/relevant."""
    last_message = state["messages"][-1].content
    llm = ChatGroq(model="openai/gpt-oss-120b")
    prompt = f"Is the following user query a relevant question about logistics, shipping, policies, accounts, tickets, or customer support? Answer ONLY 'YES' or 'NO'. Query: {last_message}"
    
    try:
        response = llm.invoke(prompt)
        if "NO" in response.content.upper():
            return {"messages": [AIMessage(content="I'm sorry, I can only assist with ParcelPilot support, policies, and account queries. Please ask a relevant question.")]}
    except Exception as e:
        pass # fail open
    return None
