from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 1. Initialize your LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. Design a clean system prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert AI assistant. Answer the user's question using ONLY the provided context from the uploaded PDF document. If you don't know, say 'I don't know'.\n\nContext:\n{context}"),
    ("user", "{question}")
])

# 3. Format helper for retrieved documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 4. The Modern LCEL RAG Chain (No deprecated classes!)
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 5. Run the chain with a single clean invoke!
response = rag_chain.invoke("What is the main topic discussed in the PDF?")
print(response)