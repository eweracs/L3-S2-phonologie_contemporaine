# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import argparse
from datetime import datetime

def process_formant_file(filepath):
    """
    Process a single formant file and return the data as a pandas DataFrame
    """
    try:
        # Read the file, specifying whitespace as the delimiter
        df = pd.read_csv(filepath, sep='\s+')
        
        # Check if the expected columns are present
        required_columns = ['F1_Hz', 'F2_Hz', 'F3_Hz', 'F4_Hz']
        if not all(col in df.columns for col in required_columns):
            print(f"Warning: File {filepath} does not contain all required columns.")
            print(f"Available columns: {df.columns.tolist()}")
            return None
        
        # Round all formant values to the nearest integer
        for col in required_columns:
            df[col] = df[col].round(0).astype(int)
            
        return df
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        return None

def process_all_formants(file_list):
    """
    Process multiple formant files and combine all values into one DataFrame
    """
    # List to store all dataframes
    all_data = []
    
    # Process each file
    for file_path in file_list:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        df = process_formant_file(file_path)
        
        if df is not None:
            # Add filename column to track source
            df['Source_File'] = os.path.basename(file_path)
            all_data.append(df)
    
    # Combine all dataframes
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Calculate averages (already using rounded values)
        avg_f1 = int(round(combined_df['F1_Hz'].mean()))
        avg_f2 = int(round(combined_df['F2_Hz'].mean()))
        avg_f3 = int(round(combined_df['F3_Hz'].mean()))
        avg_f4 = int(round(combined_df['F4_Hz'].mean()))
        
        averages = {
            'F1_Hz': avg_f1,
            'F2_Hz': avg_f2,
            'F3_Hz': avg_f3,
            'F4_Hz': avg_f4
        }
        
        return combined_df, averages
    else:
        return None, None

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Calculate formant values from multiple text files.')
    parser.add_argument('files', nargs='+', help='List of formant text files to process')
    parser.add_argument('--output', '-o', help='Output CSV file for results (default: formant_values_YYYY-MM-DD.csv)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Process all formants
    combined_data, averages = process_all_formants(args.files)
    
    if combined_data is not None:
        # Generate default output filename if not specified
        if not args.output:
            current_date = datetime.now().strftime("%Y-%m-%d")
            args.output = f"formant_values_{current_date}.csv"
        
        # Save all values to CSV
        combined_data.to_csv(args.output, index=False)
        print(f"\nAll formant values saved to {args.output}")
        
        # Display average values
        print("\nAverage Formant Values:")
        print(f"F1: {averages['F1_Hz']} Hz")
        print(f"F2: {averages['F2_Hz']} Hz")
        print(f"F3: {averages['F3_Hz']} Hz")
        print(f"F4: {averages['F4_Hz']} Hz")
        
        # Save average values to a separate file
        avg_file = args.output.replace('.csv', '_averages.csv')
        with open(avg_file, 'w') as f:
            f.write("Formant,Average (Hz)\n")
            for formant, value in averages.items():
                f.write(f"{formant},{value}\n")
        print(f"\nAverage values saved to {avg_file}")
    else:
        print("No valid data found in the provided files.")

if __name__ == "__main__":
    main()