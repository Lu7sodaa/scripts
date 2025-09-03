from sentence_transformers import SentenceTransformer, models
from transformers import CamembertTokenizer

model_name = "dangvantuan/sentence-camembert-large"
tokenizer_name = "camembert-base"  # Tokenizer SentencePiece stable

# On force un tokenizer slow et compatible SentencePiece
tokenizer = CamembertTokenizer.from_pretrained(tokenizer_name)

# Le modèle de transformer à charger
word_embedding_model = models.Transformer(
    model_name_or_path="dangvantuan/sentence-camembert-large",
    tokenizer_name_or_path="camembert-base",
    max_seq_length=512
)


pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
sentence_model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

sentence_model.save("/Users/sodaa/RAG/models/camembert-converted")
print("✅ Modèle converti avec succès.")
