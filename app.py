import os
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config(page_title="Deep Web AI Crawler", page_icon="🌐", layout="wide")
st.title("🌐 Deep Web RAG Crawler & Assistant")
st.write("Crawl any website, index its sub-links mathematically, and chat with it in real-time.")

if not os.environ.get("OPENAI_API_KEY"):
    st.error("❌ OPENAI_API_KEY not found! Please set it in your terminal environment.")
    st.stop()

HUMAN_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def clean_html_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
        script.decompose()
    return "\n".join([line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()])

def crawl_site_pages(root_url, max_pages=3):
    pages_text_pool = []
    visited_urls = set()
    urls_to_visit = [root_url]
    base_domain = urlparse(root_url).netloc
    
    status_text = st.empty()
    
    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop(0)
        if current_url in visited_urls:
            continue
            
        try:
            status_text.write(f"📄 Crawling Page ({len(visited_urls) + 1}/{max_pages}): {current_url}")
            response = requests.get(current_url, headers=HUMAN_HEADERS, timeout=5)
            if response.status_code != 200:
                continue
                
            visited_urls.add(current_url)
            pages_text_pool.append(clean_html_text(response.text))
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for anchor in soup.find_all('a', href=True):
                full_url = urljoin(current_url, anchor['href'])
                if urlparse(full_url).netloc == base_domain and full_url not in visited_urls:
                    urls_to_visit.append(full_url)
        except Exception:
            pass
            
    status_text.success(f"✅ Successfully crawled {len(visited_urls)} pages from {base_domain}!")
    return "\n\n--- PAGE SEPARATOR ---\n\n".join(pages_text_pool)

# Sidebar UI Configuration
st.sidebar.header("⚙️ Crawler Settings")
url_target = st.sidebar.text_input("Website URL to Crawl:", "https://wikipedia.org")
max_pages_select = st.sidebar.slider("Max Pages to Crawl:", min_value=1, max_value=5, value=3)

if st.sidebar.button("🚀 Crawl & Index Website"):
    with st.spinner("Scraping site architecture and running vector embeds..."):
        combined_text = crawl_site_pages(url_target, max_pages=max_pages_select)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        docs = text_splitter.create_documents([combined_text])
        
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Runs entirely in RAM to completely bypass Mac folder locking issues!
        st.session_state.vector_store = Chroma.from_documents(docs, embeddings)
        st.sidebar.success("🎉 Website successfully indexed!")

# Main Chat Window UI
st.subheader("💬 Chat with the Indexed Website")
if "vector_store" in st.session_state:
    user_query = st.text_input("Ask a question about the crawled web data:")
    if user_query:
        with st.spinner("Combing vector store database..."):
            retriever = st.session_state.vector_store.as_retriever(search_kwargs={"k": 5})
            system_prompt = "You are an analytical assistant. Answer the question using the gathered context.\n\n{context}"
            prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            rag_chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt))
            response = rag_chain.invoke({"input": user_query})
            
            st.markdown("### 🤖 AI Response:")
            st.info(response["answer"])
else:
    st.warning("👈 Please click the 'Crawl & Index Website' button in the sidebar to load data before chatting.")
