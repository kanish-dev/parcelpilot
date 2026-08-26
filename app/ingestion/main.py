import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from langchain_community.vectorstores import FAISS, Chroma
from app.config import DATA_DIR, FAISS_PATH, CHROMA_PATH
from app.services.retrieval.retrievers import get_embeddings
from app.ingestion.loaders.loaders import load_pdfs, load_excel
from app.ingestion.chunking.chunker import chunk_documents

def ingest_pdfs(embeddings):
    docs = load_pdfs(DATA_DIR)
    splits = chunk_documents(docs)
    
    if not splits:
        print("No documents were split. Skipping FAISS ingestion.")
        return
        
    vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local(FAISS_PATH)
    print(f"Saved {len(splits)} PDF chunks to FAISS.")

def ingest_excel(embeddings):
    excel_path = DATA_DIR / "ParcelPilot_Assessment_Data.xlsx"
    documents = load_excel(excel_path)
    
    if documents:
        vectorstore = Chroma.from_documents(
            documents=documents, 
            embedding=embeddings, 
            persist_directory=CHROMA_PATH
        )
        print(f"Saved {len(documents)} structured data records to ChromaDB.")

def main():
    embeddings = get_embeddings()
    ingest_pdfs(embeddings)
    ingest_excel(embeddings)
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
