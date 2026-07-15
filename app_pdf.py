from operator import itemgetter
import os
import tempfile
import hashlib
import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader  # MUCH faster parser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="Streamlit PDF RAG Agent", layout="wide")
st.title("⚡ High-Speed PDF RAG Assistant")
st.subheader("Optimized for massive documents (700+ pages)")

# Ensure OpenAI API Key is loaded
if "OPENAI_API_KEY" not in os.environ:
    api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    else:
        st.info("Please set your OPENAI_API_KEY to begin.")
        st.stop()

# Initialize conversational memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

uploaded_file = st.sidebar.file_uploader("Upload your PDF document", type=["pdf"])

if uploaded_file is not None:
    # We calculate a unique hash of the file to see if we've processed it before
    bytes_data = uploaded_file.getvalue()
    file_hash = hashlib.md5(bytes_data).hexdigest()
    persist_directory = f"./chroma_db_{file_hash}"

    st.sidebar.info("Checking for cached document data...")

    @st.cache_resource
    def get_optimized_retriever(file_bytes, persist_dir):
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Check if we have already built the database for this specific PDF file
        if os.path.exists(persist_dir):
            st.sidebar.success("⚡ Loaded cached document index instantly!")
            vectorstore = Chroma(
                persist_directory=persist_dir, 
                embedding_function=embeddings
            )
        else:
            st.sidebar.warning("Processing document for the first time. This may take a minute...")
            # Save bytes to a temp file to let the fast loader parse it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(file_bytes)
                tmp_path = tmp_file.name

            # Use the ultra-fast PyMuPDF parser
            loader = PyMuPDFLoader(tmp_path)
            docs = loader.load()
            
            # Optimized chunk size to balance speed and accuracy
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
            splits = text_splitter.split_documents(docs)
            
            # Generate vectors and save them locally to disk
            vectorstore = Chroma.from_documents(
                documents=splits, 
                embedding=embeddings,
                persist_directory=persist_dir
            )
            os.unlink(tmp_path)
            st.sidebar.success("🎉 Processing complete! Index saved to local disk.")

        return vectorstore.as_retriever(search_kwargs={"k": 4})

    # Get retriever (loads in milliseconds if the file was uploaded previously)
    retriever = get_optimized_retriever(bytes_data, persist_directory)

    # LLM Setup
  # 3. Build the Modern LCEL Chain with Memory
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful AI assistant. Answer the user's question using ONLY "
            "the provided PDF context below. If you do not know the answer, state that "
            "it is not mentioned in the document.\n\n"
            "Context:\n{context}"
        )),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{question}")
    ])

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Clean and robust LCEL pipeline using itemgetter
    rag_chain = (
        {
            "context": itemgetter("question") | retriever | format_docs, 
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history")
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # Display Chat History
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.write(message.content)

    # Chat input
    user_query = st.chat_input("Ask something about your PDF...")
    
    if user_query:
        with st.chat_message("user"):
            st.write(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Searching document..."):
                try:
                    response = rag_chain.invoke({
                        "question": user_query,
                        "chat_history": st.session_state.chat_history
                    })
                    st.write(response)
                    
                    st.session_state.chat_history.append(HumanMessage(content=user_query))
                    st.session_state.chat_history.append(AIMessage(content=response))
                except Exception as e:
                    st.error(f"Error: {e}")