#!/usr/bin/env python3
"""
Process the CTCAE Excel file and extract structured data.
"""
import os
import sys
import json
import pandas as pd
from pathlib import Path

# Path to CTCAE Excel file
CTCAE_PATH = Path("data/CTCAE_v5.0.xlsx")
OUTPUT_PATH = Path("data/ctcae_processed.json")


def process_ctcae():
    """Extract and process CTCAE data from Excel file."""
    if not CTCAE_PATH.exists():
        print(f"Error: CTCAE file not found at {CTCAE_PATH}")
        print("Please run download_ctcae.py first.")
        return False

    print(f"Processing CTCAE data from {CTCAE_PATH}...")
    try:
        # Read Excel file - get the sheet with the CTCAE terms
        # Usually the first sheet, but we'll check all sheets to be sure
        xl = pd.ExcelFile(CTCAE_PATH)
        ctcae_data = None

        # Try to identify the correct sheet by looking for expected columns
        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            # Check if this sheet has the expected columns
            expected_cols = ["MedDRA Code", "CTCAE Term", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"]
            if all(col in df.columns for col in expected_cols):
                ctcae_data = df
                print(f"Found CTCAE data in sheet: {sheet_name}")
                break

        if ctcae_data is None:
            print("Error: Could not find CTCAE data in the Excel file")
            return False

        # Clean the data
        # Replace any NaN values with empty strings
        ctcae_data = ctcae_data.fillna("")

        # Convert to structured format
        terms = []
        for _, row in ctcae_data.iterrows():
            term = {
                "meddra_code": str(row.get("MedDRA Code", "")),
                "meddra_soc": row.get("MedDRA SOC", ""),
                "ctcae_term": row.get("CTCAE Term", ""),
                "definition": row.get("Definition", ""),
                "navigational_note": row.get("Navigational Note", ""),
                "grades": []
            }

            # Add grade descriptions
            for grade_num in range(1, 6):
                grade_col = f"Grade {grade_num}"
                if grade_col in row and row[grade_col]:
                    term["grades"].append({
                        "grade": str(grade_num),
                        "description": row[grade_col]
                    })

            terms.append(term)

        # Create output structure
        output_data = {
            "version": "5.0",
            "terms": terms,
            "categories": sorted(list(set(t["meddra_soc"] for t in terms if t["meddra_soc"])))
        }

        # Save to JSON file
        os.makedirs(OUTPUT_PATH.parent, exist_ok=True)
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"Processed {len(terms)} CTCAE terms with {len(output_data['categories'])} categories")
        print(f"Output saved to {OUTPUT_PATH}")
        return True
    except Exception as e:
        print(f"Error processing CTCAE data: {e}")
        return False


if __name__ == "__main__":
    success = process_ctcae()
    sys.exit(0 if success else 1)