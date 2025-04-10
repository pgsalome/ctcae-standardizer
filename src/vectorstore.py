# In src/vectorstore.py

import os
import logging
from typing import Optional, Dict, List, Any, Tuple
from pathlib import Path
import dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = Path('.env')
if env_path.exists():
    dotenv.load_dotenv(env_path)
    logger.info("Loaded environment variables from .env file")
else:
    logger.warning("Warning: .env file not found")

# Check if the OpenAI API key is set
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    logger.warning("Warning: OPENAI_API_KEY environment variable is not set")
else:
    logger.info("OpenAI API key is set")

from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain_iris import IRISVector

# Set the environment variable to allow iris import to work with containerized IRIS
os.environ['IRISINSTALLDIR'] = '/usr'


def setup_vector_store(
        collection_name: str = "ctcae_terms",
        connection_string: Optional[str] = None,
        reset_collection: bool = False
) -> Any:
    """
    Set up an IRIS vector store.

    Args:
        collection_name: Name for the vector collection
        connection_string: IRIS connection string
        reset_collection: Whether to reset existing collection

    Returns:
        Vector store instance (IRISVector)
    """
    # Get OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set")

    # Initialize embeddings
    embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Default connection string if not provided
    if connection_string is None:
        username = '_SYSTEM'
        password = 'SYS'
        hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
        port = os.getenv('IRIS_PORT', '1972')
        namespace = 'USER'
        connection_string = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"

    logger.info(f"Using connection string: {connection_string}")

    # If reset requested, try to delete the existing collection
    if reset_collection:
        try:
            logger.info(f"Attempting to delete existing collection: {collection_name}")
            temp_store = IRISVector(
                embedding_function=embedding_model,
                collection_name=collection_name,
                connection_string=connection_string
            )
            temp_store.delete_collection()
            logger.info(f"Successfully deleted collection: {collection_name}")
        except Exception as e:
            logger.info(f"No existing collection to delete or error occurred: {e}")

    # Create new vectorstore
    try:
        logger.info(f"Creating new vector store: {collection_name}")
        vectorstore = IRISVector.from_documents(
            documents=[Document(page_content="Initialization document")],
            embedding=embedding_model,
            collection_name=collection_name,
            connection_string=connection_string
        )
        logger.info(f"IRIS Vector store initialized: {collection_name}")

        # Try to remove initialization document
        try:
            vectorstore.delete(["Initialization document"])
        except:
            logger.info("Note: Could not remove initialization document, but collection was created.")

        return vectorstore
    except Exception as e:
        logger.warning(f"Error creating vector store: {e}")
        logger.info("Attempting to connect to existing store instead...")

        # Connect to existing vector store
        vectorstore = IRISVector(
            embedding_function=embedding_model,
            collection_name=collection_name,
            connection_string=connection_string
        )
        logger.info(f"Connected to existing vector store: {collection_name}")
        return vectorstore


# Add alias for backward compatibility
setup_iris_vectorstore = setup_vector_store


def add_terms_to_vectorstore(vectorstore: Any, terms: List[Dict[str, Any]]) -> int:
    """
    Add CTCAE terms to vector store.

    Args:
        vectorstore: Vector store instance
        terms: List of CTCAE term dictionaries

    Returns:
        Number of documents added
    """
    documents = []

    # Create documents for term definitions
    for term in terms:
        term_name = term.get("ctcae_term", "")
        if not term_name:
            continue

        # Create a document for the term definition
        term_content = f"CTCAE Term: {term_name}\n"
        term_content += f"Definition: {term.get('definition', '')}\n"
        term_content += f"Category: {term.get('meddra_soc', '')}"

        term_doc = Document(
            page_content=term_content,
            metadata={
                "ctcae_term": term_name,
                "meddra_soc": term.get("meddra_soc", ""),
                "definition": term.get("definition", ""),
                "meddra_code": term.get("meddra_code", ""),
                "doc_type": "term"
            }
        )
        documents.append(term_doc)

        # Create documents for each grade description
        for grade in term.get("grades", []):
            grade_num = grade.get("grade", "")
            description = grade.get("description", "")

            if grade_num and description:
                grade_content = f"CTCAE Term: {term_name} - Grade {grade_num}\n"
                grade_content += f"Description: {description}\n"
                grade_content += f"Category: {term.get('meddra_soc', '')}"

                grade_doc = Document(
                    page_content=grade_content,
                    metadata={
                        "ctcae_term": term_name,
                        "grade": grade_num,
                        "description": description,
                        "meddra_soc": term.get("meddra_soc", ""),
                        "doc_type": "grade_description"
                    }
                )
                documents.append(grade_doc)

    logger.info(f"Created {len(documents)} documents to add to vector store")

    # Add documents to vector store in batches
    batch_size = 100
    total_added = 0

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        try:
            logger.info(f"Adding batch {i // batch_size + 1} of {len(documents) // batch_size + 1}")
            vectorstore.add_documents(batch)
            total_added += len(batch)
            logger.info(f"Added batch of {len(batch)} documents ({total_added}/{len(documents)})")
        except Exception as e:
            logger.error(f"Error adding batch to vector store: {e}")
            import traceback
            traceback.print_exc()

    return total_added


def search_term_store(
        vectorstore: Any,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, str]] = None
) -> List[Tuple[Document, float]]:
    """
    Search for terms in the vector store.

    Args:
        vectorstore: Vector store instance
        query: Search query
        k: Number of results to return
        filter_dict: Filter to apply to search

    Returns:
        List of (document, score) tuples
    """
    try:
        results = vectorstore.similarity_search_with_score(
            query,
            k=k,
            filter=filter_dict
        )
        return results
    except Exception as e:
        logger.error(f"Error searching vector store: {e}")
        return []