"""
Vector store implementation for InterSystems IRIS.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Tuple

from langchain.docstore.document import Document
from langchain_iris import IRISVector
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)


def setup_iris_vectorstore(
        collection_name: str = "ctcae_terms",
        connection_string: Optional[str] = None,
        reset_collection: bool = False
) -> IRISVector:
    """
    Set up an IRIS vector store with the specified collection.

    Args:
        collection_name: Name for the vector collection
        connection_string: IRIS connection string (if None, uses environment variables)
        reset_collection: Whether to reset the collection if it exists

    Returns:
        An initialized IRISVector store
    """
    # Default connection string if not provided
    if connection_string is None:
        username = os.getenv('IRIS_USERNAME', '_SYSTEM')
        password = os.getenv('IRIS_PASSWORD', 'SYS')
        hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
        port = os.getenv('IRIS_PORT', '1972')
        namespace = os.getenv('IRIS_NAMESPACE', 'USER')
        connection_string = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"

    # Initialize embeddings
    embedding_model = OpenAIEmbeddings()

    # If reset requested, try to delete the existing collection
    if reset_collection:
        try:
            temp_store = IRISVector(
                embedding_function=embedding_model,
                collection_name=collection_name,
                connection_string=connection_string
            )
            logger.info(f"Deleting existing collection: {collection_name}")
            temp_store.delete_collection()
        except Exception as e:
            logger.debug(f"Collection deletion attempt: {e}")

    # Create new vectorstore
    try:
        # Initialize with a dummy document
        vectorstore = IRISVector.from_documents(
            documents=[Document(page_content="Initialization document")],
            embedding=embedding_model,
            collection_name=collection_name,
            connection_string=connection_string
        )
        logger.info(f"Vector store initialized: {collection_name}")

        # Try to remove initialization document
        try:
            vectorstore.delete(["Initialization document"])
        except Exception:
            pass

        return vectorstore
    except Exception as e:
        # If creation fails, try to connect to existing store
        logger.warning(f"Error creating vector store: {e}")
        logger.info("Attempting to connect to existing store...")

        return IRISVector(
            embedding_function=embedding_model,
            collection_name=collection_name,
            connection_string=connection_string
        )


def add_terms_to_vectorstore(
        vectorstore: IRISVector,
        terms: List[Dict[str, Any]]
) -> int:
    """
    Add CTCAE terms to the vector store.

    Args:
        vectorstore: The IRIS vector store
        terms: List of CTCAE term dictionaries to add

    Returns:
        Number of documents added
    """
    documents = []

    for term in terms:
        # Create a document for general term information
        term_doc = Document(
            page_content=f"{term.get('ctcae_term')}: {term.get('definition')}",
            metadata={
                "meddra_code": term.get("meddra_code", ""),
                "meddra_soc": term.get("meddra_soc", ""),
                "ctcae_term": term.get("ctcae_term", ""),
                "definition": term.get("definition", ""),
                "doc_type": "term"
            }
        )
        documents.append(term_doc)

        # Create separate documents for each grade description
        for grade_info in term.get("grades", []):
            grade_doc = Document(
                page_content=f"{term.get('ctcae_term')} Grade {grade_info.get('grade')}: {grade_info.get('description')}",
                metadata={
                    "meddra_code": term.get("meddra_code", ""),
                    "meddra_soc": term.get("meddra_soc", ""),
                    "ctcae_term": term.get("ctcae_term", ""),
                    "grade": grade_info.get("grade", ""),
                    "description": grade_info.get("description", ""),
                    "doc_type": "grade_description"
                }
            )
            documents.append(grade_doc)

    # Add all documents to the vector store
    vectorstore.add_documents(documents)
    logger.info(f"Added {len(documents)} documents to vector store")

    return len(documents)


def search_term_store(
        vectorstore: IRISVector,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
) -> List[Tuple[Document, float]]:
    """
    Search the vector store for relevant CTCAE terms.

    Args:
        vectorstore: The IRIS vector store
        query: Search query
        k: Number of results to return
        filter_dict: Optional filter dictionary

    Returns:
        List of (document, score) tuples
    """
    try:
        if filter_dict:
            results = vectorstore.similarity_search_with_score(
                query, k=k, filter=filter_dict
            )
        else:
            results = vectorstore.similarity_search_with_score(query, k=k)

        return results
    except Exception as e:
        logger.error(f"Error searching vector store: {e}")
        return []