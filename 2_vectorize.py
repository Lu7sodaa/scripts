#!/usr/bin/env python3

import os
import argparse
from tqdm import tqdm
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Dossiers par défaut à utiliser (à adapter si besoin)
DEFAULT_PERSIST_DIRECTORY = "/Users/sodaa/RAG/knowledge"  # Doit correspondre au volume mappé pour OpenWebUI.
DEFAULT_INPUT_DIRECTORY = "/Users/sodaa/RAG/corpus/zotero0425"  # Dossier contenant tes documents nettoyés.

# S'assurer que le dossier de persistance existe
os.makedirs(DEFAULT_PERSIST_DIRECTORY, exist_ok=True)

def load_documents(input_dir: str):
    """
    Charge tous les fichiers .txt du dossier passé en argument et attribue le nom de fichier
    dans la métadonnée 'source' de chaque document.
    """
    documents = []
    files_to_process = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".txt"):
                path = os.path.join(root, file)
                files_to_process.append(path)

    for path in tqdm(files_to_process, desc="📄 Lecture des fichiers"):
        loader = TextLoader(path, encoding='utf-8')
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = os.path.basename(path)
        documents.extend(docs)

    return documents

def build_vector_store(documents, persist_dir, embedding_model, collection_name):
    """
    Vectorise la liste de documents, crée le vector store avec Chroma et le sauvegarde dans persist_dir.
    """
    print(f"🔢 {len(documents)} chunks prêts à être vectorisés.")
    print(f"📐 Chargement du modèle d'embedding : {embedding_model}")

    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={"device": "mps"},             # Adapté si tu utilises un Mac M1/M2 par exemple.
        encode_kwargs={"normalize_embeddings": True}
    )

    print("📊 Vectorisation en cours...")
    vectordb = Chroma.from_documents(
        documents,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name=collection_name
    )

    vectordb.persist()
    print("✅ Base vectorielle enregistrée dans :", persist_dir)

def main():
    parser = argparse.ArgumentParser(description="Script pour vectoriser le corpus et enregistrer la base Chroma.")
    parser.add_argument("--input_dir", type=str, default=DEFAULT_INPUT_DIRECTORY,
                        help="Chemin du corpus nettoyé (fichiers .txt).")
    # Pour forcer l'usage du bon dossier, on fixe la valeur par défaut pour output_dir
    parser.add_argument("--output_dir", type=str, default=DEFAULT_PERSIST_DIRECTORY,
                        help="Dossier de sortie Chroma (persist_directory).")
    parser.add_argument("--embedding_model", type=str, default="dangvantuan/sentence-camembert-large",
                        help="Nom du modèle d'embeddings à utiliser.")
    parser.add_argument("--collection_name", type=str, required=True,
                        help="Nom de la collection Chroma.")
    args = parser.parse_args()

    print("📂 Chargement des fichiers depuis :", args.input_dir)
    docs = load_documents(args.input_dir)

    # Ici, on s'assure que le dossier de sortie correspond bien au bon persist_directory pour OpenWebUI.
    build_vector_store(docs, args.output_dir, args.embedding_model, args.collection_name)

if __name__ == "__main__":
    main()
