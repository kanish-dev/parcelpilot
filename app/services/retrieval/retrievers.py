import os
from functools import lru_cache
from langchain_community.vectorstores import FAISS, Chroma
from app.config import FAISS_PATH, CHROMA_PATH

@lru_cache(maxsize=1)
def get_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

@lru_cache(maxsize=1)
def get_faiss_vectorstore():
    embeddings = get_embeddings()
    if not os.path.exists(FAISS_PATH):
        raise ValueError("FAISS index not found. Run ingestion first.")
    return FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)

def get_faiss_retriever():
    return get_faiss_vectorstore().as_retriever(search_kwargs={"k": 3})

@lru_cache(maxsize=1)
def get_chroma_vectorstore():
    embeddings = get_embeddings()
    if not os.path.exists(CHROMA_PATH):
        raise ValueError("ChromaDB index not found. Run ingestion first.")
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

def get_chroma_retriever(account_id=None):
    vectorstore = get_chroma_vectorstore()
    
    search_kwargs = {"k": 3}
    if account_id:
        search_kwargs["filter"] = {"account_id": str(account_id)}
        
    return vectorstore.as_retriever(search_kwargs=search_kwargs)
