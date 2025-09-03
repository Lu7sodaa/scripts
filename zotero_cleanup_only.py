
#!/usr/bin/env python3
"""
Zotero Interactive Cleanup Script
Deletes incomplete items after user confirmation.
Requirements:
    pip install pyzotero
Usage:
    python zotero_cleanup_only.py --api-key YOUR_KEY --library-id YOUR_ID --library-type user
"""

import argparse
from pyzotero import zotero
from pyzotero.zotero_errors import UnsupportedParamsError

def is_incomplete(item, zot):
    data = item["data"]

    no_authors = not data.get("creators")
    no_publisher = not data.get("publisher") and not data.get("publicationTitle") and not data.get("journalAbbreviation")
    try:
        attachments = zot.children(item["key"], itemType="attachment")
    except Exception:
        attachments = []
    no_attachments = len(attachments) == 0

    return no_authors and no_publisher and no_attachments

def interactive_cleanup(zot, items):
    for item in items:
        if item["data"]["itemType"] in {"note", "attachment", "annotation"}:
            continue
        if is_incomplete(item, zot):
            title = item["data"].get("title", "[Sans titre]")
            print(f"⛔️ Incomplet : {title}")
            user_input = input("Supprimer ? (y/n) ").strip().lower()
            if user_input == "y":
                zot.delete_item(item)
                print("✅ Supprimé.\n")
            else:
                print("❌ Conservé.\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", required=True, help="Zotero API key with write access")
    ap.add_argument("--library-id", required=True, type=int, help="User or group library ID")
    ap.add_argument("--library-type", choices=["user", "group"], default="user")
    ap.add_argument("--limit", type=int, default=100, help="Batch size")
    args = ap.parse_args()

    zot = zotero.Zotero(args.library_id, args.library_type, args.api_key)

    start = 0
    while True:
        batch = zot.everything(zot.items(limit=args.limit, start=start))
        if not batch:
            break
        interactive_cleanup(zot, batch)
        start += args.limit

if __name__ == "__main__":
    main()
