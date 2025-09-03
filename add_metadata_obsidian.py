import os
import sqlite3

# Chemin vers la base de données SQLite de Zotero
ZOTERO_DB_PATH = "/Users/sodaa/Zotero/zotero.sqlite"

# Dossier contenant les notes Markdown exportées
NOTES_FOLDER = "/Users/sodaa/Documents/notes_zotero"

# Fonction pour récupérer les métadonnées (titre et auteur) depuis la base Zotero
def fetch_metadata():
    conn = sqlite3.connect(ZOTERO_DB_PATH)
    cursor = conn.cursor()

    query = """
    SELECT items.itemID, itemDataValues.value AS title, creators.firstName || ' ' || creators.lastName AS author
    FROM items
    JOIN itemData ON items.itemID = itemData.itemID
    JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
    JOIN itemCreators ON items.itemID = itemCreators.itemID
    JOIN creators ON itemCreators.creatorID = creators.creatorID
    WHERE itemDataValues.value IS NOT NULL
    """

    cursor.execute(query)
    metadata = {str(item[1]).replace('/', '_').replace(':', '-') : (item[1], item[2]) for item in cursor.fetchall()}

    conn.close()
    return metadata

# Fonction pour ajouter les métadonnées dans les notes Markdown
def add_metadata_to_notes(metadata):
    for filename in os.listdir(NOTES_FOLDER):
        if filename.endswith(".md"):
            file_path = os.path.join(NOTES_FOLDER, filename)
            title, author = metadata.get(filename[:-3], (None, None))

            if title and author:
                with open(file_path, "r+", encoding="utf-8") as f:
                    content = f.read()
                    f.seek(0, 0)
                    # Ajouter les métadonnées au format YAML en début de fichier
                    metadata_block = f"---\nTitre: {title}\nAuteur: {author}\n---\n\n"
                    f.write(metadata_block + content)
                    print(f"✅ Métadonnées ajoutées : {filename}")
            else:
                print(f"⚠️ Métadonnées non trouvées pour : {filename}")

if __name__ == "__main__":
    metadata = fetch_metadata()
    add_metadata_to_notes(metadata)
