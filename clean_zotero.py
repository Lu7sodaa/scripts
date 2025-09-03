import os
import shutil
import zipfile
from pathlib import Path
from bs4 import BeautifulSoup
from readability import Document

SOURCE_DIR = Path("/Users/sodaa/Downloads/zotero")
DEST_DIR = Path("/Users/sodaa/RAG/zotero-clean")
TEMP_DIR = DEST_DIR / "__temp_extract__"
DEST_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def clean_html(html_path, output_path):
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
        doc = Document(html)
        title = doc.title().strip().replace('/', '_').replace('\\', '_')
        summary_html = doc.summary()
        soup = BeautifulSoup(summary_html, "html.parser")
        text = soup.get_text(separator="\n")
        output_file = output_path / f"{title}.txt"
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write(text)
        print(f"[✓] HTML nettoyé → {output_file.name}")
    except Exception as e:
        print(f"[!] Erreur nettoyage HTML ({html_path.name}): {e}")

def copy_file(src_path, output_path):
    filename = src_path.name
    dest_file = output_path / filename
    counter = 1
    while dest_file.exists():
        dest_file = output_path / f"{src_path.stem}_{counter}{src_path.suffix}"
        counter += 1
    shutil.copy2(src_path, dest_file)
    print(f"[→] Copié : {dest_file.name}")

def process_zip(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            extract_path = TEMP_DIR / zip_path.stem
            extract_path.mkdir(parents=True, exist_ok=True)
            zip_ref.extractall(extract_path)

            for file in extract_path.iterdir():
                if file.suffix.lower() in ['.pdf', '.md', '.txt']:
                    copy_file(file, DEST_DIR)
                elif file.suffix.lower() == '.html':
                    clean_html(file, DEST_DIR)

            shutil.rmtree(extract_path)  # nettoyage du temporaire
    except Exception as e:
        print(f"[!] Erreur extraction ZIP ({zip_path.name}): {e}")

def main():
    for file in SOURCE_DIR.iterdir():
        if file.suffix.lower() == ".zip":
            process_zip(file)

if __name__ == "__main__":
    main()
