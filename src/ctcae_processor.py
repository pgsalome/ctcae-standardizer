"""
Process and manage CTCAE terminology.
"""
import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path


class CTCAEProcessor:
    """
    Utility class for managing and processing CTCAE terminology.
    """

    def __init__(self, ctcae_path: Optional[str] = None):
        """
        Initialize the CTCAE processor.

        Args:
            ctcae_path: Path to the processed CTCAE JSON file
        """
        self.ctcae_path = ctcae_path or os.path.join("data", "ctcae_processed.json")
        self.terms = []
        self.categories = []
        self._load_data()

    def _load_data(self) -> bool:
        """
        Load CTCAE data from JSON file.

        Returns:
            Success status as boolean
        """
        try:
            with open(self.ctcae_path, 'r') as f:
                data = json.load(f)

            self.terms = data.get("terms", [])
            self.categories = data.get("categories", [])

            return len(self.terms) > 0
        except Exception as e:
            print(f"Error loading CTCAE data: {e}")
            return False

    def get_term_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a CTCAE term by name.

        Args:
            name: Name of the CTCAE term

        Returns:
            Term dictionary or None if not found
        """
        for term in self.terms:
            if term.get("ctcae_term", "").lower() == name.lower():
                return term
        return None

    def get_grade_description(self, term_name: str, grade: str) -> Optional[str]:
        """
        Get the description for a specific grade of a CTCAE term.

        Args:
            term_name: Name of the CTCAE term
            grade: Grade number (1-5) as string

        Returns:
            Grade description or None if not found
        """
        term = self.get_term_by_name(term_name)
        if not term:
            return None

        for grade_info in term.get("grades", []):
            if grade_info.get("grade") == grade:
                return grade_info.get("description")

        return None

    def get_term_categories(self) -> List[str]:
        """
        Get all available CTCAE term categories.

        Returns:
            List of category names
        """
        return self.categories.copy()

    def get_terms_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all CTCAE terms in a specific category.

        Args:
            category: Category name

        Returns:
            List of term dictionaries
        """
        return [term for term in self.terms if term.get("meddra_soc") == category]

    def search_terms(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for CTCAE terms by keyword.

        Args:
            query: Search query

        Returns:
            List of matching term dictionaries
        """
        query = query.lower()
        results = []

        for term in self.terms:
            # Search in term name
            if query in term.get("ctcae_term", "").lower():
                results.append(term)
                continue

            # Search in definition
            if query in term.get("definition", "").lower():
                results.append(term)
                continue

            # Search in grade descriptions
            for grade in term.get("grades", []):
                if query in grade.get("description", "").lower():
                    results.append(term)
                    break

        return results