"""
============================================================
RAG AGENT — rag_agent.py
============================================================

RAG = Retrieval Augmented Generation

This agent answers questions from company documents.

How it works:
1. Loads all documents from the documents/ folder
2. Splits them into small overlapping chunks (500 chars each)
3. Converts each chunk into an embedding (vector of numbers)
4. Saves all embeddings to vectorstore/index.json
5. When a question comes in:
   a. Converts question to an embedding
   b. Finds the most similar chunks using cosine similarity
   c. Sends those chunks + question to OpenAI
   d. Returns a grounded answer with no hallucination

NEW features:
- Auto-detects when documents change and rebuilds index
- Supports uploading new documents at runtime
- Works with both .txt and .pdf files

Run standalone to test:
    python rag_agent.py setup    <- builds the index
    python rag_agent.py          <- runs test questions
============================================================
"""

import os
import json
import hashlib
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
VECTORSTORE_PATH = os.path.join(os.path.dirname(__file__), "vectorstore", "index.json")
HASH_PATH = os.path.join(os.path.dirname(__file__), "vectorstore", "doc_hashes.json")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# ============================================================
# DOCUMENT MANAGEMENT
# ============================================================

def get_document_hashes():
    """Returns filename → MD5 hash for all current documents."""
    hashes = {}
    if not os.path.exists(DOCS_DIR):
        return hashes
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_DIR, filename)
            with open(filepath, "rb") as f:
                hashes[filename] = hashlib.md5(f.read()).hexdigest()
    return hashes


def documents_changed():
    """Returns True if documents changed since last vectorstore build."""
    if not os.path.exists(HASH_PATH):
        return True
    with open(HASH_PATH, "r") as f:
        saved = json.load(f)
    return saved != get_document_hashes()


def save_document_hashes():
    """Saves current document hashes after successful build."""
    os.makedirs(os.path.dirname(HASH_PATH), exist_ok=True)
    with open(HASH_PATH, "w") as f:
        json.dump(get_document_hashes(), f)


def save_uploaded_document(filename: str, content: bytes) -> str:
    """
    Saves an uploaded document to the documents folder.
    Supports .txt and .pdf files.
    Returns the saved filename.
    """
    os.makedirs(DOCS_DIR, exist_ok=True)

    if filename.endswith(".pdf"):
        try:
            import io
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            save_name = filename.replace(".pdf", ".txt")
        except ImportError:
            raise ValueError("pypdf not installed. Run: pip install pypdf")
    else:
        text = content.decode("utf-8", errors="ignore")
        save_name = filename if filename.endswith(".txt") else filename + ".txt"

    save_path = os.path.join(DOCS_DIR, save_name)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Document saved: {save_name} ({len(text):,} characters)")
    return save_name


def list_documents():
    """Returns list of all documents in the documents folder."""
    if not os.path.exists(DOCS_DIR):
        return []
    docs = []
    for f in os.listdir(DOCS_DIR):
        if f.endswith(".txt"):
            size = os.path.getsize(os.path.join(DOCS_DIR, f))
            docs.append({"name": f, "size_bytes": size})
    return docs


# ============================================================
# CHUNKING
# ============================================================

def load_documents():
    """Loads all .txt files from the documents folder."""
    documents = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_DIR, filename)
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            documents.append({"filename": filename, "content": content})
            print(f"  Loaded: {filename} ({len(content):,} chars)")
    return documents


def split_into_chunks(documents):
    """
    Splits documents into overlapping chunks.
    
    CHUNK_SIZE=500: each chunk is ~500 characters
    CHUNK_OVERLAP=50: consecutive chunks share 50 characters
    
    Overlap prevents losing context at chunk boundaries.
    Example:
        Chunk 1: chars 0-500
        Chunk 2: chars 450-950  (50 char overlap)
        Chunk 3: chars 900-1400
    """
    chunks = []
    for doc in documents:
        content = doc["content"]
        start = 0
        while start < len(content):
            end = start + CHUNK_SIZE
            chunk_text = content[start:end]
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "source": doc["filename"],
                    "start": start
                })
            start += CHUNK_SIZE - CHUNK_OVERLAP
    print(f"  Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks


# ============================================================
# EMBEDDINGS AND VECTOR STORE
# ============================================================

def get_embedding(text):
    """
    Converts text to a vector using OpenAI embeddings.
    
    An embedding captures semantic meaning.
    Similar text → similar vectors.
    This is how we find relevant chunks for a question.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def build_vectorstore(chunks):
    """Creates embeddings for all chunks and saves to disk."""
    print(f"  Creating embeddings for {len(chunks)} chunks...")
    vectorstore = []
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk["text"])
        vectorstore.append({
            "text": chunk["text"],
            "source": chunk["source"],
            "embedding": embedding
        })
        if (i + 1) % 10 == 0:
            print(f"    Embedded {i+1}/{len(chunks)}...")

    os.makedirs(os.path.dirname(VECTORSTORE_PATH), exist_ok=True)
    with open(VECTORSTORE_PATH, "w") as f:
        json.dump(vectorstore, f)

    save_document_hashes()
    print(f"  Vectorstore saved: {len(vectorstore)} entries")
    return vectorstore


def load_vectorstore():
    """Loads the saved vectorstore from disk."""
    if not os.path.exists(VECTORSTORE_PATH):
        return None
    with open(VECTORSTORE_PATH, "r") as f:
        return json.load(f)


# ============================================================
# SIMILARITY SEARCH
# ============================================================

def cosine_similarity(vec1, vec2):
    """
    Measures similarity between two vectors.
    Returns value between -1 and 1.
    1.0 = identical meaning, 0.0 = unrelated.
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def find_relevant_chunks(question, vectorstore, top_k=4):
    """
    Finds the most relevant document chunks for the question.
    1. Converts question to embedding
    2. Compares to all chunk embeddings
    3. Returns top_k most similar chunks
    """
    question_embedding = get_embedding(question)
    scored = []
    for item in vectorstore:
        score = cosine_similarity(question_embedding, item["embedding"])
        scored.append({
            "text": item["text"],
            "source": item["source"],
            "score": score
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


# ============================================================
# ANSWER GENERATION
# ============================================================

def answer_from_documents(question, vectorstore):
    """
    Complete RAG pipeline:
    1. Find relevant chunks
    2. Build context string
    3. Ask OpenAI to answer using ONLY context
    4. Return answer with source documents
    
    Key instruction to OpenAI: answer from context only.
    This prevents hallucination.
    """
    relevant_chunks = find_relevant_chunks(question, vectorstore)

    if not relevant_chunks or relevant_chunks[0]["score"] < 0.3:
        return {
            "answer": "I could not find relevant information in the company documents.",
            "sources": [],
            "relevant": False
        }

    context = ""
    sources = set()
    for chunk in relevant_chunks:
        context += f"\n[From {chunk['source']}]\n{chunk['text']}\n"
        sources.add(chunk["source"])

    prompt = f"""You are a helpful company assistant.
                Answer the question using ONLY the information in the context below.
                If the answer is not in the context, say "I don't have that information in the company documents."
                Do not make up information.

                CONTEXT:
                {context}

                QUESTION: {question}

                ANSWER:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": list(sources),
        "relevant": True
    }


# ============================================================
# SETUP AND CACHE
# ============================================================

def setup_rag(force=False):
    """Builds the vectorstore. Skips if already up to date."""
    if not force and not documents_changed():
        print("Documents unchanged — loading existing vectorstore")
        return load_vectorstore()

    print("Building RAG vectorstore...")
    print("\nStep 1: Loading documents...")
    docs = load_documents()

    print("\nStep 2: Chunking...")
    chunks = split_into_chunks(docs)

    print("\nStep 3: Creating embeddings (this takes 1-2 minutes)...")
    vs = build_vectorstore(chunks)

    print("\nRAG setup complete!")
    return vs


def get_or_build_vectorstore():
    """
    Returns existing vectorstore if documents unchanged.
    Rebuilds automatically if documents changed or new ones added.
    """
    if documents_changed():
        print("Documents changed — rebuilding vectorstore...")
        return setup_rag(force=True)
    vs = load_vectorstore()
    if vs:
        return vs
    return setup_rag(force=True)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_rag(force=True)
    else:
        print("RAG Agent Test")
        print("=" * 50)
        vs = get_or_build_vectorstore()
        test_questions = [
            "How many days of annual leave do employees get?",
            "What is the bonus for Outstanding performance rating?",
            "What is the price of the GenAI Bootcamp?",
            "What are the working hours at TechVision?",
        ]
        for q in test_questions:
            print(f"\nQ: {q}")
            result = answer_from_documents(q, vs)
            print(f"A: {result['answer']}")
            print(f"Sources: {result['sources']}")
