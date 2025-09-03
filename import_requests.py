import os
import requests
import fitz  # PyMuPDF pour les PDF
from bs4 import BeautifulSoup
from collections import defaultdict
import spacy
from io import BytesIO
from requests.auth import HTTPBasicAuth
import urllib.parse
import xml.etree.ElementTree as ET
import urllib3

# Désactiver les avertissements SSL pour certificats auto-signés
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Charger le modèle NLP de spaCy
nlp = spacy.load("fr_core_news_md")

# Fonction pour récupérer la liste des fichiers via WebDAV
def get_file_list_via_webdav(base_url, username, password):
    response = requests.request("PROPFIND", base_url, auth=HTTPBasicAuth(username, password), verify=False)
    if response.status_code == 207:
        file_list = []
        root = ET.fromstring(response.content)
        for elem in root.findall(".//{DAV:}href"):
            file_path = elem.text.strip()
            # Exclure les fichiers de la corbeille et cachés
            if "#recycle" not in file_path and not file_path.startswith('.'):
                file_list.append(file_path.strip('/'))
        return file_list
    else:
        print(f"Erreur lors de la récupération de la liste des fichiers: {response.status_code}")
        return []

# Fonction pour télécharger les fichiers via WebDAV
def download_file_via_webdav(base_url, file, local_path, username, password):
    remote_path = urllib.parse.unquote(f"{base_url.rstrip('/')}/{file.strip('/')}")
    if 'zotero/zotero/' in remote_path:
        remote_path = remote_path.replace('zotero/zotero/', 'zotero/')

    headers = {
        "Authorization": f"Basic {requests.auth._basic_auth_str(username, password)}",
        "Depth": "1",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0"
    }

    print(f"Tentative d'accès à : {remote_path}")  # Pour vérification

    try:
        response = requests.get(remote_path, headers=headers, verify=False)
        if response.status_code == 200:
            with open(local_path, 'wb') as file:
                file.write(response.content)
            return local_path
        else:
            print(f"Erreur lors du téléchargement du fichier {remote_path}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erreur lors du téléchargement du fichier {remote_path}: {e}")
        return None

# Fonction pour analyser les PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Erreur lors de la lecture du PDF {pdf_path}: {e}")
    return text

# Fonction pour analyser les fichiers HTML
def extract_text_from_html(html_path):
    try:
        with open(html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            return soup.get_text()
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier HTML {html_path}: {e}")
        return ""

# Fonction principale pour analyser les fichiers Zotero via WebDAV
def analyze_zotero_library_webdav(base_url, username, password, temp_dir):
    all_concepts = defaultdict(int)
    file_list = get_file_list_via_webdav(base_url, username, password)

    for file in file_list:
        local_path = os.path.join(temp_dir, os.path.basename(file))
        downloaded_file = download_file_via_webdav(base_url, file, local_path, username, password)

        if downloaded_file:
            if file.endswith(".pdf"):
                text = extract_text_from_pdf(downloaded_file)
            elif file.endswith(".html"):
                text = extract_text_from_html(downloaded_file)
            elif file.endswith(".txt") or file.endswith(".md"):
                with open(downloaded_file, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                continue

            concepts = extract_concepts(text)
            for concept, count in concepts.items():
                all_concepts[concept] += count

    return dict(sorted(all_concepts.items(), key=lambda x: -x[1]))

# Fonction pour extraire les concepts clés
def extract_concepts(text):
    doc = nlp(text)
    concepts = defaultdict(int)
    for ent in doc.ents:
        concepts[ent.text] += 1
    return dict(sorted(concepts.items(), key=lambda x: -x[1]))

# Fonction pour générer un plan de taggage
def generate_tagging_plan(concepts, top_n=50):
    print(f"\nTop {top_n} concepts clés pour le taggage :")
    for concept, count in list(concepts.items())[:top_n]:
        print(f"{concept}: {count}")

# Exécution du script
if __name__ == "__main__":
    webdav_url = "https://sodaa.synology.me:5006/zotero"
    username = "lucas"
    password = "7uc45KKIB1990!"  # Remplace par ton mot de passe
    temp_dir = "./temp_zotero"
    os.makedirs(temp_dir, exist_ok=True)

    concepts = analyze_zotero_library_webdav(webdav_url, username, password, temp_dir)
    generate_tagging_plan(concepts)
