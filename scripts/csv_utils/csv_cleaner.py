import argparse

import pandas as pd

"""
Script that cleans and reformats metadata from csv
input:

BUG: Nekatera imena so v stolpcu Organism Name napisana drugače - npr Ceriporiopsis (Gelatoporia) subvermispora B.
    Logika skripte je takšna, da Organism Name razdeli na presledke, tako dobimo npr iz Flavodon flavus 38 v1.0  --> Flavodon flavus
    Ker pa je pri nekaterih ime v oklepaju ali je drugače ime "unikatno" za te organizme ne bo delovalo. V naslednjem koraku ohranjevanja samo macpf/aegerolizin vsbujočih proteinov nujno preglej ujemanje.ssssssssssssssssssss
"""

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

# Get arguments
args = parser.parse_args()

# Get input file path from arguments
csv_file_path = args.infile

# Create data frame from the given csv metadata file
df = pd.read_csv(csv_file_path)

# Concatenate the specific parameters to recreate FASTA header as it appears in protein FASTA file.
df["fasta_header"] = (
    "jgi|" + df["Organism Id"] + "|" + df["Protein Id"].astype(str) + "|" + df["Name"]
)

# Reposition fasta header
fasta_headers = df.pop("fasta_header")
df.insert(1, "fasta_header", fasta_headers)

# Extract genus and species name from Organism name
df[["Genus", "Species", "Others"]] = df["Organism Name"].str.split(
    " ", n=2, expand=True
)
df.pop("Others")
df["Genus species"] = df["Genus"] + " " + df["Species"]

# Clean up the data
df.pop("Genus")
df.pop("Species")

# Reposition genus+species name.
genus_species = df.pop("Genus species")
df.insert(4, "Genus species", genus_species)

# Export to file.
df.to_csv(args.outfile, sep=",", index=False)
