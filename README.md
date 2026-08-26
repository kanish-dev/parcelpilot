# 📦 ParcelPilot Support Agent

ParcelPilot is an AI-driven support agent system built on the LangGraph framework. It features a conversational AI agent designed to assist users (both Customers and Support Agents) by providing answers regarding policies, querying structured records, and allowing escalated ticket actions.

## 🌟 Key Features

- **Conversational AI Interface:** Built with Streamlit for a seamless chat-like user experience.
- **LangGraph Orchestration:** Utilizes LangGraph to maintain state, enforce guardrails, and control conversational loops.
- **Role-Based Access Control (RBAC):** 
  - **Customers** are bound to their specific `account_id` and can only access their own data.
  - **Support Agents** have broader access and can query data across different accounts.
- **Human-in-the-Loop:** Safety first. Actions that change the state of external systems (e.g., escalating a ticket) pause automated execution and require explicit user confirmation.
- **Advanced Retrieval-Augmented Generation (RAG):**
  - **FAISS:** Used for querying unstructured company policies and Standard Operating Procedures (SOPs).
  - **ChromaDB:** Used for structured or account-scoped data retrieval.
- **High-Performance LLM:** Powered by `ChatGroq` (using OSS models) to ensure fast and responsive conversational support.

## 🏗️ Architecture Overview

The core of ParcelPilot is a directed state graph containing the following nodes:

1. **StateGraph:** Maintains conversational state, pending confirmations, account IDs, and user roles.
2. **Guardrail Node:** Runs early safety and boundary checks (e.g., blocking toxic requests) before hitting the primary agent.
3. **Agent Node:** A LangChain conversational agent powered by Groq. It determines whether to respond to the user directly or invoke a tool.
4. **Tool Node:** Executes defined tools and intercepts state-changing actions to require human confirmation.

For more detailed technical decisions, see [architecture.md](architecture.md).

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A [Groq API Key](https://console.groq.com/)

### Installation

1. **Clone the repository (or navigate to the project directory):**
   ```bash
   cd parcelpilot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   # Add any other required keys (e.g., Google/OpenAI if using their embeddings)
   ```

### Running the Application

To launch the interactive chat interface, run the Streamlit app:

```bash
streamlit run ui/chat.py
```

This will open the application in your default web browser. From the sidebar, you can switch between "Customer" and "Support Agent" roles and test the RBAC capabilities.

## 🗂️ Project Structure

- `app/`: Core application logic.
  - `agents/`: LangGraph nodes, guardrails, and agent definitions.
  - `services/`: Tools and external system integrations.
  - `main.py`: LangGraph graph construction and routing logic.
- `ui/`: Streamlit frontend application (`chat.py`).
- `data/`, `chroma_db/`, `faiss_index/`: Vector store persistent data and document sources.
- `architecture.md`: Detailed architecture and design documentation.

## 📐 4. Architecture Note

- **Agent design:** Designed as a directed state graph using LangGraph. The `StateGraph` maintains the conversational state, including messages, `pending_confirmation`, `account_id`, and `user_role`. A `Guardrail Node` precedes the `Agent Node` to block toxic or out-of-bounds requests. The `Agent Node` is powered by a `ChatGroq` LLM (e.g., `openai/gpt-oss-120b`).
- **Tool design:** Tools are decoupled from the agent logic. They include read-only tools like `search_policies` (FAISS) and `lookup_record` (ChromaDB), and state-changing tools like `escalate_ticket`. State-changing tools return a `PENDING_CONFIRMATION` signal that pauses the graph, enforcing a Human-in-the-Loop check before executing the actual function.
- **Document and structured-data handling:** Unstructured documents (policies, SOPs) are embedded and stored in FAISS for fast similarity search. Structured data (account and order records) are stored in ChromaDB, which allows filtering by `account_id` via metadata to ensure strict RBAC.
- **Source reliability and conflict handling:** Context is injected into the LLM prompt with explicit metadata (e.g., Source Document or Record Sheet). The system relies on the LLM to synthesize conflicting information based on the recency or authority specified in the retrieved chunks. RAG retrieves top-k chunks, and the guardrail ensures responses remain within domain boundaries.
- **Major technical trade-offs:** 
    - Using dual vector stores (FAISS for unstructured, ChromaDB for structured) adds complexity but optimizes for their respective strengths (FAISS for pure speed, ChromaDB for metadata filtering). 
    - Relying on Groq provides exceptional speed but requires fallback logic if rate limits are hit.
    - LangGraph offers fine-grained control over loops and human-in-the-loop pauses but requires more boilerplate than a simple Langchain AgentExecutor.
