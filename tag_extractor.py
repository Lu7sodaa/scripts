import os
import re
import spacy
from collections import Counter
from spacy.lang.fr.stop_words import STOP_WORDS

# Installation de spaCy si nécessaire
try:
    nlp = spacy.load("fr_core_news_md")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "fr_core_news_md"])
    nlp = spacy.load("fr_core_news_md")

# Chemin vers le dossier contenant les notes Obsidian
NOTES_FOLDER = "/Users/sodaa/Documents/temp_notes_zotero"

# Liste complète des concepts existants à EXCLURE
CONCEPTS_LIST = [
    "immanence", "biopolitique", "rhizome", "épistémologie", "ontologie",
    "capitalisme", "destitution", "révolution", "communisme", "affect", "affection", 
    "police", "société", "économie", "émeute", "forme", "institution", "insurrection", 
    "néolibéral", "peuple", "réel", "agencement", "anarchiste", "capital", "civilisation", 
    "langage", "classes", "conatus", "pulsion", "contrôle", "imitation", "corps", "démocratie", 
    "désir", "imagination", "individu", "joie", "justice", "légitimité", "politique", 
    "populisme", "pouvoir", "puissance", "relation", "sabotage", "travail", "usage", "amour", 
    "artiste", "attentat", "autochtone", "autonome", "autre", "banlieue", "catastrophe", "commun", 
    "communauté", "communisme", "commune", "communication", "complot", "conflit", "consentement", 
    "contrainte", "critique", "cybernétique", "désastre", "déterminisme", "dette", "division du travail", 
    "échelle", "espoir", "évènement", "étendue", "pensée", "fragmentation", "genre", "gouverner", 
    "hétéronomie", "horizontalité", "information", "ingouvernable", "libertaire", "liens", "masse", 
    "militant", "militer", "mobilisation", "obséquium", "imperium", "panoptique", "république", 
    "rencontre", "situation", "souveraineté", "spectacle", "structure", "surveillance", "technologie", 
    "technique", "temps", "transindividuel", "utopie", "tristesse"
]

# Dictionnaire pour stocker les concepts et leur fréquence
concepts_counter = Counter()

# Fonction pour nettoyer et extraire le contenu sans métadonnées YAML
def extract_content(content):
    yaml_pattern = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
    content = re.sub(yaml_pattern, "", content).strip()
    return content

# Fonction pour extraire les concepts potentiels
def detect_concepts(text):
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.is_alpha and token.text.lower() not in STOP_WORDS]
    keyword_freq = Counter(keywords)

    # Ajouter les concepts récurrents non listés dans CONCEPTS_LIST
    for keyword, freq in keyword_freq.items():
        if keyword not in CONCEPTS_LIST and freq >= 5:  # Ajuster la fréquence pour limiter le bruit
            concepts_counter[keyword] += freq

# Fonction principale
def analyze_all_notes():
    for root, _, files in os.walk(NOTES_FOLDER):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                text_content = extract_content(content)
                detect_concepts(text_content)

    # Générer les 200 concepts les plus pertinents
    top_concepts = concepts_counter.most_common(200)

    with open(os.path.join(NOTES_FOLDER, "concepts_proposés.md"), "w", encoding="utf-8") as f:
        f.write("# Concepts proposés pour validation (200 max)\n\n")
        for concept, freq in top_concepts:
            f.write(f"- {concept} (fréquence : {freq})\n")

    print("\n✅ Fichier 'concepts_proposés.md' créé avec succès !")

if __name__ == "__main__":
    print("🔍 Analyse de l'ensemble de tes notes en cours...")
    analyze_all_notes()
    print("✅ Analyse terminée ! Vérifie le fichier `concepts_proposés.md`")
