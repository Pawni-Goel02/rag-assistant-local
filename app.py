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