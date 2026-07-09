from rag import RAG

rag = RAG()

for token in rag.stream(
    "What is positive skewness?"
):
    print(token, end="", flush=True)