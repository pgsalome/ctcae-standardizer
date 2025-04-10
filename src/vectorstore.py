# In src/vectorstore.py

import os
import logging
from typing import Optional, Dict, List, Any, Tuple

from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings

# Try to import IRISVector, fallback to FAISS if not available
try:
    from langchain_iris import IRISVector

    IRIS_AVAILABLE = True
except ImportError:
    from langchain_community.vectorstores import FAISS

    IRIS_AVAILABLE = False
    logging.warning("IRISVector not available, falling back to FAISS for local development")


def setup_vector_store(
        collection_name: str = "ctcae_terms",
        connection_string: Optional[str] = None,
        reset_collection: bool = False,
        local_index_path: Optional[str] = "data/vector_index"
) -> Any:
    """
    Set up a vector store (IRIS if available, FAISS as fallback).

    Args:
        collection_name: Name for the vector collection (IRIS only)
        connection_string: IRIS connection string (IRIS only)
        reset_collection: Whether to reset existing collection (IRIS only)
        local_index_path: Path to save local index (FAISS only)

    Returns:
        Vector store instance (IRISVector or FAISS)
    """
    # Initialize embeddings
    embedding_model = OpenAIEmbeddings()

    # Use IRIS if available
    if IRIS_AVAILABLE:
        # Default connection string if not provided
        if connection_string is None:
            username = os.getenv('IRIS_USERNAME', '_SYSTEM')
            password = os.getenv('IRIS_PASSWORD', 'SYS')
            hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
            port = os.getenv('IRIS_PORT', '1973')  # The mapped port
            namespace = os.getenv('IRIS_NAMESPACE', 'USER')
            connection_string = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"

        # If reset requested, try to delete the existing collection
        if reset_collection:
            try:
                temp_store = IRISVector(
                    embedding_function=embedding_model,
                    collection_name=collection_name,
                    connection_string=connection_string
                )
                logging.info(f"Deleting existing collection: {collection_name}")
                temp_store.delete_collection()
            except Exception as e:
                logging.debug(f"Collection deletion attempt: {e}")

        # Create new vectorstore
        try:
            # Initialize with a dummy document
            vectorstore = IRISVector.from_documents(
                documents=[Document(page_content="Initialization document")],
                embedding=embedding_model,
                collection_name=collection_name,
                connection_string=connection_string
            )
            logging.info(f"IRIS Vector store initialized: {collection_name}")

            # Try to remove initialization document
            try:
                vectorstore.delete(["Initialization document"])
            except Exception:
                pass

            return vectorstore
        except Exception as e:
            # If creation fails, try to connect to existing store
            logging.warning(f"Error creating IRIS vector store: {e}")
            logging.info("Attempting to connect to existing store...")

            try:
                return IRISVector(
                    embedding_function=embedding_model,
                    collection_name=collection_name,
                    connection_string=connection_string
                )
            except Exception as e2:
                logging.error(f"Could not connect to IRIS: {e2}")
                # Fall back to FAISS
                logging.warning("Falling back to FAISS for local storage")
                IRIS_AVAILABLE = False

    # Fallback to FAISS for local development
    if not IRIS_AVAILABLE:
        logging.info(f"Using FAISS vector store at {local_index_path}")
        os.makedirs(os.path.dirname(local_index_path), exist_ok=True)

        # Check if there's an existing index
        if os.path.exists(local_index_path) and not reset_collection:
            try:
                vectorstore = FAISS.load_local(local_index_path, embedding_model)
                logging.info(f"Loaded existing FAISS index from {local_index_path}")
                return vectorstore
            except Exception as e:
                logging.warning(f"Error loading FAISS index: {e}")

        # Create new FAISS index
        vectorstore = FAISS.from_documents(
            [Document(page_content="Initialization document")],
            embedding_model
        )
        vectorstore.save_local(local_index_path)
        logging.info(f"Created new FAISS index at {local_index_path}")
        return vectorstore