"""
Streamlit frontend for AskCompany.
Features: chat UI, document upload, conversation memory, source indicators.

Run: streamlit run frontend/app.py
Requires FastAPI running: uvicorn main:app --port 8000
"""

import streamlit as st
import requests
import os

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AskCompany AI",
    page_icon="🤖",
    layout="wide"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

with st.sidebar:
    st.title("🤖 AskCompany")

    try:
        health = requests.get(f"{FASTAPI_URL}/health", timeout=3)
        if health.status_code == 200:
            st.success("✅ System Online")
        else:
            st.error("❌ API Error")
    except Exception:
        st.error("❌ API Offline\nRun: uvicorn main:app --port 8000")

    st.markdown("---")

    st.subheader("📂 Upload Document")
    st.caption("Upload a company document to make it searchable")

    uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf"])

    if uploaded_file is not None:
        if st.button("Upload & Index", type="primary"):
            with st.spinner("Uploading and indexing..."):
                try:
                    response = requests.post(
                        f"{FASTAPI_URL}/upload",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue())},
                        timeout=120
                    )
                    if response.status_code == 200:
                        st.success("✅ Uploaded and indexed!")
                        st.rerun()
                    else:
                        st.error(f"Failed: {response.json().get('detail', 'Error')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    st.markdown("---")

    st.subheader("📄 Loaded Documents")
    try:
        docs_response = requests.get(f"{FASTAPI_URL}/documents", timeout=5)
        if docs_response.status_code == 200:
            docs = docs_response.json()["documents"]
            if docs:
                for doc in docs:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        size_kb = round(doc["size_bytes"] / 1024, 1)
                        st.caption(f"📄 {doc['name']} ({size_kb} KB)")
                    with col2:
                        if st.button("🗑️", key=f"del_{doc['name']}"):
                            try:
                                del_resp = requests.delete(
                                    f"{FASTAPI_URL}/documents/{doc['name']}",
                                    timeout=30
                                )
                                if del_resp.status_code == 200:
                                    st.rerun()
                            except Exception as e:
                                st.error(str(e))
            else:
                st.caption("No documents loaded")
    except Exception:
        st.caption("Cannot fetch document list")

    st.markdown("---")

    st.subheader("💡 Try These")
    st.caption("**From Documents:**")
    st.caption("• How many leave days do I get?")
    st.caption("• What is the bonus for Outstanding rating?")
    st.caption("• What does the GenAI Bootcamp cost?")
    st.caption("")
    st.caption("**From Database:**")
    st.caption("• Who are the top 3 salespeople?")
    st.caption("• Average salary in Engineering?")
    st.caption("• Which product sold the most?")
    st.caption("")
    st.caption("**Test Memory:**")
    st.caption("• Ask about salespeople, then ask 'what city are they from?'")

    st.markdown("---")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.display_messages = []
        st.rerun()

st.title("AskCompany AI Assistant")
st.caption("Ask questions about company policies, employees, products, and sales data.")

if not st.session_state.display_messages:
    st.info("👋 Ask me anything about the company!")

for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "meta" in msg:
            meta = msg["meta"]
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                icons = {
                    "documents": "📄 Documents",
                    "database": "🗄️ Database",
                    "both": "📄🗄️ Both"
                }
                st.caption(icons.get(meta.get("source", ""), "🤖"))
            with col2:
                st.caption(f"⏱️ {meta.get('time', '?')}s")
            with col3:
                if meta.get("docs"):
                    st.caption(f"📚 {', '.join(meta['docs'])}")

if prompt := st.chat_input("Ask a question..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.display_messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{FASTAPI_URL}/ask",
                    json={
                        "question": prompt,
                        "conversation_history": st.session_state.messages[:-1]
                    },
                    timeout=90
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    st.markdown(answer)

                    meta = {
                        "source": data["source"],
                        "time": data["time_taken"],
                        "docs": data["details"].get("document_sources", [])
                    }

                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        icons = {
                            "documents": "📄 Documents",
                            "database": "🗄️ Database",
                            "both": "📄🗄️ Both"
                        }
                        st.caption(icons.get(data["source"], "🤖"))
                    with col2:
                        st.caption(f"⏱️ {data['time_taken']}s")
                    with col3:
                        if meta["docs"]:
                            st.caption(f"📚 {', '.join(meta['docs'])}")

                    st.session_state.messages.append({
                        "role": "assistant", "content": answer
                    })
                    st.session_state.display_messages.append({
                        "role": "assistant", "content": answer, "meta": meta
                    })
                else:
                    st.error(f"API Error {response.status_code}")
                    st.session_state.messages.pop()
                    st.session_state.display_messages.pop()

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Run: uvicorn main:app --port 8000")
                st.session_state.messages.pop()
                st.session_state.display_messages.pop()
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.messages.pop()
                st.session_state.display_messages.pop()
