"""
============================================================
FASTAPI — main.py
============================================================

Entry point for AskCompany.

Endpoints:
    GET  /health          — system health check
    POST /ask             — main question endpoint
    POST /upload          — upload a new document
    GET  /documents       — list loaded documents
    DELETE /documents/{f} — delete a document

Run:
    uvicorn main:app --port 8000 --reload
============================================================
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import time

from orchestrator import ask, reload_vectorstore
from rag_agent import save_uploaded_document, list_documents

app = FastAPI(
    title="AskCompany AI Assistant",
    description="Enterprise AI — RAG + Database Agent + Conversation Memory",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class QuestionRequest(BaseModel):
    question: str
    conversation_history: Optional[List[Message]] = []


class QuestionResponse(BaseModel):
    answer: str
    source: str
    details: dict
    time_taken: float


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "system": "AskCompany AI Assistant"
    }


@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    history = [
        {"role": m.role, "content": m.content}
        for m in (request.conversation_history or [])
    ]

    start = time.time()
    try:
        result = ask(request.question, history)
        elapsed = round(time.time() - start, 2)
        return QuestionResponse(
            answer=result["answer"],
            source=result["source"],
            details=result["details"],
            time_taken=elapsed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a new document and rebuild the vectorstore."""
    if not file.filename.endswith((".txt", ".pdf")):
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .pdf files supported"
        )
    try:
        content = await file.read()
        saved_name = save_uploaded_document(file.filename, content)
        reload_vectorstore()
        return {
            "message": "Document uploaded and indexed successfully",
            "filename": saved_name,
            "size_bytes": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
def get_documents():
    """Lists all documents currently in the system."""
    return {"documents": list_documents()}


@app.delete("/documents/{filename}")
def delete_document(filename: str):
    """Deletes a document and rebuilds the vectorstore."""
    docs_dir = os.path.join(os.path.dirname(__file__), "documents")
    filepath = os.path.join(docs_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Document not found")
    os.remove(filepath)
    reload_vectorstore()
    return {"message": f"{filename} deleted and vectorstore rebuilt"}
