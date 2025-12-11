"""
Filename: add_manual.py
Project: AutoAssist - Vehicle Maintenance Question Answering Tool
Description:
    Command-line interface for ingesting new manuals. Wraps the
    manual_tools module to support bulk PDF importing and prepares
    the corpus for re-indexing.

Author: Kunal Sinha
Course: CS410 - Text Information Systems (Fall 2025), UIUC
"""

import argparse
from manual_tools import add_manual, find_all_pdfs


def main():
    parser = argparse.ArgumentParser(description="Add a new car manual.")
    parser.add_argument("--make", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--pdf", required=True,
                        help="A single PDF file OR a folder containing PDFs")

    args = parser.parse_args()

    # Accept file or folder
    pdf_input = args.pdf
    if os.path.isdir(pdf_input):
        pdf_paths = find_all_pdfs(pdf_input)
    else:
        pdf_paths = [pdf_input]

    add_manual(args.make, args.model, pdf_paths)

    print("\nRun: python src/tfidf_indexer.py  to rebuild the index.")


if __name__ == "__main__":
    main()