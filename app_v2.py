import os
import time
import streamlit as st
import pypdf
import docx  # The Word document parser we just installed
from openai import OpenAI

st.set_page_config(page_title="Universal AI Knowledge Base", page_icon="🗂️", layout="wide")
st.title("🗂️ Universal AI Knowledge Base (Multi-Format RAG)")
st.write("Upload any PDF, Microsoft Word (.docx), or Plain Text (.txt) file to chat with its contents.")

if not os.environ.get("OPENAI_API_KEY"):
    st.error("❌ OPENAI_API_KEY not found! Please set it in your terminal environment.")
    st.stop()

client = OpenAI()

# --- THE UNIFIED ROUTER FUNCTION ---
def extract_text_by_format(uploaded_file):
    file_name = uploaded_file.name.lower()
    extracted_text = ""
    
    # Route 1: Handle PDF Files using our sanitized character technique
    if file_name.endswith('.pdf'):
        reader = pypdf.PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += "\n" + page_text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
                
    # Route 2: Handle Microsoft Word Documents (.docx)
    elif file_name.endswith('.docx'):
        doc = docx.Document(uploaded_file)
        for paragraph in doc.paragraphs:
            if paragraph.text:
                extracted_text += "\n" + paragraph.text
                
    # Route 3: Handle Plain Text Files (.txt)
    elif file_name.endswith('.txt'):
        extracted_text = str(uploaded_file.read(), "utf-8", errors="ignore")
        
    return extracted_text.strip()

# Sidebar Control Panel
st.sidebar.header("⚙️ Ingestion Control Center")
uploaded_file = st.sidebar.file_uploader("Upload Document (.pdf, .docx, .txt):", type=["pdf", "docx", "txt"])

if uploaded_file is not None and st.sidebar.button("🚀 Ingest & Index Document"):
    with st.spinner("Extracting structural layout data..."):
        try:
            # Run the file through our smart automated router
            raw_text = extract_text_by_format(uploaded_file)
            
            if len(raw_text) == 0:
                st.error("❌ Extracted text layer is empty.")
                st.stop()
                
            # MATCH FIX: Explicitly name this text_chunks to fix the error!
            text_chunks = []
            start = 0
            while start < len(raw_text):
                end = start + size
                chunk = raw_text[start:end].strip()
                if chunk:
                    text_chunks.append(str(chunk))
                start += (size - overlap)
                
            # Cache the arrays into Streamlit's session memory state using text_chunks
            st.session_state.v2_chunks = text_chunks
            st.session_state.v2_total = len(text_chunks)
            st.session_state.active_file_name = uploaded_file.name
            st.sidebar.success(f"🎉 Indexed '{uploaded_file.name}' into {len(text_chunks)} chunks!")
        except Exception as e:
            st.error(f"❌ Pipeline processing failure: {str(e)}")


# Interactive Chat Interface
st.subheader("💬 Query Your Universal Knowledge Base")
if "v2_chunks" in st.session_state:
    st.write(f"📁 Active Source Context: **{st.session_state.active_file_name}**")
    user_query = st.text_input("Ask a question about the document:")
    
    if user_query:
        with st.spinner("Combing text array matrices..."):
            start_time = time.time()
            
            # Simple keyword-relevance matching algorithm
            matched_context = []
            query_words = [w.lower() for w in user_query.split() if len(w) > 3]
            
            for chunk in st.session_state.v2_chunks:
                score = sum(1 for w in query_words if w in chunk.lower())
                if score > 0:
                    matched_context.append(chunk)
                    
            top_chunks = matched_context[:5]
            if not top_chunks:
                top_chunks = st.session_state.v2_chunks[:5]
                
            context_block = "\n\n---\n\n".join(top_chunks)
            
            # Request factual summary from OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {"role": "system", "content": f"Answer using ONLY this verified context:\n\n{context_block}"},
                    {"role": "user", "content": user_query}
                ]
            )
            
            duration = round(time.time() - start_time, 2)
            
            col1, col2 = st.columns(2)
            col1.metric("📦 Total Active Chunks", st.session_state.v2_total)
            col2.metric("⏱️ Execution Speed", f"{duration} seconds")
            
            st.markdown("### 🤖 AI Response:")
            st.info(response.choices[0].message.content)
else:
    st.warning("👈 Please upload a document in the sidebar and click process to initialize.")
