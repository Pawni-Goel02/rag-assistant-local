from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pathlib import Path
from fastapi import UploadFile, File, HTTPException
import shutil
from text_extract import TextExtractor
from chunking import TextChunker
from embeddings import EmbeddingGenerator
from vector_store import VectorStore

app = FastAPI(title="Local RAG Assistant")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
vector_store = VectorStore()


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
    pages = TextExtractor.extract(save_path)

    chunks = TextChunker.chunk_pages(pages)

    embeddings = [
        EmbeddingGenerator.generate(chunk["text"])
        for chunk in chunks
    ]
    print(f"Pages: {len(pages)}")
    print(f"Chunks: {len(chunks)}")
    print(f"Embeddings: {len(embeddings)}")

    vector_store.add_chunks(
        chunks,
        embeddings
    )

    return {
        "success": True,
        "filename": file.filename,
        "chunks": len(chunks)
    }