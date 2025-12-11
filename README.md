
# AutoAssist: Vehicle Maintenance Question Answering Tool
A CS410 Course Project - Fall 2025  
Author: Kunal Sinha (kunal7)

## Overview
AutoAssist is a retrieval-based question answering system designed to help users understand and troubleshoot vehicle issues using natural language. A person may describe a problem in everyday terms, and the system connects that description to technical procedures found in automotive service manuals. AutoAssist expands user queries into terminology commonly found in manuals, detects the vehicle make when possible, and retrieves the most relevant maintenance steps or diagnostic checks.

The system uses TF-IDF with cosine similarity for ranking passages, a rule-based expansion method for bridging informal and technical vocabulary, and a simple boosting mechanism to prioritize results for the detected manufacturer. A Streamlit application provides an accessible interface, and an evaluation module supports precision-based assessment of retrieval effectiveness.

## Data Pipeline
### 1. PDF to Raw Text
Service manuals are processed page by page. Each PDF page is extracted into a plain text file.

### 2. Passage Segmentation
Each page is split into passages using sentence boundaries and a minimum-length threshold. This improves search granularity and aligns with best practices in retrieval systems that operate over long documents.

### 3. Passage Aggregation
All passages for a given make are stored in jsonl files under:
```
data/corpus/<make>/passages/
```

### 4. TF-IDF Index Construction
A unified index is built for all makes. The process generates:
- `vectorizer.pkl`  
- `tfidf_matrix.pkl`  
- `metadata.pkl`

These artifacts allow the system to match user queries against the entire set of passages.

## System Architecture
### Query Normalization
A rule-based synonym expansion module maps common descriptions to technical language. This step improves recall and is intentionally transparent to show how input is interpreted.

### Retrieval Engine
The engine loads the TF-IDF index, transforms queries into the same vector space, applies cosine similarity, and ranks passages. If the make of the vehicle is detected, scores for matching passages are boosted before ranking.

### User Interface
A Streamlit interface allows users to:
- Enter a problem description  
- View the normalized query  
- See likely checks and open full instructions in the service manual  
- Upload new manuals through the “Add Manuals” interface  

### Manual Ingestion Pipeline
New manuals can be added without modifying the code. Uploading a PDF triggers text extraction, passage segmentation, and a rebuild of the TF-IDF index.

### Evaluation Module
An evaluation script guides a human evaluator through a set of predefined queries. For each query, the top five passages are shown, the linked PDFs are opened, and the evaluator marks relevant results. The tool then computes Precision@5, Recall@5, and F1@5.

## How to Run the System
### Installation
```
pip install -r requirements.txt
```

### Building the TF-IDF Index
```
python src/tfidf_indexer.py
```

### Launching the Application
```
streamlit run src/app.py
```

## Adding New Manuals
### Through the UI
Upload PDF files in the “Add New Manuals” section.

### Through the Command Line
```
python src/add_manual.py --make honda --model accord --pdf path/to/manual.pdf
```

This will copy the manual, extract its text, segment passages, and rebuild the index.

## Evaluation
Run:
```
python src/evaluate.py
```
The script outputs Precision@5, Recall@5, and F1@5 for each query and stores human judgments in:
```
human_judgments.json
```

## Design Decisions
### Choice of TF-IDF
TF-IDF is well understood, transparent, and suitable for a system whose goal is interpretability. It matches the instruction and theory taught in CS410, especially the Vector Space Model and traditional retrieval pipelines.

### Streamlit as the Interface
Streamlit allows rapid prototyping, clear layout, and a low barrier for graders who need to run and inspect the system.

### Rule-Based Query Expansion
Automotive manuals rely on consistent technical terminology. Query expansion compensates for differences between lay descriptions and these terms. A rule-based approach was chosen due to its reliability and predictability.

### Optional Language Model Integration
If needed, a language model could assist with summarization or query interpretation, but the system is designed to satisfy the course requirements using classical IR techniques alone.

## Summary
AutoAssist implements the full lifecycle of a classical retrieval system: parsing, segmentation, indexing, searching, ranking, evaluation, and user interaction. The system reflects the principles covered in CS410 and demonstrates how traditional IR techniques can solve a practical real-world problem.
