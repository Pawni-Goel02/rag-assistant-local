from pathlib import Path

from text_extract import TextExtractor
from chunking import TextChunker

pages = TextExtractor.extract(
    Path("uploads/datasci.pdf")
)

chunks = TextChunker.chunk_pages(pages)

print(f"Total Chunks: {len(chunks)}")

print("=" * 50)

print(chunks[0])