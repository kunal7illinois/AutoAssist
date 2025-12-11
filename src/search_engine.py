"""
Filename: search_engine.py
Project: AutoAssist - Vehicle Maintenance Question Answering Tool
Description:

    Core retrieval engine performing cosine similarity search over
    the TF-IDF index. Includes manufacturer detection, scoring,
    PDF linking, and pretty-print utilities for the interactive CLI.

    Performs TF-IDF cosine similarity search over all vehicle maintenance
    passages. After displaying top-k results, allows the user to select a
    result number to open the corresponding PDF. Entering 0 skips to the
    next query.

Author: Kunal Sinha
Course: CS410 - Text Information Systems (Fall 2025), UIUC
"""

import os
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import subprocess

from query_normalizer import normalize_query

# Path to index files
from config import INDEX_ROOT, MANUALS_ROOT, CORPUS_ROOT, PROJECT_ROOT

def detect_car_make(query):
    """
    Dynamically detect car manufacturer based on manuals present
    in data/manuals/. This makes detection future-proof as 
    new manuals/makes are added by the user.
    """

    query = query.lower()

    # Scan available makes from local folder structure
    try:
        makes = [
            d.lower() 
            for d in os.listdir(MANUALS_ROOT) 
            if os.path.isdir(os.path.join(MANUALS_ROOT, d))
        ]
    except Exception:
        makes = []

    # Try direct match of make name in query
    for make in makes:
        if make in query:
            return make

    # Fallback: try basic model-name detection from metadata (after index loaded)
    try:
        _, _, metadata = load_index()
        model_names = { m["model"].lower(): m["make"].lower() for m in metadata }
        for model, make in model_names.items():
            if model.lower() in query:
                return make
    except:
        pass

    return None


def highlight_terms(text, query):
    """Bold any words from the query that appear in the text."""
    query_words = query.lower().split()
    highlighted = text
    for w in query_words:
        if len(w) > 2:  # avoid highlighting "at", "in", etc.
            highlighted = highlighted.replace(
                w, f"\033[1m{w}\033[0m"
            )
    return highlighted

def load_index():
    """Loads the TF-IDF vectorizer, matrix, and metadata."""
    with open(os.path.join(INDEX_ROOT, "vectorizer.pkl"), "rb") as f:
        vectorizer = pickle.load(f)

    with open(os.path.join(INDEX_ROOT, "tfidf_matrix.pkl"), "rb") as f:
        tfidf_matrix = pickle.load(f)

    with open(os.path.join(INDEX_ROOT, "metadata.pkl"), "rb") as f:
        metadata = pickle.load(f)

    return vectorizer, tfidf_matrix, metadata


def search(query, top_k=5, car_make=None):
    """
    Performs a cosine similarity search against the TF-IDF matrix.

    Returns:
        A list of metadata dictionaries including:
        - make
        - model
        - source_pdf
        - page_number
        - score
    """
    vectorizer, tfidf_matrix, metadata = load_index()

    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # Apply car-make boost BEFORE selecting top-K results
    if car_make:
        for i, meta in enumerate(metadata):
            if meta["make"].lower() == car_make.lower():
                scores[i] *= 2

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        entry = metadata[idx].copy()
        entry["score"] = float(scores[idx])
        results.append(entry)

    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results



def pretty_print(results, query=None):
    for i, r in enumerate(results, start=1):
        text = r.get("text", "")
        lower_text = text.lower()

        excerpt_raw = text[:250].replace("\n", " ") + ("..." if len(text) > 250 else "")

        # Highlight query terms
        if query:
            excerpt = highlight_terms(excerpt_raw.lower(), query)
        else:
            excerpt = excerpt_raw

        print(f"\n=== Recommended Check / Likely Cause {i} ===")
        print(f"doc_id:      {r['doc_id']}")   # <-- ADDED LINE

        # Optional helpful flag
        action_keywords = ["check", "inspect", "replace", "adjust", "diagnose", "verify"]
        if any(kw in lower_text for kw in action_keywords):
            print("This passage includes actionable steps.")

        print(f"Score:       {r['score']:.4f}")
        print(f"Make:        {r['make']}")
        print(f"Model:       {r['model']}")
        print(f"Manual:      {r['source_pdf']}")
        print(f"Page:        {r['page_number']}")
        print(f"Excerpt:     {excerpt}")


def find_pdf_recursive(make, pdf_name):
    """Search for a PDF anywhere under data/manuals/."""
    for root, _, files in os.walk(MANUALS_ROOT):
        for f in files:
            if f.lower() == pdf_name.lower():
                return os.path.join(root, f)
    return None

def open_pdf(result):
    make = result["make"].lower()
    pdf_name = result["source_pdf"]

    pdf_path = find_pdf_recursive(make, pdf_name)

    if pdf_path and os.path.exists(pdf_path):
        print(f"Opening: {pdf_path}")
        subprocess.Popen([pdf_path], shell=True)
    else:
        print("Could not locate PDF:", pdf_name)


def main():

    print("AutoAssist Vehicle Maintenance Search Engine")
    print("Type 'quit' to exit.")
    print()

    while True:
        query = input("Enter your question: ")
        if query.lower().strip() == "quit":
            break

        # Auto-detect make
        detected_make = detect_car_make(query)
        if detected_make:
            print(f"\nDetected manufacturer: {detected_make.capitalize()} (boosting relevant results)")
        else:
            print("\nNo manufacturer detected in query.")

        normalized_query = normalize_query(query)
        if normalized_query != query.lower():
            print(f"\nNormalized query: {normalized_query}")


        results = search(normalized_query, top_k=5, car_make=detected_make)
        pretty_print(results, query=normalized_query)


        if not results:
            print("No results found.\n")
            continue

        while True:
            choice = input("Enter result number to open its PDF (0 to continue): ").strip()

            if not choice.isdigit():
                print("Please enter a number.")
                continue

            choice = int(choice)

            if choice == 0:
                print()
                break

            if 1 <= choice <= len(results):
                open_pdf(results[choice - 1])
                print()
                break
            else:
                print("Invalid number. Try again.")


if __name__ == "__main__":

    main()
