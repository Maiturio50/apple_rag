import os
import time
import streamlit as st
import pypdf
from openai import OpenAI

st.set_page_config(page_title="AI Book Assistant", page_icon="📚", layout="wide")
st.title("📚 AI Book Assistant & RAG Analyzer")
st.write("System operating in Direct Local Disk Mode. Reading 'dino_book.pdf' straight from your folder.")

if not os.environ.get("OPENAI_API_KEY"):
    st.error("❌ OPENAI_API_KEY not found! Please set it in your terminal environment.")
    st.stop()

client = OpenAI()

st.sidebar.header("⚙️ Local Control Center")

# This button completely replaces the old file uploader widget!
if st.sidebar.button("🚀 Process Local dino_book.pdf"):
    with st.spinner("Bypassing server buffers, sanitizing encodings, and index chunking..."):
        try:
            target_file_path = "./dino_book.pdf"
            if not os.path.exists(target_file_path):
                st.error("❌ 'dino_book.pdf' not found inside your apple_rag folder! Please make sure it's there.")
                st.stop()
                
            raw_text_pool = []
            with open(target_file_path, "rb") as file_stream:
                reader = pypdf.PdfReader(file_stream)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        clean_string = page_text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
                        if len(clean_string.strip()) > 5:
                            raw_text_pool.append(clean_string.strip())
                            
            combined_book_text = "\n\n".join(raw_text_pool)
            size = 2000
            overlap = 200
            text_chunks = []
            
            start = 0
            while start < len(combined_book_text):
                end = start + size
                chunk = combined_book_text[start:end].strip()
                if chunk:
                    text_chunks.append(str(chunk))
                start += (size - overlap)
                
            st.session_state.raw_text_chunks = text_chunks
            st.session_state.total_chunks = len(text_chunks)
            st.sidebar.success(f"🎉 Successfully indexed {len(text_chunks)} data chunks!")
        except Exception as e:
            st.error(f"❌ Structural file breakdown: {str(e)}")

st.subheader("💬 Chat with your Document")
if "raw_text_chunks" in st.session_state:
    user_query = st.text_input("Ask a question about the uploaded book:")
    if user_query:
        with st.spinner("Searching document chunks..."):
            start_time = time.time()
            matched_context_list = []
            query_words = [word.lower() for word in user_query.split() if len(word) > 3]
            for chunk in st.session_state.raw_text_chunks:
                match_score = sum(1 for word in query_words if word in chunk.lower())
                if match_score > 0:
                    matched_context_list.append(chunk)
            top_chunks = matched_context_list[:5]
            if not top_chunks:
                top_chunks = st.session_state.raw_text_chunks[:5]
            context_block = "\n\n---\n\n".join(top_chunks)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {"role": "system", "content": f"Answer using ONLY this verified context:\n\n{context_block}"},
                    {"role": "user", "content": user_query}
                ]
            )
            col1, col2 = st.columns(2)
            col1.metric("📦 Total Book Chunks Created", st.session_state.total_chunks)
            col2.metric("⏱️ Match Retrieval Speed", f"{round(time.time() - start_time, 2)} seconds")
            st.markdown("### 🤖 AI Analysis Response:")
            st.info(response.choices[0].message.content)
else:
    st.warning("👈 Please click the 'Process Local dino_book.pdf' button to load the text directly from disk.")
