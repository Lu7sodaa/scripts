import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

START_URL = "https://millenaire3.grandlyon.com/"
DOMAIN = "millenaire3.grandlyon.com"
VISITED = set()

# Dossier de destination personnalisé
PDF_FOLDER = "/Users/sodaa/RAG/corpus/M3"
os.makedirs(PDF_FOLDER, exist_ok=True)

def is_valid(url):
    parsed = urlparse(url)
    return parsed.netloc == DOMAIN and url not in VISITED

def crawl(url):
    try:
        print(f"[+] Visite : {url}")
        VISITED.add(url)
        response = requests.get(url, timeout=10)
        if not response.ok or "text/html" not in response.headers.get("Content-Type", ""):
            return

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = urljoin(url, link["href"])
            if href.endswith(".pdf"):
                download_pdf(href)
            elif is_valid(href):
                crawl(href)
    except Exception as e:
        print(f"[!] Erreur sur {url} : {e}")

def download_pdf(url):
    try:
        filename = os.path.basename(urlparse(url).path)
        filepath = os.path.join(PDF_FOLDER, filename)
        if os.path.exists(filepath):
            print(f"[=] Déjà téléchargé : {filename}")
            return
        print(f"[↓] Téléchargement : {filename}")
        r = requests.get(url, timeout=15)
        with open(filepath, "wb") as f:
            f.write(r.content)
    except Exception as e:
        print(f"[!] Erreur lors du téléchargement de {url} : {e}")

if __name__ == "__main__":
    crawl(START_URL)
    print(f"\n✅ Téléchargement terminé. PDFs enregistrés dans {PDF_FOLDER}")
