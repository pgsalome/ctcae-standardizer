#!/usr/bin/env python3
"""
Process the CTCAE Excel file and extract structured data.
Modified version with more flexible column detection.
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
        # Read Excel file
        xl = pd.ExcelFile(CTCAE_PATH)

        # Print sheet names for debugging
        print(f"Found {len(xl.sheet_names)} sheets in the Excel file:")
        for sheet_name in xl.sheet_names:
            print(f"  - {sheet_name}")

        # Try each sheet to find CTCAE data
        ctcae_data = None

        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)

            # Print column names for debugging
            print(f"\nColumns in sheet '{sheet_name}':")
            for col in df.columns:
                print(f"  - {col}")

            # Check for CTCAE-related content in the columns
            # Look for columns that might contain grade information and CTCAE terms
            grade_columns = [col for col in df.columns if 'grade' in str(col).lower()]
            term_columns = [col for col in df.columns if 'term' in str(col).lower() or 'ctcae' in str(col).lower()]

            if len(grade_columns) >= 2 and len(term_columns) >= 1:
                print(f"\nFound potential CTCAE data in sheet '{sheet_name}'")
                print(f"  Term columns: {term_columns}")
                print(f"  Grade columns: {grade_columns}")

                ctcae_data = df
                break

        if ctcae_data is None:
            # Try a more flexible approach - look for any sheet with a column structure like we need
            for sheet_name in xl.sheet_names:
                df = xl.parse(sheet_name)

                # If we have 5+ columns, it might be our data
                if len(df.columns) >= 5:
                    # Check if any columns might be grade columns (numbers 1-5 in them)
                    potential_grade_cols = 0
                    for col in df.columns:
                        col_str = str(col).lower()
                        if any(f"grade {i}" in col_str or f"grade{i}" in col_str for i in range(1, 6)):
                            potential_grade_cols += 1

                    if potential_grade_cols >= 3:  # If we have at least 3 grade columns
                        print(f"\nFound potential CTCAE data in sheet '{sheet_name}' based on column structure")
                        ctcae_data = df
                        break

        if ctcae_data is None:
            # Let's try a full text search approach
            for sheet_name in xl.sheet_names:
                df = xl.parse(sheet_name)

                # Convert entire dataframe to string to check content
                df_str = df.to_string().lower()
                if 'ctcae' in df_str and 'grade' in df_str and 'term' in df_str:
                    print(f"\nFound potential CTCAE data in sheet '{sheet_name}' based on content search")
                    ctcae_data = df
                    break

        if ctcae_data is None:
            print("Error: Could not find CTCAE data in the Excel file")
            print("Please examine the Excel file structure manually and update the script accordingly.")
            return False

        # Map expected column names to actual column names
        column_mapping = {}

        # Find MedDRA SOC column
        soc_candidates = [col for col in ctcae_data.columns if
                          'soc' in str(col).lower() or 'system organ class' in str(col).lower()]
        if soc_candidates:
            column_mapping['MedDRA SOC'] = soc_candidates[0]
        else:
            # Try to guess based on content
            for col in ctcae_data.columns:
                sample_values = ctcae_data[col].dropna().astype(str).tolist()[:10]
                if sample_values and any('system' in val.lower() for val in sample_values):
                    column_mapping['MedDRA SOC'] = col
                    break

        # Find MedDRA Code column
        code_candidates = [col for col in ctcae_data.columns if
                           'code' in str(col).lower() or 'meddra' in str(col).lower()]
        if code_candidates:
            column_mapping['MedDRA Code'] = code_candidates[0]

        # Find CTCAE Term column
        term_candidates = [col for col in ctcae_data.columns if 'term' in str(col).lower()]
        if term_candidates:
            column_mapping['CTCAE Term'] = term_candidates[0]
        else:
            # If no explicit term column, try to find a column that might contain term names
            for col in ctcae_data.columns:
                if col not in column_mapping.values():  # Don't reuse columns
                    sample_values = ctcae_data[col].dropna().astype(str).tolist()[:10]
                    if sample_values and all(len(val) > 3 and ' ' in val for val in sample_values):
                        column_mapping['CTCAE Term'] = col
                        break

        # Find Definition column
        def_candidates = [col for col in ctcae_data.columns if 'def' in str(col).lower()]
        if def_candidates:
            column_mapping['Definition'] = def_candidates[0]

        # Find Grade columns
        for grade_num in range(1, 6):
            grade_candidates = [col for col in ctcae_data.columns
                                if f'grade {grade_num}' in str(col).lower() or f'grade{grade_num}' in str(col).lower()]
            if grade_candidates:
                column_mapping[f'Grade {grade_num}'] = grade_candidates[0]

        print("\nMapped columns:")
        for expected_col, actual_col in column_mapping.items():
            print(f"  {expected_col} -> {actual_col}")

        # Check if we have the minimum required columns
        required_cols = ['CTCAE Term', 'Grade 1', 'Grade 2', 'Grade 3']
        missing_cols = [col for col in required_cols if col not in column_mapping]

        if missing_cols:
            print(f"Error: Could not identify these required columns: {missing_cols}")
            print("Please examine the Excel file structure and update the script accordingly.")
            return False

        # Process the data with the mapped columns
        terms = []
        for _, row in ctcae_data.iterrows():
            term = {
                "meddra_code": str(row.get(column_mapping.get('MedDRA Code', ''), "")),
                "meddra_soc": row.get(column_mapping.get('MedDRA SOC', ''), ""),
                "ctcae_term": row.get(column_mapping.get('CTCAE Term', ''), ""),
                "definition": row.get(column_mapping.get('Definition', ''), ""),
                "navigational_note": row.get(column_mapping.get('Navigational Note', ''), ""),
                "grades": []
            }

            # Skip rows with empty CTCAE term
            if not term["ctcae_term"]:
                continue

            # Add grade descriptions
            for grade_num in range(1, 6):
                grade_col = f'Grade {grade_num}'
                if grade_col in column_mapping and column_mapping[grade_col] in row:
                    grade_desc = row[column_mapping[grade_col]]
                    if pd.notna(grade_desc) and grade_desc:
                        term["grades"].append({
                            "grade": str(grade_num),
                            "description": str(grade_desc)
                        })

            # Only add terms that have at least one grade
            if term["grades"]:
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
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = process_ctcae()
    sys.exit(0 if success else 1)