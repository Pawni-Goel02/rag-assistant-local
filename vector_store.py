import chromadb
from chromadb.config import Settings


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    def add_chunks(self, chunks, embeddings):

        ids = [
            f'{chunk["source"]}_{chunk["id"]}'
            for chunk in chunks
        ]

        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        metadatas = [
            {
                "source": chunk["source"],
                "page": chunk["page"]
            }
            for chunk in chunks
        ]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding,
        k=5
    ):

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
    
    def clear(self):

        self.client.delete_collection(
            "documents"
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    def list_documents(self):

        data = self.collection.get(
            include=["metadatas"],
            limit=self.collection.count()
        )

        seen = set()
        documents = []

        for metadata in data["metadatas"]:

            source = metadata["source"]

            if source not in seen:

                seen.add(source)
                documents.append(source)

        return documents