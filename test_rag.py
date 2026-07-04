from rag import RAG

rag = RAG()

response = rag.ask(
    "Explain positive skewness."
)

print("\nANSWER\n")

print(response["answer"])

print("\nSOURCES\n")

for source in response["sources"]:

    print(source)