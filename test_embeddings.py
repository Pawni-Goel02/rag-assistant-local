from pathlib import Path

from text_extract import TextExtractor
from chunking import TextChunker
from embeddings import EmbeddingGenerator

pages = TextExtractor.extract(
    Path("uploads/datasci.pdf")
)

chunks = TextChunker.chunk_pages(pages)

embedding = EmbeddingGenerator.generate(
    chunks[0]["text"]
)

print("Embedding length:", len(embedding))

print()

print("First 10 values:")

print(embedding[:10])