"""
Filename: config.py
Project: AutoAssist - Vehicle Maintenance Question Answering Tool
Description:
    Centralized configuration for directory paths including
    project root, corpus storage, manual storage, and index files.
    Ensures consistency across all modules.

Author: Kunal Sinha
Course: CS410 - Text Information Systems (Fall 2025), UIUC
"""

import os

# Automatically locate the project root (directory above src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directories
DATA_ROOT = os.path.join(PROJECT_ROOT, "data")
CORPUS_ROOT = os.path.join(DATA_ROOT, "corpus")
INDEX_ROOT = os.path.join(CORPUS_ROOT, "index")
MANUALS_ROOT = os.path.join(DATA_ROOT, "manuals")