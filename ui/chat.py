# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import sys
from pathlib import Path

# Add the project root to sys.path so 'app' is resolvable
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from app.main import graph
from app.services.tools import execute_escalation

load_dotenv()

st.set_page_config(page_title="ParcelPilot Support Agent", page_icon="📦")

st.title("📦 ParcelPilot Support Agent")

# Sidebar Authentication Mock
st.sidebar.title("Login Context")
user_role = st.sidebar.selectbox("Role", ["Customer", "Support Agent"])

account_id = ""
if user_role == "Customer":
    account_id = st.sidebar.text_input("Account ID", value="ACC-1001")
    st.sidebar.caption(f"You can only access data for {account_id}.")
else:
    # Support agents have global access
    st.sidebar.caption("Support agents have global access to all accounts and policies.")

# Initialize state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_confirmation" not in st.session_state:
    st.session_state.pending_confirmation = None

# Suggested Questions
st.markdown("### Suggested Questions")
if user_role == "Customer":
    questions = [
        "Where is my package?",
        "What is your refund policy?",
        "Can I change the delivery address?"
    ]
else:
    questions = [
        f"Show me the recent shipments for {account_id if account_id else 'ACC-1001'}",
        "What is the policy for hazardous materials?",
        "Escalate ticket TICK-999 about a delayed package"
    ]

# Display questions as buttons in columns
cols = st.columns(len(questions))
for i, q in enumerate(questions):
    if cols[i].button(q, key=f"q_{i}"):
        if st.session_state.pending_confirmation:
            st.error("Please confirm or cancel the pending action first.")
        else:
            st.session_state.messages.append(HumanMessage(content=q))
            with st.spinner("Agent is thinking..."):
                inputs = {
                    "messages": st.session_state.messages,
                    "account_id": account_id,
                    "user_role": user_role
                }
                res = graph.invoke(inputs)
                st.session_state.messages = res["messages"]
                if res.get("pending_confirmation"):
                    st.session_state.pending_confirmation = res["pending_confirmation"]
                st.rerun()

# Display chat messages
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage) and msg.content:
        st.chat_message("assistant").write(msg.content)
    # We hide ToolMessages from chat by default for clean UI

# Handle pending confirmation
if st.session_state.pending_confirmation:
    st.warning("⚠️ The agent requested a state-changing action.")
    details = st.session_state.pending_confirmation["details"]
    st.write(f"**Action:** Escalate Ticket")
    st.write(f"**Details:** {details}")
    
    col1, col2 = st.columns(2)
    if col1.button("✅ Confirm Action"):
        # Execute tool
        result = execute_escalation(details.get("issue_description", ""), details.get("ticket_id", ""))
        tool_call_id = st.session_state.pending_confirmation["tool_call_id"]
        
        # Append ToolMessage and resume
        st.session_state.messages.append(ToolMessage(content=result, tool_call_id=tool_call_id))
        st.session_state.pending_confirmation = None
        
        # Resume graph
        with st.spinner("Processing..."):
            inputs = {"messages": st.session_state.messages, "account_id": account_id, "user_role": user_role}
            # Because we already updated messages, we just invoke
            res = graph.invoke(inputs)
            st.session_state.messages = res["messages"]
            st.rerun()
            
    if col2.button("❌ Cancel"):
        tool_call_id = st.session_state.pending_confirmation["tool_call_id"]
        st.session_state.messages.append(ToolMessage(content="User cancelled the action.", tool_call_id=tool_call_id))
        st.session_state.pending_confirmation = None
        
        with st.spinner("Processing..."):
            inputs = {"messages": st.session_state.messages, "account_id": account_id, "user_role": user_role}
            res = graph.invoke(inputs)
            st.session_state.messages = res["messages"]
            st.rerun()

# User Input
if prompt := st.chat_input("Ask ParcelPilot Support..."):
    # Clear any pending if user sends new message? No, disable input if pending is better, but Streamlit makes it tricky.
    if st.session_state.pending_confirmation:
        st.error("Please confirm or cancel the pending action first.")
    else:
        st.session_state.messages.append(HumanMessage(content=prompt))
        st.chat_message("user").write(prompt)
        
        with st.spinner("Agent is thinking..."):
            inputs = {
                "messages": st.session_state.messages,
                "account_id": account_id,
                "user_role": user_role
            }
            
            res = graph.invoke(inputs)
            
            # Update state with new messages
            st.session_state.messages = res["messages"]
            if res.get("pending_confirmation"):
                st.session_state.pending_confirmation = res["pending_confirmation"]
                
            st.rerun()
