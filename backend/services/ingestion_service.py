import os
import uuid
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from services.vector_store import vector_store
from supabase import create_client

load_dotenv()

class IngestionService:
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def scrape_documentation(self, url: str) -> str:
        try:
            response = requests.get(url)

            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text
        except Exception as e:
            raise Exception(f"failed to scrape {url}: {str(e)}")

    def process_documents(self, url: str, job_id: str):
        try:
            self.supabase.table("ingestion_jobs").update({
                "status": "processing"
            }).eq("id", job_id).execute()

            content = self.scrape_documentation(url)
            
            doc = Document(
                    page_content = content,
                    metadata={"source": url}
            )

            chunks = self.text_splitter.split_documents([doc])

            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["job_id"] = job_id

            vector_store.add_documents(chunks)

            for i, chunk in enumerate(chunks):
                self.supabase.table("document_chunks").insert({
                    "ingestion_job_id": job_id,
                    "content": chunk.page_content,
                    "metadata": chunk.metadata,
                    "chunk_index": i,
                    "source_url": url
                }).execute()

            self.supabase.table("ingestion_jobs").update({
                "status": "completed",
                "completed_at": "now()"
            }).eq("id", job_id).execute()


        except Exception as e:
            self.supabase.table("ingestion_jobs").update({
                "status": "failed",
                "error_message": str(e)
            }).eq("id", job_id).execute()
            print(f"got error: {str(e)}")

