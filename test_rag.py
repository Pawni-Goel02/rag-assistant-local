from rag import RAG

rag = RAG()

results = rag.retrieve(
    "What is positive skewness?"
)

print(results)