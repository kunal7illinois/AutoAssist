"""
Filename: manual_tools.py
Project: AutoAssist - Vehicle Maintenance Question Answering Tool
Description:
    Utility module for adding new car manuals to the system.
    Handles PDF discovery, copying, text extraction, and routing
    into the corpus structure used for TF-IDF indexing.

Author: Kunal Sinha
Course: CS410 - Text Information Systems (Fall 2025), UIUC
"""

import os
from config import MANUALS_ROOT, CORPUS_ROOT
from extract_pdfs import process_pdf_with_pages
from segment_passages import build_passages


def find_all_pdfs(path):
    """Return a list of all PDF file paths under the provided directory."""
    pdfs = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdfs.append(os.path.join(root, f))
    return pdfs


def add_manual(make, model, pdf_paths):
    """
    Add a new manual to the system.
    Args:
        make (str): manufacturer name
        model (str): model name
        pdf_paths (List[str]): absolute paths to PDF files
    """

    make = make.lower()
    model = model.lower()

    # Folder for manuals of this make
    manual_root = os.path.join(MANUALS_ROOT, make)
    os.makedirs(manual_root, exist_ok=True)

    print(f"Adding manuals to: {manual_root}")

    copied_pdf_paths = []

    # Copy PDFs locally into data/manuals/<make>/
    for src_pdf in pdf_paths:
        dest = os.path.join(manual_root, os.path.basename(src_pdf))
        with open(src_pdf, "rb") as fsrc, open(dest, "wb") as fdst:
            fdst.write(fsrc.read())

        print(f" - Copied {os.path.basename(src_pdf)}")
        copied_pdf_paths.append(dest)

    # Extract raw text into data/corpus/<make>/raw_text/
    raw_text_dir = os.path.join(CORPUS_ROOT, make, "raw_text")
    os.makedirs(raw_text_dir, exist_ok=True)

    print("\nExtracting text pages...")
    for pdf in copied_pdf_paths:
        process_pdf_with_pages(pdf, raw_text_dir)

    # Segment passages
    print("Segmenting into passages...")
    build_passages(make, model)

    print("\nManual added successfully.")
    return True
