from text_extract import TextExtractor
from chunking import TextChunker
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from llm import LLM


class RAG:

    def __init__(self):
        self.store = VectorStore()

    def index_document(self, file_path):

        pages = TextExtractor.extract(file_path)

        chunks = TextChunker.chunk_pages(pages)

        embeddings = [
            EmbeddingGenerator.generate(chunk["text"])
            for chunk in chunks
        ]

        self.store.add_chunks(
            chunks,
            embeddings
        )

        return len(chunks)

    def ask(self, question, k=3):

        embedding = EmbeddingGenerator.generate(question)

        results = self.store.search(
            embedding,
            k
        )

        context = "\n\n".join(
            results["documents"][0]
        )

        prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the context below.

If the answer is not present in the context,
say:

"I couldn't find that information in the uploaded documents."

Context:

{context}

Question:

{question}
"""

        answer = LLM.ask(prompt)

        return {
            "answer": answer,
            "sources": results["metadatas"][0]
        }
    
    def stream(self, question, k=3):

        embedding = EmbeddingGenerator.generate(question)

        results = self.store.search(
            embedding,
            k
        )

        context = "\n\n".join(
            results["documents"][0]
        )

        prompt = f"""
    You are a helpful AI assistant.

    Answer ONLY using the context below.

    If the answer is not present in the context,
    say:

    "I couldn't find that information in the uploaded documents."

    Context:

    {context}

    Question:

    {question}
    """

        return LLM.stream(prompt)