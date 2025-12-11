"""
Filename: extract_pdfs.py
Project: AutoAssist - Vehicle Maintenance Question Answering Tool
Description:
    PDF extraction utility using pdfplumber. Processes each page
    into standalone text files for downstream passage segmentation.

Author: Kunal Sinha
Course: CS410 - Text Information Systems (Fall 2025), UIUC
"""

import os
import pdfplumber
from pathlib import Path
from tqdm import tqdm

from config import PROJECT_ROOT, CORPUS_ROOT, MANUALS_ROOT
ROOT = PROJECT_ROOT
OUTPUT_ROOT = CORPUS_ROOT

MANUFACTURERS = {
    "mitsubishi": "mitsubishi-eclipse_2000-2005",
    "toyota": "Toyota-Camry-Aurion-XV40-Workshop-Manual",
    "honda": "2005_to_2011_Honda_Civic_Workshop_Manual.pdf"
}

def process_pdf_with_pages(pdf_path, out_dir):
    """Extract text from each page and save as separate files with metadata."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                outname = f"{Path(pdf_path).stem}_page{i}.txt"
                with open(os.path.join(out_dir, outname), "w", encoding="utf-8") as f:
                    f.write(text)
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

def process_manufacturer(name, rel_path):
    manu_raw_dir = os.path.join(OUTPUT_ROOT, name, "raw_text")
    os.makedirs(manu_raw_dir, exist_ok=True)

    print(f"\n Processing: {name}")

    if name == "honda":
        pdf_file = os.path.join(ROOT, rel_path)
        process_pdf_with_pages(pdf_file, manu_raw_dir)
        return

    root_dir = os.path.join(ROOT, rel_path)
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                process_pdf_with_pages(pdf_path, manu_raw_dir)

def main():
    for manu, rel_path in MANUFACTURERS.items():
        process_manufacturer(manu, rel_path)

if __name__ == "__main__":
    main()
