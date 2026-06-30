from embeddings import EmbeddingGenerator
from vector_store import VectorStore

store = VectorStore()

query = "What is positive skewness?"

query_embedding = EmbeddingGenerator.generate(query)

results = store.search(
    query_embedding,
    k=3
)

print("=" * 60)

for i in range(len(results["documents"][0])):

    print(f"\nResult {i+1}")

    print("Source:",
          results["metadatas"][0][i]["source"])

    print("Page:",
          results["metadatas"][0][i]["page"])

    print()

    print(results["documents"][0][i])

    print("=" * 60)