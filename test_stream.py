from rag import RAG

rag = RAG()

for item in rag.stream(
    "What is positive skewness?"
):
    print(item)