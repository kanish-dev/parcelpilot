import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
FAISS_PATH = str(BASE_DIR / "faiss_index")
CHROMA_PATH = str(BASE_DIR / "chroma_db")
