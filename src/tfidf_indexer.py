"""
Filename: tfidf_indexer.py
Project: AutoAssist - Vehicle Maintenance Question Answering Tool
Description:

    Builds the TF-IDF vector index over all segmented passages
    from the corpus. Saves the vectorizer, sparse matrix, and
    metadata to disk for fast querying.

    This script loads the segmented passages stored under data/corpus/<make>/passages,
    builds a unified TF-IDF index, and saves three artifacts:

        - vectorizer.pkl     (TF-IDF vocabulary + weighting)
        - tfidf_matrix.pkl   (matrix of passage vectors)
        - metadata.pkl       (list of metadata dictionaries, one per passage)

    A unique doc_id is added for each passage so the system can compute
    evaluation metrics such as Precision@k and Recall@k. 

Author: Kunal Sinha
Course: CS410 - Text Information Systems (Fall 2025), UIUC
"""

import os
import json
import pickle
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer

from config import CORPUS_ROOT, INDEX_ROOT


def collect_passage_files():
    """Collect all passage .jsonl files for any make present in the corpus."""
    passage_files = []

    for make in os.listdir(CORPUS_ROOT):
        make_dir = os.path.join(CORPUS_ROOT, make)
        if not os.path.isdir(make_dir):
            continue

        path = os.path.join(make_dir, "passages", f"{make}_passages.jsonl")
        if os.path.exists(path):
            passage_files.append(path)

    return passage_files


def load_passages():
    """
    Load all passage texts and keep their metadata.
    Each JSONL line is expected to contain:
        text, make, model, source_pdf, page_number, ...

    We attach a unique doc_id to every passage.
    """
    passage_files = collect_passage_files()

    passages = []
    metadata = []
    counter = 0  # used to generate unique doc_id values

    for path in passage_files:
        print(f"Loading: {path}")

        with open(path, "r", encoding="utf-8") as f:
            for line in tqdm(f, desc="Reading passages"):
                record = json.loads(line)

                # Create the doc_id
                make = record.get("make", "unknown")
                pdf = record.get("source_pdf", "unknown").replace(" ", "_")
                page = record.get("page_number", 0)

                doc_id = f"{make}_{pdf}_p{page}_{counter}"
                record["doc_id"] = doc_id

                passages.append(record["text"])
                metadata.append(record)

                counter += 1

    print(f"Total passages loaded: {len(passages)}")
    return passages, metadata


def build_tfidf(passages):
    """Fit a TF-IDF vectorizer and compute the document-term matrix."""
    print("Building TF-IDF index...")

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        max_df=0.95,
        min_df=2,
        ngram_range=(1, 2)
    )

    tfidf_matrix = vectorizer.fit_transform(passages)

    print("TF-IDF matrix shape:", tfidf_matrix.shape)
    return vectorizer, tfidf_matrix


def save_index(vectorizer, tfidf_matrix, metadata):
    """Write the artifacts to disk under data/corpus/index/."""
    os.makedirs(INDEX_ROOT, exist_ok=True)

    with open(os.path.join(INDEX_ROOT, "vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)

    with open(os.path.join(INDEX_ROOT, "tfidf_matrix.pkl"), "wb") as f:
        pickle.dump(tfidf_matrix, f)

    with open(os.path.join(INDEX_ROOT, "metadata.pkl"), "wb") as f:
        pickle.dump(metadata, f)

    print("Index successfully saved.")


def main():
    passages, metadata = load_passages()
    vectorizer, tfidf_matrix = build_tfidf(passages)
    save_index(vectorizer, tfidf_matrix, metadata)


if __name__ == "__main__":
    main()
