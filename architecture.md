# ParcelPilot Solution Architecture and Technical Decisions

## 1. Solution Architecture Overview
ParcelPilot is an AI-driven support agent system built on the LangGraph framework. It features a conversational AI agent designed to assist users (both Customers and Support Agents) by providing answers regarding policies, querying structured records, and allowing escalated ticket actions. 

The architecture consists of a directed state graph containing the following key components:
- **StateGraph**: Maintains state containing the conversational `messages`, `pending_confirmation`, `account_id`, and `user_role`.
- **Guardrail Node**: Runs before the primary agent to enforce early safety or boundary checks (e.g., blocking toxic requests or enforcing domain limits). If the guardrail blocks a request, execution ends.
- **Agent Node**: A LangChain conversational agent powered by `ChatGroq` (using the model `openai/gpt-oss-120b`). It determines when to converse with the user and when to invoke tools.
- **Tool Node**: Executes defined tools. It also intercepts state-changing actions (like escalating a ticket) and pauses execution to require explicit user confirmation.

## 2. Key Product Decisions
- **Role-Based Access Control (RBAC)**: The system supports multiple roles ("Customer" and "Support Agent"). Customers are strictly bound to their own `account_id` when making queries, whereas Support Agents possess global access.
- **Human-in-the-Loop / Explicit Confirmations**: Actions that change the state of external systems (e.g., `escalate_ticket`) are designed to pause the automated execution. The UI/system awaits an explicit user approval ("PENDING_CONFIRMATION") before proceeding.
- **Conversational UI Compatibility**: The system works by maintaining a strict sequence of `BaseMessage` inputs/outputs, allowing it to seamlessly integrate into modern chat UI frontends like Streamlit.

## 3. Key Technical Decisions
- **LangGraph for Orchestration**: We chose LangGraph to have explicit control over the flow of the agent, especially for creating cyclical conversational loops and for having clear boundaries like pausing at the Tool Node for user confirmations.
- **Vector Stores for Retrieval**: 
    - **FAISS**: Chosen for querying unstructured company policies and SOPs (`search_policies`).
    - **ChromaDB**: Chosen for structured or account-scoped data retrieval (`lookup_record`), providing efficient local persistence.
- **Groq LLM Engine**: We leverage `ChatGroq` (specifically `openai/gpt-oss-120b` or similar fast OSS models via Groq) to ensure lightning-fast generation and tool-calling speeds, which is essential for responsive customer support.
- **Separation of Concerns**: Tools, nodes, and graphs are cleanly separated. `tools.py` handles business logic and retrievers, while `nodes.py` manages the LLM and tool execution logic. This ensures easier testing and scalability.
