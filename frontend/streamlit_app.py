import streamlit as st
import requests
import uuid

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Azure RAG Chatbot",
    page_icon="📄",
    layout="wide"
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

with st.sidebar:
    st.title("🤖 Azure RAG Chatbot")
    st.markdown("---")
    st.subheader("📂 Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")
    if uploaded_file:
        if st.button("Upload & Index", type="primary"):
            with st.spinner("Uploading to Blob Storage and indexing..."):
                try:
                    response = requests.post(
                        f"{API_URL}/upload",
                        files={"file": uploaded_file}
                    )
                    result = response.json()
                    st.success(result["message"])
                    st.info(f"Pages indexed: {result['pages']}")
                    st.session_state.uploaded_files.append(uploaded_file.name)
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")

    if st.session_state.uploaded_files:
        st.markdown("---")
        st.subheader("📚 Indexed Documents")
        for f in st.session_state.uploaded_files:
            st.write(f"✅ {f}")

    st.markdown("---")
    st.subheader("⚙️ Session Info")
    st.code(st.session_state.session_id[:8] + "...", language=None)
    if st.button("🔄 New Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("**Powered by:**")
    st.markdown("🔵 Azure Blob Storage")
    st.markdown("🔵 Azure Document Intelligence")
    st.markdown("🔵 Azure AI Search")
    st.markdown("🔵 Azure Cosmos DB")
    st.markdown("🔵 Azure OpenAI")

st.title("💬 Chat with your Documents")
st.markdown("Upload a PDF in the sidebar, then ask questions below.")
st.markdown("---")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask a question about your document..."):
    if not st.session_state.uploaded_files:
        st.warning("⚠️ Please upload a PDF first using the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating answer..."):
                try:
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "question": prompt,
                            "session_id": st.session_state.session_id
                        }
                    )
                    result = response.json()
                    answer = result["answer"]
                    sources = result["sources_used"]
                    st.write(answer)
                    st.caption(f"📎 Retrieved {sources} document chunks")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })
                except Exception as e:
                    st.error(f"Error: {str(e)}")