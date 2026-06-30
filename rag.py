from embeddings import EmbeddingGenerator
from vector_store import VectorStore


class RAG:

    def __init__(self):

        self.store = VectorStore()

    def retrieve(
        self,
        question,
        k=3
    ):

        embedding = EmbeddingGenerator.generate(
            question
        )

        return self.store.search(
            embedding,
            k
        )