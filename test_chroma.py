from pathlib import Path

from text_extract import TextExtractor
from chunking import TextChunker
from embeddings import EmbeddingGenerator
from vector_store import VectorStore

pages = TextExtractor.extract(
    Path("uploads/datasci.pdf")
)

chunks = TextChunker.chunk_pages(pages)

embeddings = []

for chunk in chunks:
    embeddings.append(
        EmbeddingGenerator.generate(
            chunk["text"]
        )
    )

store = VectorStore()

store.add_chunks(
    chunks,
    embeddings
)

print("Stored", len(chunks), "chunks.")