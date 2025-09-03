import sqlite3
import os
import re
import time
from bs4 import BeautifulSoup  # Bibliothèque pour nettoyer le HTML

# Chemin vers la base de données SQLite de Zotero
ZOTERO_DB_PATH = "/Users/sodaa/Zotero/zotero.sqlite"

# Dossier de sortie pour les notes Markdown
OUTPUT_FOLDER = "/Users/sodaa/Documents/notes_zotero"

# Fonction pour nettoyer le contenu HTML des notes
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text().strip()

# Fonction pour tronquer les noms de fichier trop longs
def truncate_filename(filename, max_length=100):
    if len(filename) > max_length:
        return filename[:max_length].strip() + "..."
    return filename

# Fonction pour récupérer les métadonnées et les notes
def extract_notes_with_metadata():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    conn = sqlite3.connect(ZOTERO_DB_PATH)
    cursor = conn.cursor()

    # Nouvelle requête SQL pour récupérer les notes, les titres et les auteurs
    query = """
    SELECT itemDataValues.value AS title, itemNotes.note, 
           creators.firstName || ' ' || creators.lastName AS author
    FROM itemNotes
    LEFT JOIN items ON itemNotes.parentItemID = items.itemID
    LEFT JOIN itemData ON items.itemID = itemData.itemID
    LEFT JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
    LEFT JOIN itemCreators ON items.itemID = itemCreators.itemID
    LEFT JOIN creators ON itemCreators.creatorID = creators.creatorID
    WHERE itemDataValues.value IS NOT NULL
    """

    cursor.execute(query)
    notes = cursor.fetchall()

    for title, note_content, author in notes:
        if not note_content:
            continue  # Sauter les notes vides

        clean_title = truncate_filename(title.replace('/', '_').replace(':', '-').strip()) if title else f"Annotation_{int(time.time())}"
        file_path = os.path.join(OUTPUT_FOLDER, f"{clean_title}.md")

        # Nettoyage du contenu HTML
        cleaned_note = clean_html(note_content)

        # Ajouter les métadonnées YAML directement dans le fichier
        with open(file_path, "w", encoding="utf-8") as f:
            metadata_block = f"---\nTitre: {title if title else 'Inconnu'}\nAuteur: {author if author else 'Inconnu'}\n---\n\n"
            f.write(metadata_block + cleaned_note)
            print(f"✅ Note exportée avec métadonnées : {clean_title}.md")

    conn.close()

if __name__ == "__main__":
    extract_notes_with_metadata()