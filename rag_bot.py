import os
import shutil
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# THE MODERN FIX: Importing from the fresh standalone package
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("❌ Please set your OPENAI_API_KEY in the terminal!")

HUMAN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_html_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
        script.decompose()
    clean_text = soup.get_text(separator="\n")
    return "\n".join([line.strip() for line in clean_text.splitlines() if line.strip()])

def crawl_site_pages(root_url, max_pages=3):
    pages_text_pool = []
    visited_urls = set()
    urls_to_visit = [root_url]
    base_domain = urlparse(root_url).netloc
    
    print(f"\n🌐 Starting Crawler on domain: {base_domain}")
    
    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop(0)
        if current_url in visited_urls:
            continue
            
        try:
            print(f"📄 Crawling Page ({len(visited_urls) + 1}/{max_pages}): {current_url}")
            response = requests.get(current_url, headers=HUMAN_HEADERS, timeout=5)
            if response.status_code != 200:
                continue
                
            visited_urls.add(current_url)
            page_text = clean_html_text(response.text)
            pages_text_pool.append(page_text)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for anchor in soup.find_all('a', href=True):
                href = anchor['href']
                full_url = urljoin(current_url, href)
                if urlparse(full_url).netloc == base_domain and full_url not in visited_urls:
                    urls_to_visit.append(full_url)
                    
        except Exception as e:
            print(f"⚠️ Skipped link due to error: {current_url}")
            
    return "\n\n--- NEW PAGE SEPARATOR ---\n\n".join(pages_text_pool)

if __name__ == "__main__":
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
        
    print("\n--- DEEP MULTI-PAGE RAG CRAWLER WITH CONTINUOUS CHAT ---")
    link_input = input("Paste a website homepage URL to crawl (Enter for Wikipedia Python): ").strip()
    if not link_input:
        link_input = "https://www.wikipedia.org/"
        
    combined_site_text = crawl_site_pages(link_input, max_pages=3)
    
    print("\n🤖 Step 2: Chunking all gathered text...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = text_splitter.create_documents([combined_site_text])

    print("🤖 Step 3: Indexing data into local Chroma DB...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    system_prompt = (
        "You are an analytical assistant. Answer the question using the gathered multi-page web context.\n\n"
        "{context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    print("\n✅ Database ready! You can now ask unlimited questions about this site.")
    print("👉 Type 'exit' at any time to quit the program.")

    while True:
        print("\n" + "_"*50)
        user_question = input("\n💬 Ask a question about the website: ").strip()
        
        if user_question.lower() == 'exit':
            print("\n👋 Closing the session. Great job today!")
            break
            
        if not user_question:
            print("⚠️ Please enter a real question.")
            continue
            
        print("🔍 Searching database...")
        response = rag_chain.invoke({"input": user_question})
        
        print("\n🤖 AI ANSWER:")
        print(response["answer"])
