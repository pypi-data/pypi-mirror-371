#!/usr/bin/env python3
import os
from pathlib import Path
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

def store_codebase(path, db_path="chroma_db"):
    """Store entire codebase in ChromaDB for context"""
    path = Path(path)
    documents = []
    
    # Code file extensions
    code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.php', '.c', '.cpp', '.cs']
    ignore_dirs = ['node_modules', '.git', 'venv', '__pycache__', 'dist', 'build', '.venv', 'env']
    
    # Walk directory and collect files
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in code_extensions):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    doc = Document(
                        page_content=content,
                        metadata={'file_path': str(file_path), 'file_name': file}
                    )
                    documents.append(doc)
                    
                except Exception:
                    continue
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    
    # Create ChromaDB
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(splits, embeddings, persist_directory=db_path)
    
    print(f"Stored {len(documents)} files ({len(splits)} chunks) in {db_path}")
    return vectorstore

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python vector_db.py <codebase_path>")
        sys.exit(1)
    
    store_codebase(sys.argv[1])