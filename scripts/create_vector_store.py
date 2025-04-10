#!/usr/bin/env python3
"""
Create and populate vector store with CTCAE term data.
"""
import os
import sys
import json
import logging
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vectorstore import setup_iris_vectorstore, add_terms_to_vectorstore
from src.utils import configure_logging

# Path to processed CTCAE data
CTCAE_PATH = Path("data/ctcae_processed.json")


def create_vector_store():
    """Create and populate the IRIS vector store with CTCAE terms."""
    configure_logging()

    if not CTCAE_PATH.exists():
        print(f"Error: Processed CTCAE data not found at {CTCAE_PATH}")
        print("Please run process_ctcae.py first.")
        return False

    try:
        # Load CTCAE data
        with open(CTCAE_PATH, 'r') as f:
            ctcae_data = json.load(f)

        terms = ctcae_data.get("terms", [])
        if not terms:
            print("Error: No CTCAE terms found in the processed data")
            return False

        print(f"Setting up vector store for {len(terms)} CTCAE terms...")
        # Initialize vector store
        vectorstore = setup_iris_vectorstore(
            collection_name="ctcae_terms",
            reset_collection=True
        )

        # Add terms to vector store
        count = add_terms_to_vectorstore(vectorstore, terms)

        print(f"Successfully added {count} CTCAE term documents to vector store")
        return True
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return False


if __name__ == "__main__":
    success = create_vector_store()
    sys.exit(0 if success else 1)