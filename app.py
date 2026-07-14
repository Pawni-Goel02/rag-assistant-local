from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pathlib import Path
from fastapi import UploadFile, File, HTTPException
import shutil
from rag import RAG
from fastapi.responses import StreamingResponse
import json
import os

from pydantic import BaseModel

class URLRequest(BaseModel):
    url: str

app = FastAPI(title="Local RAG Assistant")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
rag = RAG()


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

    save_path = UPLOAD_DIR / file.filename
    print(save_path)

    # Save the uploaded file first
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Now process it
    chunk_count = rag.index_document(save_path)

    if chunk_count == 0:
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in this file. It may be a scanned/image-only document."
        )

    return {
        "success": True,
        "filename": file.filename,
        "chunks": chunk_count
    }

from pydantic import BaseModel

class ChatRequest(BaseModel):
    question:str

@app.post("/chat")
async def chat(request: ChatRequest):

    def event_generator():

        for item in rag.stream(request.question):

            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@app.post("/chat/reset")
async def reset_chat():

    rag.memory.clear()

    return {
        "success": True
    }

@app.post("/documents/clear")
async def clear_documents():

    rag.clear_documents()

    for file in UPLOAD_DIR.iterdir():

        if file.is_file():
            file.unlink()

    return {
        "success": True
    }

@app.get("/documents")
async def documents():

    return {
        "documents": rag.list_documents()
    }

@app.post("/upload-url")
async def upload_url(request: URLRequest):

    chunks = rag.index_url(
        request.url
    )

    return {
        "success": True,
        "url": request.url,
        "chunks": chunks
    }