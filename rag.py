from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from llm import LLM


class RAG:

    def __init__(self):

        self.store = VectorStore()

    def ask(
        self,
        question,
        k=3
    ):

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

If the answer is not present in the context, reply:

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