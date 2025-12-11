"""
Filename: extract_pdfs.py
Project: AutoAssist - Vehicle Maintenance Question Answering Tool
Description:
    PDF extraction utility using pdfplumber. Processes each page
    into standalone text files for downstream passage segmentation.

    For each query:
    1. Show top-5 retrieved passages
    2. Automatically open all 5 PDFs so the evaluator can inspect them
    3. User marks which ones are relevant ("1 2 5", or "none")
    4. Computes Precision@5, Recall@5, and F1@5
    5. Saves human judgments into human_judgments.json

Author: Kunal Sinha
Course: CS410 - Text Information Systems (Fall 2025), UIUC
"""

import json
from search_engine import search, find_pdf_recursive
from query_normalizer import normalize_query
import subprocess
import os

# Queries used for evaluation (updated list)

TEST_QUERIES = [
    # CAR-SPECIFIC (6 queries)

    # 1 - Mitsubishi Eclipse, Idle Adjustment
    "Mitsubishi Eclipse idle speed adjustment and idle mixture inspection procedure",

    # 2 - Mitsubishi Eclipse, EVAP Leak
    "Mitsubishi Eclipse EVAP system inspection for fuel vapor leakage and fuel smell",

    # 3 - Toyota Camry, Drive Shaft Noise
    "Toyota Camry drive shaft noise or vibration while turning or accelerating",

    # 4 - Toyota Camry, SRS Warning Light
    "Toyota Camry SRS airbag system warning light on - need airbag precaution and connector diagrams",

    # 5 - Honda Civic, No-Start
    "Honda Civic no-start condition - check starter circuit, ignition switch, and battery",

    # 6 - Audi TT, CAN Bus Communication Failure
    "Audi TT diagnostic scan tool cannot communicate with vehicle modules - CAN bus inspection",


    # GENERAL / NON-SPECIFIC (4 queries)

    # 7 - General Engine Hesitation
    "engine hesitation or stumble during light acceleration, feels like misfire or poor fuel delivery",

    # 8 - General HVAC Weak Airflow
    "air conditioning blows weak airflow and cabin does not cool properly",

    # 9 - General Transmission Slipping
    "transmission slipping when accelerating from a stop, RPM rises but vehicle is slow",

    # 10 - General CAN Bus / Diagnostics Failure
    "diagnostic scan tool cannot communicate with vehicle modules, no response from ECU"
]

# Metrics for k = 5

def precision_at_k(hits, k=5):
    return hits / k

def recall_at_k(hits, total_relevant):
    if total_relevant == 0:
        return 0.0
    return hits / total_relevant

def f1_score(p, r):
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


# Helper: Open PDF

def open_pdf_file(pdf_path):
    try:
        if os.path.exists(pdf_path):
            subprocess.Popen([pdf_path], shell=True)
    except Exception as e:
        print("Error opening PDF:", e)


# Main evaluation loop\

def main():
    print("\nAutoAssist Manual Evaluation (Interactive Mode - P@5)")
    print("-----------------------------------------------------")
    print("For each query, top-5 results are shown AND opened.")
    print("Mark which ones are relevant (e.g., '1 4 5') or 'none'.\n")

    judgments = {}
    total_p = total_r = total_f = 0.0
    k = 5  # cutoff

    for query in TEST_QUERIES:
        print("\n=============================================")
        print("QUERY:", query)
        print("=============================================\n")

        normalized = normalize_query(query)
        results = search(normalized, top_k=5)

        # Automatically open all PDFs
        print("Opening all PDFs for inspection...")
        for i, r in enumerate(results, start=1):
            print(f"\n---- Result {i} ----")
            print(f"doc_id:   {r['doc_id']}")
            print(f"Manual:   {r['source_pdf']}")
            print(f"Make:     {r['make']}  |  Model: {r['model']}")
            print(f"Page:     {r['page_number']}")

            # Show excerpt
            excerpt = r['text'][:300].replace("\n", " ")
            if len(r['text']) > 300:
                excerpt += "..."
            print(f"Excerpt:  {excerpt}")

            # Open PDF
            pdf_path = find_pdf_recursive(r["make"], r["source_pdf"])
            if pdf_path:
                open_pdf_file(pdf_path)
            else:
                print("PDF not found.")

        # -------- Human relevance input --------
        while True:
            ans = input("\nWhich results are relevant? ('1 2 5', or 'none'): ").strip().lower()

            if ans == "none":
                relevant_indices = []
                break

            tokens = ans.split()
            if all(t.isdigit() and 1 <= int(t) <= 5 for t in tokens):
                relevant_indices = [int(t) for t in tokens]
                break

            print("Invalid input. Try again.")

        relevant_doc_ids = [results[i - 1]['doc_id'] for i in relevant_indices]
        judgments[query] = relevant_doc_ids

        # -------- Compute metrics --------
        hits = len(relevant_indices)
        total_relevant = len(relevant_indices)

        p = precision_at_k(hits, k)
        r = recall_at_k(hits, total_relevant)
        f = f1_score(p, r)

        print(f"\nPrecision@5: {p:.3f}")
        print(f"Recall@5:    {r:.3f}")
        print(f"F1@5:        {f:.3f}")

        total_p += p
        total_r += r
        total_f += f

    # -------- Macro averages --------
    n = len(TEST_QUERIES)
    print("\n=====================================")
    print("   Macro-Averaged Evaluation (k=5)")
    print("=====================================")
    print(f"Mean Precision@5: {total_p / n:.3f}")
    print(f"Mean Recall@5:    {total_r / n:.3f}")
    print(f"Mean F1@5:        {total_f / n:.3f}")

    # Save results
    with open("human_judgments.json", "w", encoding="utf-8") as f:
        json.dump(judgments, f, indent=2)

    print("\nSaved -> human_judgments.json\n")


if __name__ == "__main__":
    main()
