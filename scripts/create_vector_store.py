#!/usr/bin/env python3
"""
Create and populate vector store with CTCAE term data.
"""
import os
import sys
import json
import logging
from pathlib import Path
import dotenv

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import configure_logging

# Load environment variables from .env file
env_path = Path('.env')
if env_path.exists():
    dotenv.load_dotenv(env_path)
    print("Loaded environment variables from .env file")
else:
    print("Warning: .env file not found")

# Check if the OpenAI API key is set
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    print("Warning: OPENAI_API_KEY environment variable is not set")
else:
    print("OpenAI API key is set")

# Set the environment variable to allow iris import to work with containerized IRIS
os.environ['IRISINSTALLDIR'] = '/usr'

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
        # Import here to avoid circular imports
        from src.vectorstore import setup_vector_store, add_terms_to_vectorstore

        # Load CTCAE data
        with open(CTCAE_PATH, 'r') as f:
            ctcae_data = json.load(f)

        terms = ctcae_data.get("terms", [])
        if not terms:
            print("Error: No CTCAE terms found in the processed data")
            return False

        print(f"Setting up vector store for {len(terms)} CTCAE terms...")

        # Initialize vector store with direct connection parameters
        vectorstore = setup_vector_store(
            collection_name="ctcae_terms",
            connection_string=None,  # Will use default connection string
            reset_collection=True
        )

        # Add terms to vector store
        count = add_terms_to_vectorstore(vectorstore, terms)

        print(f"Successfully added {count} CTCAE term documents to vector store")
        return True
    except Exception as e:
        print(f"Error creating vector store: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = create_vector_store()
    sys.exit(0 if success else 1)