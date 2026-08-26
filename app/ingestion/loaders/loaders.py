from pathlib import Path
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

def load_pdfs(data_dir: Path):
    print(f"Loading PDFs from {data_dir}...")
    pdf_files = list(data_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files.")
    docs = []
    
    for file_path in pdf_files:
        loader = PyPDFLoader(str(file_path))
        docs.extend(loader.load())
    return docs

def load_excel(excel_path: Path):
    print(f"Loading Excel data from {excel_path}...")
    
    if not excel_path.exists():
        print(f"Excel file not found at {excel_path}")
        return []
        
    xls = pd.ExcelFile(str(excel_path))
    sheet_names = xls.sheet_names
    print(f"Found sheets: {sheet_names}")
    
    documents = []
    
    for sheet_name in sheet_names:
        if sheet_name.lower() == 'readme':
            continue
            
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        for index, row in df.iterrows():
            row_dict = row.dropna().to_dict()
            
            account_id = str(row_dict.get('Account_ID', row_dict.get('AccountID', row_dict.get('account_id', 'UNKNOWN'))))
            
            content = f"Record Type: {sheet_name}\n"
            for k, v in row_dict.items():
                content += f"{k}: {v}\n"
                
            doc = Document(
                page_content=content,
                metadata={"source": str(excel_path), "sheet": sheet_name, "account_id": account_id}
            )
            documents.append(doc)
    return documents
