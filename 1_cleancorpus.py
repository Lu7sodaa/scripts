import os
import hashlib
import argparse
from pathlib import Path
from unstructured.partition.auto import partition
from tqdm import tqdm


def hash_text(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def chunk_text(text, chunk_size, overlap):
    tokens = text.split()
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk = " ".join(tokens[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def clean_and_chunk_file(file_path, input_dir, output_dir, chunk_size, overlap):
    try:
        elements = partition(filename=str(file_path))
        raw_text = "\n".join([str(el) for el in elements if str(el).strip()])
        chunks = chunk_text(raw_text, chunk_size, overlap)
        rel_path = file_path.relative_to(input_dir).with_suffix("")

        for i, chunk in enumerate(chunks):
            chunk_hash = hash_text(chunk)
            chunk_file = output_dir / rel_path.parent / f"{rel_path.stem}_chunk{i:03}_{chunk_hash}.txt"
            chunk_file.parent.mkdir(parents=True, exist_ok=True)
            chunk_file.write_text(chunk, encoding="utf-8")
    except Exception as e:
        print(f"[!] Erreur avec le fichier {file_path} : {e}")


def process_corpus(input_dir, output_dir, chunk_size, overlap):
    all_files = list(input_dir.rglob("*.*"))
    print(f"Traitement de {len(all_files)} fichiers...")
    for file in tqdm(all_files):
        clean_and_chunk_file(file, input_dir, output_dir, chunk_size, overlap)


def main():
    parser = argparse.ArgumentParser(description="Nettoie et découpe un corpus pour RAG")
    parser.add_argument("--input-dir", required=True, type=Path, help="Dossier source brut")
    parser.add_argument("--output-dir", required=True, type=Path, help="Dossier de sortie pour les chunks")
    parser.add_argument("--chunk-size", type=int, default=750, help="Taille des chunks (en tokens)")
    parser.add_argument("--overlap", type=int, default=200, help="Recouvrement entre les chunks (en tokens)")
    args = parser.parse_args()

    process_corpus(args.input_dir, args.output_dir, args.chunk_size, args.overlap)


if __name__ == "__main__":
    main()
