import json
from langchain.tools import tool
from pydantic import BaseModel, Field
from app.services.retrieval.retrievers import get_faiss_retriever, get_chroma_retriever

@tool
def search_policies(query: str) -> str:
    """Search policies, agreements, product documentation, SOPs, and other supplied documents."""
    retriever = get_faiss_retriever()
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant policies found."
    return "\n\n".join([f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}" for doc in docs])

class LookupRecordInput(BaseModel):
    query: str = Field(description="The natural language query about the order, account, or ticket.")
    account_id: str = Field(description="The customer's Account ID to scope access. Mandatory for customer queries.")

@tool(args_schema=LookupRecordInput)
def lookup_record(query: str, account_id: str) -> str:
    """Query or calculate information using the supplied account, order, and ticket data."""
    try:
        retriever = get_chroma_retriever(account_id=account_id)
        docs = retriever.invoke(query)
        if not docs:
            return f"No records found for query '{query}' under account '{account_id}'."
        return "\n\n".join([f"Record Sheet: {doc.metadata.get('sheet', 'Unknown')}\n{doc.page_content}" for doc in docs])
    except Exception as e:
        return f"Error retrieving structured data: {str(e)}"

class EscalateInput(BaseModel):
    issue_description: str = Field(description="Description of the issue being escalated.")
    ticket_id: str = Field(description="The Ticket ID being escalated, if any.", default="")

@tool(args_schema=EscalateInput)
def escalate_ticket(issue_description: str, ticket_id: str = "") -> str:
    """Perform a state-changing action to escalate a ticket. Requires explicit confirmation."""
    pending_action = {
        "status": "PENDING_CONFIRMATION",
        "action": "escalate_ticket",
        "details": {
            "issue_description": issue_description,
            "ticket_id": ticket_id
        }
    }
    return json.dumps(pending_action)

def execute_escalation(issue_description: str, ticket_id: str) -> str:
    """Actual function called when confirmation is granted."""
    return f"SUCCESS: Escalation created for ticket {ticket_id}. Reason: {issue_description}"

tools = [search_policies, lookup_record, escalate_ticket]
