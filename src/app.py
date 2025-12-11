"""
Filename: app.py
Project: AutoAssist - Vehicle Maintenance Question Answering Tool
Description:
    Streamlit-based web interface for:
        (1) TF-IDF based troubleshooting search
        (2) Uploading and integrating new manuals
    Provides a user-friendly diagnosis workflow for graders.

Author: Kunal Sinha
Course: CS410 - Text Information Systems (Fall 2025), UIUC
"""

import os
import streamlit as st
import subprocess

from search_engine import search, find_pdf_recursive, detect_car_make
from query_normalizer import normalize_query
from manual_tools import add_manual
from config import MANUALS_ROOT

from tfidf_indexer import main as build_index


# STREAMLIT PAGE SETTINGS

st.set_page_config(page_title="AutoAssist", layout="wide")
st.title("AutoAssist - Vehicle Troubleshooting Assistant")



# SECTION 1 - DIAGNOSIS TOOL

st.header("Diagnose a Car Problem")

query = st.text_input("Describe your car problem:")

if st.button("Diagnose"):
    if not query.strip():
        st.warning("Please enter a problem description.")
        st.stop()

    normalized = normalize_query(query)
    st.write("### Normalized Query")
    st.code(normalized)

    detected_make = detect_car_make(normalized)
    if detected_make:
        st.write(f"**Detected Manufacturer:** {detected_make.title()}")
        st.success(f"Boosting results for: {detected_make.title()}")
    else:
        st.info("No manufacturer detectedm, ranking unboosted.")

    results = search(normalized, top_k=5, car_make=detected_make)

    if not results:
        st.error("No results found.")
        st.stop()

    st.subheader("Most likely checks to perform")

    for i, r in enumerate(results, start=1):
        st.markdown(f"### {i}. {r['make'].title()} - Page {r['page_number']}")
        st.write(f"**Model:** {r['model']}")
        st.write(f"**Manual:** {r['source_pdf']}")
        st.write(f"**Score:** {r['score']:.4f}")

        excerpt = r["text"][:350].replace("\n", " ") + "..."
        st.write(f"**Excerpt:** {excerpt}")

        # Clickable PDF link
        
        st.write("**Open full instructions in the service manual:**")

        pdf_path = find_pdf_recursive(r["make"], r["source_pdf"])
        if pdf_path:
            st.markdown(f"[Open PDF]({pdf_path})")
            st.write(f"**Page Number:** {r['page_number']}")
        else:
            st.warning("PDF not found.")


# SECTION 2 - ADDING A NEW MANUAL

st.header("Add New Manuals")

st.write("Upload one or more PDF files to add a new manual to the system.")

col1, col2 = st.columns(2)
with col1:
    make = st.text_input("Make (e.g., Honda)")
with col2:
    model = st.text_input("Model (e.g., Accord)")

uploaded_files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)

if st.button("Add Manual"):
    if not make or not model:
        st.error("Make and model are required.")
        st.stop()
    if not uploaded_files:
        st.error("Please upload at least one PDF.")
        st.stop()

    st.info("Processing manuals… this may take a minute.")

    # STEP 1 - Save uploads to temp
    progress = st.progress(0)
    temp_paths = []

    for i, f in enumerate(uploaded_files):
        temp_path = f"temp_{f.name}"
        with open(temp_path, "wb") as out:
            out.write(f.read())
        temp_paths.append(temp_path)
        progress.progress((i+1) / len(uploaded_files))

    # STEP 2 - Add manual to corpus
    st.write("Extracting text and building passages...")
    progress.progress(0.3)

    add_manual(make, model, temp_paths)

    progress.progress(0.6)

    # STEP 3 - Rebuild TF-IDF index
    st.write("Rebuilding TF-IDF index...")
    from tfidf_indexer import main as build_index
    build_index()

    progress.progress(1.0)

    # Cleanup temps
    for p in temp_paths:
        os.remove(p)

    st.success(f"Manual added and index rebuilt! {make.title()} {model.title()} is now searchable.")
