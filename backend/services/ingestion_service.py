import os
import uuid
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urlparse
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

        self._nextjs_docs_domain = os.getenv("NEXTJS_DOCS_DOMAIN")
        self._nextjs_sitemap_url = os.getenv("NEXTJS_SITEMAP_URL")
        self._nextjs_max_pages = int(os.getenv("NEXTJS_MAX_PAGES", 0))
        self._langchain_docs_domain = os.getenv("LANGCHAIN_DOCS_DOMAIN")
        self._langchain_sitemap_url = os.getenv("LANGCHAIN_SITEMAP_URL")
        self._langchain_max_pages = int(os.getenv("LANGCHAIN_MAX_PAGES", 0))
        self._stripe_docs_domain = os.getenv("STRIPE_DOCS_DOMAIN")
        self._stripe_sitemap_url = os.getenv("STRIPE_SITEMAP_URL")
        self._stripe_max_pages = int(os.getenv("STRIPE_MAX_PAGES", 0))

        self._considering_nextjs_docs = (self._nextjs_docs_domain is not None
                and self._nextjs_sitemap_url is not None and self._nextjs_max_pages != 0)
        self._considering_langchain_docs = (self.langchain_docs_domain is not None
                and self._langchain_sitemap_url is not None and self._langchain_max_pages != 0)
        self._considering_stripe_docs = (self._stripe_docs_domain is not None
                and self._stripe_sitemap_url is not None and self._stripe_max_pages != 0)
    
    def _get_current_time(self):
        try:
            return datatime.now().strftime("%H:%M:%S")
        except Exception:
            return ""

    def _is_urls_in_same_domain(self, url1: str, url2: str) -> bool:
        try:
            url1_netloc = urlparse(url1).netloc.lower()
            url2_netloc = urlparse(url2).netloc.lower()
            return url1_netloc == url2_netloc
        except Exception:
            return False

    def _get_pages_of_intrest(self, sitemap_url: str, max_pages):
        response = requests.get(sitemap_url)
        soup = BeautifulSoup(response.content, 'xml')
        
        pages_of_intrest = []
        items = soup.find_all('loc')
        for item in items[:max_pages]:
            pages_of_intrest.append(item.get_text())

        return pages_of_intrest

    def scrape_documentation(self, url: str) -> str:
        print(f"--- [INJECTOR][{self._get_current_time()}]: scraping url: {url}")
        try:
            response = requests.get(url)

            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            print(f"--- [INJECTOR][{self._get_current_time}]: done scraping url: {url}")
            return text
        except Exception as e:
            raise Exception(f"failed to scrape {url}: {str(e)}")

    def process_documents(self, source_url: str, job_id: str):
        try:
            print(f"--- [INJECTOR][{self._get_current_time()}]: starting job: {job_id}")
            self.supabase.table("ingestion_jobs").update({
                "status": "processing"
            }).eq("id", job_id).execute()

            urls = [source_url]

            try:
                new_pages = []
                if self._considering_nextjs_docs and self._is_urls_in_same_domain(source_url, self._nextjs_docs_domain):
                    new_pages = self._get_pages_of_intrest(self._nextjs_sitemap_url, self._nextjs_max_pages)
                elif self._considering_langchain_docs and self._is_urls_in_same_domain(source_url, self._langchain_docs_domain):
                    new_pages = self._get_pages_of_intrest(self._langchain_sitemap_url, self._langchain_max_pages)
                elif self._considering_stripe_docs and self._is_urls_in_same_domain(source_url, self._stripe_docs_domain):
                    new_pages = self._get_pages_of_intrest(self._stripe_sitemap_url, self._stripe_max_pages)
                urls.extend(new_pages)
            except:
                pass

            for url in urls:
                print(f"--- [INJECTOR][{self._get_current_time()}]: processing url: {url}")

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
                    print(f"--- [INJECTOR][{self._get_current_time()}]: storing chunk: {i}")
                    self.supabase.table("document_chunks").insert({
                        "ingestion_job_id": job_id,
                        "content": chunk.page_content,
                        "metadata": chunk.metadata,
                        "chunk_index": i,
                        "source_url": url
                    }).execute()

                print(f"--- [INJECTOR][{self._get_current_time()}]: completed job: {job_id}")
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

