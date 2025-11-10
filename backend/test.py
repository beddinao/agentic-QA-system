import requests
from bs4 import BeautifulSoup

DOCS_1="https://nextjs.org/"
DOCS_2="https://python.langchain.com/"

SITEMAP_1="https://nextjs.org/sitemap.xml"
SITEMAP_2="https://docs.langchain.com/sitemap.xml"

MAX_PAGES_1=2
MAX_PAGES_2=3

def extract_pages(sitemap_url: str, max_pages: str):
    try:
        response = requests.get(sitemap_url)
        soup = BeautifulSoup(response.content, 'xml')

        pages_of_intrest = []
        items = soup.find_all('loc')
        
        for item in items[:max_pages]:
            pages_of_intrest.append(item.get_text())

        print(pages_of_intrest)
        return "success"

    except Exception as e:
        return f"{str(e)}"

def scrape(url: str):
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
        return e

from urllib.parse import urlparse

def is_urls_in_same_domain(url1: str, url2: str) -> bool:
    try:
        parsed_url1 = urlparse(url1)
        parsed_url2 = urlparse(url2)
        url1_netloc = parsed_url1.netloc.lower()
        url2_netloc = parsed_url2.netloc.lower()
        return url1_netloc == url2_netloc

    except Exception:
        return False

#print(is_urls_in_same_domain("https://docs.langchain.com/sitemap.xml", "https://langchain.com/"))

from datetime import datetime

def _get_current_time():
    try:
        return datetime.now().strftime("%H:%M:%S")
    except Exception:
        return ""

print(_get_current_time())
