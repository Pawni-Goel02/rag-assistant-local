from typing import List, Dict


class TextChunker:

    @staticmethod
    def chunk_pages(
        pages: List[Dict],
        chunk_size: int = 500,
        overlap: int = 100
    ):

        chunks = []

        for page in pages:

            text = page["text"]

            start = 0

            while start < len(text):

                end = start + chunk_size

                chunk = text[start:end]
                chunk_id = len(chunks)

                chunks.append(
                    {
                        "id": chunk_id,
                        "source": page["source"],
                        "page": page["page"],
                        "text": chunk
                    }
                )

                start += chunk_size - overlap

        return chunks