from pathlib import Path
from readability import Document
from bs4 import BeautifulSoup
from fpdf import FPDF

STORAGE_DIR = Path("/Users/sodaa/Zotero_backup/storage")
FONT_PATH = "/Users/sodaa/scripts/DejaVuSans.ttf"  # Police Unicode

def extract_text_from_html(html_path):
    try:
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
        doc = Document(html)
        title = doc.title()
        summary_html = doc.summary()
        soup = BeautifulSoup(summary_html, "html.parser")
        text = soup.get_text(separator="\n")
        return title.strip(), text
    except Exception as e:
        print(f"[!] Erreur lecture HTML : {html_path} → {e}")
        return None, None

def save_text_as_pdf(title, text, output_path):
    try:
        pdf = FPDF()
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("DejaVu", size=14)
        pdf.multi_cell(0, 10, txt=title, align='L')
        pdf.ln(5)
        pdf.set_font("DejaVu", size=11)
        for line in text.splitlines():
            pdf.multi_cell(0, 8, txt=line.strip(), align='L')
        pdf.output(output_path)
        print(f"[✓] PDF créé : {output_path}")
    except Exception as e:
        print(f"[!] Erreur génération PDF : {output_path} → {e}")

def main():
    for subdir in STORAGE_DIR.iterdir():
        if subdir.is_dir():
            for file in subdir.iterdir():
                if file.suffix.lower() == ".html":
                    title, text = extract_text_from_html(file)
                    if title and text:
                        output_pdf = subdir / f"{file.stem}.pdf"
                        save_text_as_pdf(title, text, output_pdf)

if __name__ == "__main__":
    main()
