import os
import re
from pathlib import Path

import markdown
from bs4 import BeautifulSoup

from pdfminer.high_level import extract_text as pdf_extract_text
from ebooklib import epub

def clean_markdown(md_text):
    # Convert Markdown to HTML, then strip HTML tags to get plain text
    html = markdown.markdown(md_text)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text(separator='\n')

def extract_epub_text(epub_path):
    book = epub.read_epub(epub_path)
    texts = []
    for item in book.get_items():
        if item.get_type() == epub.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            texts.append(soup.get_text(separator='\n'))
    return '\n'.join(texts)

def extract_html_text(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text(separator='\n')

def process_file(filepath, output_dir):
    ext = filepath.suffix.lower()
    try:
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        elif ext == '.md':
            with open(filepath, 'r', encoding='utf-8') as f:
                md = f.read()
            text = clean_markdown(md)
        elif ext == '.pdf':
            text = pdf_extract_text(str(filepath))
        elif ext == '.epub':
            text = extract_epub_text(str(filepath))
        elif ext in ['.html', '.htm']:
            text = extract_html_text(str(filepath))
        else:
            return  # Unsupported extension

        # Nettoyage supplémentaire : suppression des espaces multiples
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        # Sauvegarde dans le dossier de sortie
        output_path = output_dir / (filepath.stem + '.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Fichier traité : {filepath} -> {output_path}")
    except Exception as e:
        print(f"Erreur lors du traitement de {filepath}: {e}")

def process_directory(root_dir, output_dir):
    root_dir = Path(root_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            ext = filename.lower().split('.')[-1]
            if ext in ['txt', 'md', 'pdf', 'epub', 'html', 'htm']:
                filepath = Path(dirpath) / filename
                process_file(filepath, output_dir)

if __name__ == "__main__":
    dossier_a_traiter = "/Users/sodaa/Zotero"  # À adapter
    dossier_sortie = "/Users/sodaa/Desktop/rag"  # À adapter
    process_directory(dossier_a_traiter, dossier_sortie)
