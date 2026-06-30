from ollama import embed


class EmbeddingGenerator:

    MODEL = "nomic-embed-text"

    @staticmethod
    def generate(text: str):
        if not text.strip():
            raise ValueError("Cannot generate embedding for empty text.")

        try:
            response = embed(
                model=EmbeddingGenerator.MODEL,
                input=text
            )
            return response["embeddings"][0]

        except Exception as e:
            raise RuntimeError(f"Embedding generation failed: {e}")