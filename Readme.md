Activer l'environnement virtuel Python
    source venv/bin/activate

Lancer le script 1_cleancorpus.py en spécifiant les paramètres : 
    python 1_cleancorpus.py \
  --input-dir /Users/sodaa/RAG/corpus/corpus2clean \
  --output-dir /Users/sodaa/RAG/corpus/corpus_clean \
  --chunk-size 512 \
  --overlap 100


Lancer le script 2_vectorize.py en spécifiant les paramètres : 
    python 2_vectorize.py \
  --input-dir /Users/sodaa/RAG/corpus/corpus_clean \
  --output-dir /Users/sodaa/RAG/chroma_store \
  --embedding-model dangvantuan/sentence-camembert-large
