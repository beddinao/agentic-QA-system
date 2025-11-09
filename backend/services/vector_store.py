import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

class VectorStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.pinecone = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY")
        )
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        try:
            self._ensure_index_exists()
        except Exception as e:
            print("--- [PINECONE]: INIT FAILURE")
        print("--- [PINECONE]: INIT SUCCESS")

    def _ensure_index_exists(self):
        existing_indexes = self.pinecone.list_indexes()
        existing_index_names = [index.name for index in existing_indexes]
        if self.index_name not in existing_index_names:
            print("--- [PINECONE]: creating new index")
            self.pinecone.create_index(
                name=self.index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                ),
                deletion_protection="disabled"
            )

    def get_vector_store(self):
        return PineconeVectorStore.from_existing_index(
            index_name=self.index_name,
            embedding=self.embeddings
        )

    def add_documents(self, documents):
        vector_store = self.get_vector_store()
        return vector_store.add_documents(documents)


vector_store = VectorStore()
