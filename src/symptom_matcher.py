"""
Symptom matching to CTCAE terminology.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Tuple

from langchain.docstore.document import Document
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

from src.vectorstore import setup_iris_vectorstore, search_term_store

logger = logging.getLogger(__name__)


class SymptomMatcher:
    """
    Match symptoms to CTCAE terminology using RAG.
    """

    def __init__(
            self,
            collection_name: str = "ctcae_terms",
            model_name: str = "gpt-3.5-turbo"
    ):
        """
        Initialize the symptom matcher.

        Args:
            collection_name: Name of the vector collection
            model_name: LLM model name to use
        """
        self.vector_store = setup_iris_vectorstore(collection_name=collection_name)
        self.llm = ChatOpenAI(model_name=model_name, temperature=0)

        # Create matching prompt
        self.matching_prompt = ChatPromptTemplate.from_template(
            """You are a medical expert in standardizing symptom descriptions to CTCAE terminology.

            Please analyze the following patient symptom:

            Patient symptom: {symptom}
            Additional details: {details}

            Based on the following CTCAE reference information:

            {context}

            Instructions:
            1. Identify the most appropriate CTCAE term
            2. Determine the appropriate grade (1-5)
            3. Provide rationale for your selection

            Return your response in this JSON format:
            {
              "ctcae_term": "The matched CTCAE term",
              "grade": "The grade as a number (1-5)",
              "grade_description": "The official description for this grade",
              "meddra_soc": "The MedDRA system organ class",
              "confidence": "high/medium/low",
              "rationale": "Your explanation"
            }
            """
        )

    def match_symptom(
            self,
            symptom: str,
            details: str = ""
    ) -> Dict[str, Any]:
        """
        Match a symptom description to CTCAE terminology.

        Args:
            symptom: Symptom description
            details: Additional symptom details

        Returns:
            Dictionary with matching results
        """
        # Step 1: Search for relevant CTCAE terms
        term_results = search_term_store(
            self.vector_store,
            symptom,
            k=3,
            filter_dict={"doc_type": "term"}
        )

        # Step 2: Search for relevant grade descriptions
        grade_results = search_term_store(
            self.vector_store,
            symptom + " " + details,
            k=5,
            filter_dict={"doc_type": "grade_description"}
        )

        # Combine results
        all_results = term_results + grade_results

        # Create context from search results
        context_parts = []

        for doc, score in all_results:
            metadata = doc.metadata

            if metadata.get("doc_type") == "term":
                context_parts.append(
                    f"CTCAE Term: {metadata.get('ctcae_term')}\n"
                    f"MedDRA SOC: {metadata.get('meddra_soc')}\n"
                    f"Definition: {metadata.get('definition')}\n"
                    f"Similarity: {score:.4f}"
                )
            else:  # grade description
                context_parts.append(
                    f"CTCAE Term: {metadata.get('ctcae_term')}\n"
                    f"Grade: {metadata.get('grade')}\n"
                    f"Description: {metadata.get('description')}\n"
                    f"Similarity: {score:.4f}"
                )

        context = "\n\n".join(context_parts)

        # Step 3: Use LLM to make the final match
        chain = LLMChain(llm=self.llm, prompt=self.matching_prompt)

        try:
            # Extract symptoms using LLM
            response = chain.run(symptom=symptom, details=details, context=context)

            # Parse JSON response
            import json
            result = json.loads(response.strip())

            # Add original symptom to result
            result["original_symptom"] = symptom
            if details:
                result["details"] = details

            return result

        except Exception as e:
            logger.error(f"Error matching symptom: {e}")
            return {
                "original_symptom": symptom,
                "error": str(e)
            }