"""
Filename: bulk_add_manuals.py
Project: AutoAssist - Vehicle Maintenance Question Answering Tool
Description:
    Multi-threaded ingestion script for large batches of car manuals.
    Identifies new PDFs, extracts text, segments passages, and
    triggers a full TF-IDF index rebuild.

Author: Kunal Sinha
Course: CS410 - Text Information Systems (Fall 2025), UIUC
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm

from manual_tools import add_manual, find_all_pdfs
from tfidf_indexer import main as rebuild_index
from config import MANUALS_ROOT

RAW_ROOT = r"C:\Users\Kunal\Documents\CS 410 Project\Old\autoassist\RAW DATA"

# Cars to process (folder name → (make, model))
CARS = {
    "Audi Mk2": ("audi", "mk2"),
    "Honda Civic": ("honda", "civic"),
    "Mitsubishi Eclipse": ("mitsubishi", "eclipse"),
    "Subaru brz": ("subaru", "brz"),
    "Toyota Camry": ("toyota", "camry"),
}


def get_new_pdfs_for_make(folder_path: str, make: str):
    """
    Find all PDFs under folder_path, but skip ones that already exist
    in data/manuals/<make>/ with the same filename.
    """
    all_pdfs = find_all_pdfs(folder_path)

    if not all_pdfs:
        return []

    dest_dir = os.path.join(MANUALS_ROOT, make.lower())
    os.makedirs(dest_dir, exist_ok=True)

    new_pdfs = []
    for src_pdf in all_pdfs:
        dest_pdf = os.path.join(dest_dir, os.path.basename(src_pdf))
        if os.path.exists(dest_pdf):
            continue
        new_pdfs.append(src_pdf)

    return new_pdfs


def process_car(folder_name: str, make: str, model: str):
    folder_path = os.path.join(RAW_ROOT, folder_name)

    if not os.path.exists(folder_path):
        return f"Skipped {folder_name} (folder not found)"

    # Find only NEW PDFs for this make
    new_pdfs = get_new_pdfs_for_make(folder_path, make)

    if not new_pdfs:
        return f"No new PDFs for {folder_name} (all duplicates or none found)"

    msg_lines = [f"Processing {folder_name} ({make} {model})"]

    # Show a per-car progress bar over the NEW PDFs we’re about to ingest
    for _ in tqdm(
        new_pdfs,
        desc=f"{folder_name} - new PDFs",
        unit="pdf",
        leave=False,
    ):
        pass

    add_manual(make, model, new_pdfs)

    msg_lines.append(f"Finished {folder_name}: {len(new_pdfs)} new PDF(s) added")
    return "\n".join(msg_lines)


def main():
    print("\n AutoAssist Corpus Rebuilder (Multi-threaded)\n")
    print(f"RAW root: {RAW_ROOT}\n")

    tasks = []
    with ThreadPoolExecutor(max_workers=min(5, len(CARS))) as executor:
        # Submit each car as a separate job
        for folder_name, (make, model) in CARS.items():
            tasks.append(
                executor.submit(process_car, folder_name, make, model)
            )

        # Overall progress bar over cars
        for future in tqdm(
            as_completed(tasks),
            total=len(tasks),
            desc="Overall progress (cars)",
            unit="car",
        ):
            result_msg = future.result()
            if result_msg:
                print("\n" + result_msg)

    print("\n All car jobs completed. Rebuilding TF-IDF index once...")
    rebuild_index()
    print(" Done! All available manuals are now indexed.\n")


if __name__ == "__main__":
    main()
