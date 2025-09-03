import os
import re
import spacy
import random
from collections import defaultdict
from spacy.lang.fr.stop_words import STOP_WORDS
from collections import Counter

# Installation de spaCy si nécessaire
try:
    nlp = spacy.load("fr_core_news_md")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "fr_core_news_md"])
    nlp = spacy.load("fr_core_news_md")

# Chemin vers le dossier contenant les notes Obsidian
NOTES_FOLDER = "/Users/sodaa/Documents/notes_zotero"

# Liste complète des concepts existants
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

# Suggestions de concepts potentiels
suggested_concepts = defaultdict(int)

# Fonction pour nettoyer et extraire le contenu sans métadonnées YAML
def extract_content(content):
    yaml_pattern = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
    content = re.sub(yaml_pattern, "", content).strip()
    return content

# Fonction pour détecter les concepts existants + suggérer de nouveaux concepts
def detect_entities(text):
    doc = nlp(text)
    entities = {ent.text.lower() for ent in doc.ents if ent.label_ in ["PER", "ORG", "LOC", "MISC"]}

    # Recherche de concepts existants
    for concept in CONCEPTS_LIST:
        if re.search(rf"\b{re.escape(concept)}\b", text, re.IGNORECASE):
            entities.add(concept)

    # Identification de termes pertinents (enrichissement)
    keywords = [token.text.lower() for token in doc if token.is_alpha and token.text.lower() not in STOP_WORDS]
    keyword_freq = Counter(keywords)

    # Proposer les mots-clés les plus récurrents qui ne sont pas déjà dans CONCEPTS_LIST
    for keyword, freq in keyword_freq.most_common(15):  # Top 15 mots-clés
        if keyword not in CONCEPTS_LIST:
            suggested_concepts[keyword] += freq

    tags = [f"#Concept/{e}" if e in entities else f"#Concept/{e}" for e in entities]
    return tags

# Fonction principale : vérification sur 30 notes aléatoires
def verify_concepts():
    note_samples = random.sample(
        [file for file in os.listdir(NOTES_FOLDER) if file.endswith(".md")], 30
    )

    with open(os.path.join(NOTES_FOLDER, "verif_concepts.md"), "w", encoding="utf-8") as f:
        f.write("# Vérification des concepts détectés\n\n")
        
        for file in note_samples:
            file_path = os.path.join(NOTES_FOLDER, file)
            with open(file_path, "r", encoding="utf-8") as f_read:
                content = f_read.read()

            text_content = extract_content(content)
            tags = detect_entities(text_content)

            f.write(f"**{file}** : {', '.join(tags) if tags else 'Aucun tag détecté'}\n")

            print(f"🔍 Vérification : {file} → {', '.join(tags) if tags else 'Aucun tag détecté'}")

    print("\n✅ Fichier de vérification créé : `verif_concepts.md`")

# Fonction pour ajouter les tags après validation
def add_tags_to_notes():
    for root, _, files in os.walk(NOTES_FOLDER):
        for file in files:
    
