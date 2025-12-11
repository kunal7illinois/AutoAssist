"""
Filename: segment_passages.py
Project: AutoAssist - Vehicle Maintenance Question Answering Tool
Description:
    Converts extracted raw text into semantically meaningful
    passages using sentence tokenization. Outputs JSONL records
    containing metadata needed by the TF-IDF indexer.

Author: Kunal Sinha
Course: CS410 - Text Information Systems (Fall 2025), UIUC
"""

import os
import json
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
from pathlib import Path

from config import CORPUS_ROOT
ROOT = CORPUS_ROOT

def segment_text(text, min_len=40):
    sentences = sent_tokenize(text)
    passages = []
    chunk = []

    for s in sentences:
        chunk.append(s)
        if len(" ".join(chunk)) > min_len:
            passages.append(" ".join(chunk))
            chunk = []

    if chunk:
        passages.append(" ".join(chunk))

    return passages

def build_passages(make, model):
    raw_dir = os.path.join(ROOT, make, "raw_text")
    out_dir = os.path.join(ROOT, make, "passages")
    os.makedirs(out_dir, exist_ok=True)

    out_json = os.path.join(out_dir, f"{make}_passages.jsonl")
    jf = open(out_json, "w", encoding="utf-8")

    for fname in tqdm(os.listdir(raw_dir), desc=f"{make} passages"):
        if not fname.endswith(".txt"): continue

        pdf_stem = fname.rsplit("_page", 1)[0]
        page_num = fname.rsplit("_page", 1)[1].replace(".txt", "")

        text = open(os.path.join(raw_dir, fname), encoding="utf-8").read()
        passages = segment_text(text)

        for i, p in enumerate(passages):
            obj = {
                "doc_id": f"{make}_{pdf_stem}_p{page_num}_{i}",
                "make": make,
                "model": model,
                "source_pdf": f"{pdf_stem}.pdf",
                "page_number": int(page_num),
                "passage_index": i,
                "text": p
            }
            jf.write(json.dumps(obj) + "\n")

    jf.close()
    print(f"Saved → {out_json}")

def main():
    build_passages("mitsubishi", "Eclipse 2003-2005")
    build_passages("toyota", "Camry XV40")
    build_passages("honda", "Civic 2005-2011")

if __name__ == "__main__":
    main()
