import os
import pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=os.getenv("OPENROUTER_API_KEY")
        )
        self.pinecone = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY")
        )
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        self._ensure_index_exists()

        print("Pinecone Vector Store init success")

    def _ensure_index_exists(self):
        if self.index_name not in self.pinecone.list_indexes():
            print("index not found creating new")
            self.pinecone.create_index(
                name=self.index_name,
                dimension=1536,
                metric="cosine"
            )
        print("index is there")

    def get_vector_store(self):
        return PineconeVectorStore.from_existing_index(
            index_name=self.index_name,
            embedding=self.embeddings
        )

    def add_documents(self, documents):
        vector_store = self.get_vector_store()
        return vector_store.add_documents(documents)


vector_store = VectorStore()
