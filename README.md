# AutoAssist: Vehicle Maintenance Search Engine

Course: CS410 - Text Information Systems, UIUC  
Author: Kunal Sinha  
Repo: https://github.com/kunal7illinois/AutoAssist

---

## Table of Contents
1. [Overview and Motivation](#1-overview-and-motivation)  
2. [System Features](#2-system-features)  
3. [Data Pipeline](#3-data-pipeline)  
4. [Architecture](#4-architecture)  
5. [Setup and Installation](#5-setup-and-installation)  
6. [Using AutoAssist (UI and CLI)](#6-using-autoassist-ui-and-cli)  
7. [Performance and Evaluation](#7-performance-and-evaluation)  
8. [Limitations and Future Work](#8-limitations-and-future-work)

---

## 1. Overview and Motivation
AutoAssist is a lightweight search engine that makes car maintenance information easier to find. Most cars do not come with a single clean service manual. They come with many separate PDF documents, each covering different subsystems. A single problem might appear in a flowchart in one manual, a replacement guide in another, and a short note in a troubleshooting table somewhere else.

AutoAssist treats all manuals as one text corpus instead of a set of disconnected files. It converts them into searchable passages, builds a TF IDF index, and lets you search across everything at once. You type a short problem description, and it surfaces the most relevant passages with links back to the exact PDF page.

The goal: make it fast and practical to navigate large sets of manuals and connect a symptom to the pages that actually help.

---

## 2. System Features
1. **Full corpus search**  
   All manuals across all makes and models are indexed into one TF IDF index.

2. **Manual ingestion workflow**  
   Add PDFs from the Streamlit UI or CLI. The system extracts text and segments passages automatically.

3. **Two interfaces: Streamlit UI and CLI**  
   Both use the same index and retrieval engine.

4. **Passage level retrieval with page links**  
   Results include the source PDF and exact page, with one-click opening.

5. **Query normalization and expansion**  
   A rule based normalizer expands certain problem terms to improve recall.

6. **Car make detection and boosting**  
   If a make is mentioned, relevant passages receive a ranking boost.

7. **Rebuildable TF IDF index**  
   Rebuild the index after adding new manuals.

8. **Evaluation module**  
   Runs a set of queries and produces Precision@5, Recall@5, and F1.

---

## 3. Data Pipeline
1. **PDF to raw text**  
   PDFs are processed page by page into plain text.

2. **Passage segmentation**  
   Text pages are split into smaller passages and stored as JSONL with metadata.

3. **Corpus assembly and indexing**  
   All passages are combined, vectorized with TF IDF, and stored with metadata.

4. **Query processing and scoring**  
   Queries are normalized, vectorized, scored with cosine similarity, and returned with metadata.

---

## 4. Architecture
```text
                          +------------------------------+
                          |          PDF Manual          |
                          |   (user provided or local)   |
                          +--------------+---------------+
                                         |
                                         v
+----------------------------------------------------------------------------------+
| Manual Ingestion Tools (manual_tools.py, add_manual.py, bulk_add_manuals.py)     |
| - Accept new manuals from CLI or Streamlit                                      |
| - Copy PDFs into project structure                                              |
| - Trigger text extraction and passage segmentation                              |
| - Optionally rebuild TF IDF index                                               |
+------------------------------+--------------------------------------------------+
                               |
                               v
                        +--------------------------------------+
                        |           extract_pdfs.py            |
                        |   Converts each PDF page to text     |
                        +------------------+-------------------+
                                         |
                                         v
                +--------------------------------------------------+
                |                segment_passages.py               |
                | Splits extracted text into passages and writes   |
                | JSONL records with metadata                      |
                +------------------+-------------------------------+
                                         |
                                         v
                +--------------------------------------------------+
                |                tfidf_indexer.py                  |
                | Builds TF IDF index and stores vectorizer,       |
                | matrix, and metadata                             |
                +------------------+-------------------------------+
                                         |
                                         v
+----------------------------------------------------------------------------------+
|                                search_engine.py                                  |
| Loads index, normalizes query, scores passages, and returns results              |
+--------------------------------+-------------------------------------------------+
                                         |
                                         |
                    +--------------------+---------------------+
                    |                                          |
                    v                                          v
      +---------------------------+               +------------------------------+
      |       CLI Interface       |               |    Streamlit UI (app.py)     |
      | - Direct queries          |               | - Search and ingestion        |
      | - Evaluation mode         |               | - Open PDF pages              |
      +---------------------------+               +------------------------------+
                                                         |
                                                         v
                                        +----------------+----------------+
                                        |          evaluate.py            |
                                        | Runs test queries and computes  |
                                        | P@5, R@5, and F1                |
                                        +---------------------------------+
```

---

## 5. Setup and Installation

### 5.1 Prerequisites
- Python 3.9+  
- pip  
- Git (optional)  
- Any PDF reader  

### 5.2 Get the Code
```bash
git clone https://github.com/kunal7illinois/AutoAssist.git
cd AutoAssist
```

Or download ZIP from GitHub.

### 5.3 Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5.4 Set Up the Data Directory
Download the manuals package from Google Drive and place folders into:

```text
AutoAssist/data/
    manuals/
    corpus/
    Test_Manuals/
```

The repo already includes the TF IDF index.

---

## 6. Using AutoAssist (UI and CLI)

### 6.1 Run the Streamlit UI
```bash
streamlit run src/app.py
```

### 6.2 Search in the UI
Enter a problem description and click Diagnose.  
Open any result with the "Open PDF" link.

If a PDF takes time, wait a few seconds or refresh.

### 6.3 Add Manuals in the UI
Upload:
- single PDFs  
- multiple PDFs  
- full folders  

The index rebuilds automatically.

### 6.4 CLI Tools

#### Search
```bash
python src/search_engine.py
```

#### Manual Ingestion
```bash
python src/add_manual.py --make test --model sample --pdf path/to/folder
python src/tfidf_indexer.py
```

#### Evaluation
```bash
python src/evaluate.py
```

---

## 7. Performance and Evaluation

Ten queries were used to test a range of real automotive issues.  
Macro averaged results:

- Precision@5: 0.600  
- Recall@5: 1.000  
- F1@5: 0.709  

The system always returned at least one relevant passage.

**Queries used:**
1. Mitsubishi Eclipse idle speed adjustment  
2. Mitsubishi Eclipse EVAP leak  
3. Toyota Camry drive shaft noise  
4. Toyota Camry SRS warning  
5. Honda Civic no-start  
6. Audi TT CAN bus failure  
7. General engine hesitation  
8. Weak AC airflow  
9. Transmission slipping  
10. General CAN bus / ECU communication failure  

### Strengths
- Always surfaced something relevant  
- Accurate PDF links  
- Helpful cross-manual retrieval  
- Make boosting helped ranking  

### Limitations
- Precision varied  
- Rule-based normalizer missed some phrasing  
- Duplicate passages from manuals  
- Occasionally ranked another make higher  

---

## 8. Limitations and Future Work
- **LLM-based query normalization** to better match user language to technical terminology.  
- **Semantic re-ranking** on top of TF IDF to improve precision.  
- **Cleaner passage segmentation** and better handling of repeated content.  
- **Optional cloud/manual storage** for lighter installations.  

The core pipeline works well, and improving query handling and ranking will bring the largest performance gains.

