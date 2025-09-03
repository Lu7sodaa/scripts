import os
import hashlib
from collections import defaultdict

def hash_file(path, chunk_size=8192):
    """Calcule le hash SHA256 d'un fichier donné."""
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        print(f"[Erreur] Impossible de lire {path} : {e}")
        return None

def find_duplicates(root_folder):
    hashes = defaultdict(list)

    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            file_hash = hash_file(full_path)
            if file_hash:
                hashes[file_hash].append(full_path)

    duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}
    return duplicates

if __name__ == "__main__":
    dossier = "/Volumes/sodaa.synology.me/video"
    print(f"Recherche de doublons dans : {dossier}\n")
    doublons = find_duplicates(dossier)

    if not doublons:
        print("✅ Aucun doublon trouvé.")
    else:
        print("❌ Doublons détectés :\n")
        for file_hash, files in doublons.items():
            print(f"--- Hash: {file_hash} ---")
            for path in files:
                print(f"  {path}")
            print()

