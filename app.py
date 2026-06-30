from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pathlib import Path
from fastapi import UploadFile, File, HTTPException
import shutil

app = FastAPI(title="Local RAG Assistant")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


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

    try:

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        return {
            "success": True,
            "filename": file.filename
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )