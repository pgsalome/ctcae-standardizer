#!/usr/bin/env python3
"""
Run the symptom matcher from command line.
"""
import os
import sys
import json
import argparse

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.symptom_matcher import SymptomMatcher
from src.utils import configure_logging


def main():
    parser = argparse.ArgumentParser(description="Match symptoms to CTCAE terminology")
    parser.add_argument("symptom", help="Symptom description to match")
    parser.add_argument("--details", help="Additional symptom details", default="")
    parser.add_argument("--collection", default="ctcae_terms",
                        help="Vector collection name")
    parser.add_argument("--model", default="gpt-3.5-turbo",
                        help="LLM model to use")
    parser.add_argument("--output", help="Path to save output JSON", default=None)
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed output")

    args = parser.parse_args()

    # Configure logging
    log_level = "INFO" if args.verbose else "WARNING"
    configure_logging(log_level)

    # Initialize symptom matcher
    matcher = SymptomMatcher(
        collection_name=args.collection,
        model_name=args.model
    )

    # Process symptom
    print(f"Processing symptom: {args.symptom}")
    result = matcher.match_symptom(args.symptom, args.details)

    # Display result
    print("\nResult:")
    print(f"CTCAE Term: {result.get('ctcae_term')}")
    print(f"Grade: {result.get('grade')}")
    print(f"Category: {result.get('meddra_soc')}")
    print(f"Match Confidence: {result.get('confidence')}")

    if args.verbose:
        print("\nDefinition:", result.get('definition'))
        print("\nGrade Description:", result.get('grade_description'))
        print("\nRationale:", result.get('rationale'))

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResult saved to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())