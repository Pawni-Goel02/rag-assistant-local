from pathlib import Path

BASE_DIR = Path(__file__).parent

UPLOAD_DIR = BASE_DIR / "uploads"
STORAGE_DIR = BASE_DIR / "storage"
CHROMA_DIR = BASE_DIR / "chroma_db"

UPLOAD_DIR.mkdir(exist_ok=True)
STORAGE_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

OLLAMA_URL = "http://localhost:11434"

LLM_MODEL = "qwen3:8b"
EMBED_MODEL = "nomic-embed-text"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

TOP_K = 4

TEMPERATURE = 0.2