from chromadb import PersistentClient

client = PersistentClient(path="/Users/sodaa/RAG/knowledge/zotero-full")
collections = client.list_collections()

print("📦 Collections disponibles :")
for c in collections:
    print(f"- Name: {c}")
