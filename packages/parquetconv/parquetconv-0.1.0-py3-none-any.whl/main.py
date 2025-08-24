import argparse
import os
import sys
import pandas as pd
from pathlib import Path


def detect_file_format(file_path):
    """Detect if a file is Parquet or CSV based on extension and content."""
    file_path = Path(file_path)
    
    # Check file extension first
    if file_path.suffix.lower() == '.parquet':
        return 'parquet'
    elif file_path.suffix.lower() == '.csv':
        return 'csv'
    
    # Try to detect by attempting to read the file
    try:
        # Try to read as Parquet first
        pd.read_parquet(file_path, nrows=1)
        return 'parquet'
    except Exception:
        try:
            # Try to read as CSV
            pd.read_csv(file_path, nrows=1)
            return 'csv'
        except Exception:
            return None


def convert_parquet_to_csv(input_file, output_file=None):
    """Convert Parquet file to CSV."""
    try:
        df = pd.read_parquet(input_file)
        if output_file is None:
            output_file = str(Path(input_file).with_suffix('.csv'))
        
        df.to_csv(output_file, index=False)
        print(f"Successfully converted {input_file} to {output_file}")
        print(f"DataFrame shape: {df.shape}")
        return True
    except Exception as e:
        print(f"Error converting Parquet to CSV: {e}")
        return False


def convert_csv_to_parquet(input_file, output_file=None):
    """Convert CSV file to Parquet."""
    try:
        df = pd.read_csv(input_file)
        if output_file is None:
            output_file = str(Path(input_file).with_suffix('.parquet'))
        
        df.to_parquet(output_file, index=False)
        print(f"Successfully converted {input_file} to {output_file}")
        print(f"DataFrame shape: {df.shape}")
        return True
    except Exception as e:
        print(f"Error converting CSV to Parquet: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convert between Parquet and CSV file formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py input.parquet          # Convert Parquet to CSV
  python main.py input.csv              # Convert CSV to Parquet
  python main.py input.parquet -o output.csv    # Specify output file
  python main.py input.csv -o output.parquet    # Specify output file
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input file to convert (Parquet or CSV)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (optional, will auto-generate if not specified)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force conversion even if file format detection is uncertain'
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Detect file format
    file_format = detect_file_format(args.input_file)
    
    if file_format is None:
        print(f"Error: Could not determine file format for '{args.input_file}'")
        print("Please ensure the file is either a valid Parquet or CSV file.")
        if not args.force:
            sys.exit(1)
        else:
            print("Proceeding with force flag...")
            # Try to guess based on extension
            if args.input_file.lower().endswith('.parquet'):
                file_format = 'parquet'
            elif args.input_file.lower().endswith('.csv'):
                file_format = 'csv'
            else:
                print("Cannot determine format even with force flag.")
                sys.exit(1)
    
    # Perform conversion
    success = False
    if file_format == 'parquet':
        print(f"Detected Parquet file: {args.input_file}")
        success = convert_parquet_to_csv(args.input_file, args.output)
    elif file_format == 'csv':
        print(f"Detected CSV file: {args.input_file}")
        success = convert_csv_to_parquet(args.input_file, args.output)
    
    if success:
        print("Conversion completed successfully!")
    else:
        print("Conversion failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
