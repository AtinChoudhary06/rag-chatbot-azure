from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, uuid

from app.blob_service import upload_pdf, get_blob_url
from app.doc_intel import extract_text
from app.search_service import create_index, index_chunks, hybrid_search
from app.cosmos_service import save_message, get_history
from app.llm_service import generate_answer

app = FastAPI(title="Azure RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def startup():
    create_index()

@app.get("/")
def root():
    return {"status": "Azure RAG Chatbot API is running"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename
    upload_pdf(content, filename)
    blob_url = get_blob_url(filename)
    chunks = extract_text(blob_url)
    index_chunks(chunks, filename)
    return {
        "message": f"Successfully indexed {len(chunks)} pages",
        "filename": filename,
        "pages": len(chunks)
    }

class ChatRequest(BaseModel):
    question: str
    session_id: str = None

@app.post("/chat")
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    chunks = hybrid_search(req.question)
    history = get_history(session_id)
    answer = generate_answer(req.question, chunks, history)
    save_message(session_id, "user", req.question)
    save_message(session_id, "assistant", answer)
    return {
        "answer": answer,
        "session_id": session_id,
        "sources_used": len(chunks)
    }

@app.get("/history/{session_id}")
def history(session_id: str):
    messages = get_history(session_id)
    return {"session_id": session_id, "messages": messages}