#!/usr/bin/env python3
"""
Batch‑tagger for Zotero items
=============================

• Requires `pyzotero`  (pip install pyzotero).
• Tags items according to regex rules that distinguish:
    – patterns that must appear *in the title* only;
    – patterns that may appear in title, abstract or notes.

Usage
-----
$ python zotero_batch_tagger.py --api-key m887AJCU8Ch2Zjn5Jmztt9Dy --library-id 4675480 --library-type user

Optional:
    --tag-only    Apply to items missing the tag (skip already‑tagged)
    --dry-run     Show what would be done but do not write to the API
"""
import argparse
import re
from pyzotero import zotero
from pyzotero.zotero_errors import UnsupportedParamsError

# ---------------------- EDIT YOUR RULES HERE ----------------------
TAG_RULES = {
    "décolonial": {
        "title": [
            r"(?i)décolonial",
            r"(?i)colon",
            r"(?i)Sud",
            r"(?i)post[- ]colonial",
            r"(?i)indigène",
            r"(?i)occident",
            r"(?i)racial"],
        "any": [
            r"(?i)racisme",
            r"(?i)intersectionnel",
            r"(?i)angela davis",
            r"(?i)décolonial",
            r"(?i)bouteldja",
            r"(?i)césaire",
            r"(?i)fanon",
            r"(?i)bell hooks",
            r"(?i)panther",  # pour "Black Panther Party"
            r"(?i)épistémolog",
            r"(?i)autochtone",
            r"(?i)indigène",
            r"(?i)barbare",
            r"(?i)caraïbe",
            r"(?i)antiracisme"],
    },
    "Intelligence artificielle": {
        "title": [
            r"(?i)intelligence artificielle",
            r"(?i)\bIA\b",
            r"(?i)\bAI\b",
            r"(?i)machine learning",
            r"(?i)deep learning",
            r"(?i)modèle génératif",
            r"(?i)réseaux de neurones"],
        "any": [
            r"(?i)intelligence artificielle",
            r"(?i)\bIA\b",
            r"(?i)\bAI\b",
            r"(?i)machine learning",
            r"(?i)apprentissage automatique",
            r"(?i)deep learning",
            r"(?i)modèles génératifs?",
            r"(?i)chatgpt",
            r"(?i)gpt[- ]?\d+",
            r"(?i)openai",
            r"(?i)algorithme",
            r"(?i)automatisation",
            r"(?i)big data",
            r"(?i)données massives",
            r"(?i)vision par ordinateur",
            r"(?i)traitement du langage",
            r"(?i)intelligence computationnelle",
            r"(?i)turing",
            r"(?i)wiener",
            r"(?i)biais algorithmique",
            r"(?i)éthique de l'IA",
            r"(?i)surveillance algorithmique",
            r"(?i)robots intelligents"],
    },
    "Mouvements sociaux": {
        "title": [
            r"(?i)gilets jaunes",
            r"(?i)réforme des retraites",
            r"(?i)émeutes",
            r"(?i)soulèvements?",
            r"(?i)sainte[- ]soline",
            r"(?i)black bloc",
            r"(?i)sabotage",
            r"(?i)blocage"],
        "any": [
            r"(?i)gilets jaunes",
            r"(?i)mouvement social",
            r"(?i)réforme des retraites",
            r"(?i)manifestation",
            r"(?i)émeutes?",
            r"(?i)soulèvements?",
            r"(?i)soulèvement de la terre",
            r"(?i)sainte[- ]soline",
            r"(?i)black bloc",
            r"(?i)sabotage",
            r"(?i)éco-sabotage",
            r"(?i)blocage",
            r"(?i)action directe",
            r"(?i)zad",
            r"(?i)grève",
            r"(?i)pension",
            r"(?i)violence policière",
            r"(?i)lbd",
            r"(?i)militant écologiste",
            r"(?i)interpellation",
            r"(?i)révolte",
            r"(?i)quartiers populaires",
            r"(?i)banlieue"],
    },
    "Palestine": {
        "title": [
            r"(?i)palestin",
            r"(?i)gaza",
            r"(?i)cisjordanie",
            r"(?i)keffieh",
            r"(?i)intifada",
            r"(?i)sumud"],
        "any": [
            r"(?i)palestin",
            r"(?i)gaza",
            r"(?i)cisjordanie",
            r"(?i)hamas",
            r"(?i)fatah",
            r"(?i)keffieh",
            r"(?i)intifada",
            r"(?i)sumud",
            r"(?i)nabka",
            r"(?i)territoires occupés",
            r"(?i)colonisation israélienne",
            r"(?i)mur de séparation",
            r"(?i)blocus",
            r"(?i)apartheid israélien",
            r"(?i)boycott",
            r"(?i)bds",
            r"(?i)droit au retour",
            r"(?i)droit international humanitaire",
            r"(?i)génocide",
            r"(?i)occupation militaire",
            r"(?i)résistance palestinienne",
            r"(?i)camp de réfugiés",
            r"(?i)jerusalem",
            r"(?i)sionisme",
            r"(?i)tsahal"],
    },
    "Action sociale & précarité": {
        "title": [
            r"(?i)précarité",
            r"(?i)pauvreté",
            r"(?i)inégalités?",
            r"(?i)action sociale",
            r"(?i)exclusion",
            r"(?i)misère"],
        "any": [
            r"(?i)précarité",
            r"(?i)pauvreté",
            r"(?i)inégalités?",
            r"(?i)exclusion",
            r"(?i)misère",
            r"(?i)vulnérabilité",
            r"(?i)sans[- ]abri",
            r"(?i)sdf",
            r"(?i)logement précaire",
            r"(?i)hébergement d'urgence",
            r"(?i)personnes à la rue",
            r"(?i)urgence sociale",
            r"(?i)minima sociaux",
            r"(?i)rsa",
            r"(?i)cmu",
            r"(?i)aide alimentaire",
            r"(?i)distribution de repas",
            r"(?i)invisibles sociaux",
            r"(?i)travail social",
            r"(?i)travailleurs sociaux",
            r"(?i)éducateur spécialisé",
            r"(?i)accompagnement social",
            r"(?i)protection sociale",
            r"(?i)services sociaux",
            r"(?i)solidarité",
            r"(?i)stigmatisation",
            r"(?i)gouvernement des pauvres",
            r"(?i)contrôle social"],
    },
}
# ---------------------------------------------------------------------


def get_notes_text(zot, item):
    """Concatenate all child-note texts; return '' if item cannot have children."""
    if item["data"]["itemType"] in {"note", "attachment", "annotation"}:
        return ""
    try:
        notes = zot.children(item["key"], itemType="note", limit=100)
    except UnsupportedParamsError:
        return ""
    return " ".join(n["data"].get("note", "") or "" for n in notes)

def build_full_text(item, notes_text):
    title = item["data"].get("title", "")
    abstract = item["data"].get("abstractNote", "")
    return title, f"{title} {abstract} {notes_text}"

def already_tagged(item, tag):
    return any(t["tag"] == tag for t in item["data"].get("tags", []))

def apply_tags(zot, items, args):
    for item in items:
        if item["data"]["itemType"] in {"note", "attachment", "annotation"}:
            continue
        title, full = build_full_text(item, get_notes_text(zot, item))
        updates = []
        for tag, patterns in TAG_RULES.items():
            # Skip if tag exists and --tag-only is active
            if args.tag_only and already_tagged(item, tag):
                continue
            match = False
            # Title‑only patterns
            for rex in patterns["title"]:
                if re.search(rex, title):
                    match = True
                    break
            # Any‑field patterns
            if not match:
                for rex in patterns["any"]:
                    if re.search(rex, full):
                        match = True
                        break
            if match and not already_tagged(item, tag):
                item["data"]["tags"].append({"tag": tag, "type": 1})
                updates.append(tag)
        if updates:
            if args.dry_run:
                print(f"[DRY‑RUN] Would add {updates} to {item['key']}")
            else:
                zot.update_item(item)
                print(f"Added {updates} to {item['key']}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", required=True, help="Zotero API key with write access")
    ap.add_argument("--library-id", required=True, help="User or group library ID", type=int)
    ap.add_argument("--library-type", choices=["user", "group"], default="user")
    ap.add_argument("--limit", type=int, default=100, help="Batch fetch size")
    ap.add_argument("--tag-only", action="store_true", help="Only add tags if missing")
    ap.add_argument("--dry-run", action="store_true", help="Do not write modifications")
    args = ap.parse_args()

    zot = zotero.Zotero(args.library_id, args.library_type, args.api_key)

    start = 0
    while True:
        batch = zot.everything(zot.items(limit=args.limit, start=start))
        if not batch:
            break
        apply_tags(zot, batch, args)
        start += args.limit

if __name__ == "__main__":
    main()
