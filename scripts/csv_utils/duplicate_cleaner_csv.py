import pandas as pd
import argparse
import sys

""" Helper script that removes duplicate sequences based on the name from a metadata csv file."""
# Argument parsing
parser = argparse.ArgumentParser(
    prog="csv_cleaner", description="Cleans and reformats csv metadata from JGI"
)

parser.add_argument(
    "-i", "--infile", help="Input CSV file", required=True, dest="infile"
)  # Store the value in args.infile

parser.add_argument(
    "-o", "--outfile", help="Output CSV file", required=True, dest="outfile"
)  # Store the value in args.outfile

args = parser.parse_args()

metadata_file_path = args.infile

df = pd.read_csv(metadata_file_path)

df = df.drop_duplicates("fasta_header")

output_path = metadata_file_path.rstrip(".csv") + "_no_duplicates_by_name.csv"

df.to_csv(args.outfile, index=False)
