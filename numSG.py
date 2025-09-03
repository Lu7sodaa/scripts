import fitz  # PyMuPDF
import pandas as pd
from pathlib import Path
import re

# Chemin du dossier contenant les PDF
dossier = Path("/Users/sodaa/desktop")
pdf_files = [f for f in Path("/Users/sodaa/Desktop/stephanie").glob("*.pdf") if not f.name.startswith("._")]
operations = []

date_re = re.compile(r"^\d{2}/\d{2}/\d{4} \d{2}/\d{2}/\d{4}$")
montant_re = re.compile(r"^\d{1,3}(?:[ .]\d{3})*,\d{2}$")  # ex : 1 016,05

for pdf_path in pdf_files:
    doc = fitz.open(pdf_path)
    for page in doc:
        lines = page.get_text("text").split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if date_re.match(line):
                date, date_val = line.split()
                i += 1
                libelle = ""
                montant = ""

                # Lire les lignes suivantes jusqu’à trouver le montant
                while i < len(lines):
                    next_line = lines[i].strip()
                    if montant_re.match(next_line.replace(" ", "")):
                        montant = next_line.replace(" ", "").replace(".", "").replace(",", ".")
                        i += 1
                        break
                    else:
                        libelle += " " + next_line
                        i += 1

                montant = float(montant)
                credit = montant if any(kw in libelle.upper() for kw in ["VIR RECU", "CAF", "REMBOURSEMENT"]) else ""
                debit = montant if credit == "" else ""

                operations.append({
                    "Date": date,
                    "Date valeur": date_val,
                    "Libellé": libelle.strip(),
                    "Débit (€)": debit,
                    "Crédit (€)": credit,
                    "Source": pdf_path.name
                })
            else:
                i += 1

# Export vers Excel
df = pd.DataFrame(operations)
df.to_excel("releves_bancaires.xlsx", index=False)
print(f"✅ {len(df)} opérations extraites depuis {len(pdf_files)} fichiers.")
