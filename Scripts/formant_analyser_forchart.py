# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import argparse
import re
from datetime import datetime

def extract_info_from_filename(filename):
    """
    Extract vowel and word from filename pattern like 'o_gauche.txt'
    Returns tuple of (vowel, word)
    """
    # Extract using regex pattern
    match = re.match(r'([a-zA-Z]+)_([a-zA-Z]+)\.txt', filename)
    if match:
        vowel = match.group(1)
        word = match.group(2)
        return vowel, word
    else:
        # If pattern doesn't match, use basic approach
        parts = os.path.splitext(filename)[0].split('_', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return "unknown", "unknown"

def process_formant_file(filepath):
    """
    Process a single formant file and return the F1 and F2 values
    """
    try:
        # Read the file, specifying whitespace as the delimiter
        df = pd.read_csv(filepath, sep='\s+')
        
        # Check if the expected columns are present
        required_columns = ['F1_Hz', 'F2_Hz']
        if not all(col in df.columns for col in required_columns):
            print(f"Warning: File {filepath} does not contain all required columns.")
            print(f"Available columns: {df.columns.tolist()}")
            return None
        
        # Round F1 and F2 values to the nearest integer
        df['F1_Hz'] = df['F1_Hz'].round(0).astype(int)
        df['F2_Hz'] = df['F2_Hz'].round(0).astype(int)
            
        # Extract the first row (or calculate average if multiple rows)
        if len(df) > 1:
            f1_value = int(round(df['F1_Hz'].mean()))
            f2_value = int(round(df['F2_Hz'].mean()))
        else:
            f1_value = df['F1_Hz'].iloc[0]
            f2_value = df['F2_Hz'].iloc[0]
            
        return f1_value, f2_value
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        return None

def create_structured_csv(file_list, output_file):
    """
    Process formant files and create a structured CSV with vowel, F1, F2, word
    """
    # List to store rows for the CSV
    rows = []
    
    # Process each file
    for file_path in file_list:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        # Get filename without path
        filename = os.path.basename(file_path)
        
        # Extract vowel and word from filename
        vowel, word = extract_info_from_filename(filename)
        
        # Process the file to get F1 and F2
        result = process_formant_file(file_path)
        if result is not None:
            f1_value, f2_value = result
            rows.append({
                'Vowel': vowel,
                'F1': f1_value,
                'F2': f2_value,
                'Word': word
            })
    
    # Create DataFrame from rows
    if rows:
        result_df = pd.DataFrame(rows)
        
        # Save to CSV with tab separator
        result_df.to_csv(output_file, sep='\t', index=False)
        print(f"\nStructured formant data saved to {output_file}")
        return True
    else:
        print("No valid data found in the provided files.")
        return False

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Create structured CSV from formant files.')
    parser.add_argument('files', nargs='+', help='List of formant text files to process')
    parser.add_argument('--output', '-o', help='Output CSV file (default: formants_structured_YYYY-MM-DD.csv)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Generate default output filename if not specified
    if not args.output:
        current_date = datetime.now().strftime("%Y-%m-%d")
        args.output = f"formants_structured_{current_date}.csv"
    
    # Create structured CSV
    create_structured_csv(args.files, args.output)

if __name__ == "__main__":
    main()