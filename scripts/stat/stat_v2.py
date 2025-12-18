import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
import argparse

"""
TODO: naredi tako da je statistika narejena število genomov na rod in število vrst na rod. 
Preveri ali je gledanje glede na protein id okej - pomoje je bolje če gledaš na celoten fasta header.
"""

parser = argparse.ArgumentParser(
    prog="Stat.py",
    description="this script takes in a csv table for proteins and phylogeny table and calculates the statistics for select clades",
)

parser.add_argument("-m", "--metadata", required=True, help="Path to the input protein CSV file containing metadata.")
parser.add_argument("-p",
    "--phylogen",
    required=True,
    help="Path to the entire within some clade, eg. Basidiomycota. Used to calculate the statistics of organisms that contain studied protein vs all within the clade.",
)
parser.add_argument("-o", "--output", required=True, help="Path to output file containing statistics.")
args = parser.parse_args()

path_to_input = args.metadata

path_to_entire_phylogeny = args.phylogen

clipdf = pd.read_csv(path_to_input)


phylogeny_df = pd.read_csv(path_to_entire_phylogeny)
phylogeny_df = phylogeny_df.rename({"input_species": "Organism Name"}, axis="columns")


merged_df = clipdf.merge(phylogeny_df, how="inner")

(merged_df.to_clipboard())

"""Statistika za tiste ki imajo protein."""
num_orders = merged_df["order"].nunique()  # V katerih vseh redovih se pojavlja
num_families = merged_df["family"].nunique()
num_genome = merged_df["Organism Name"].nunique()
num_proteins = merged_df["Protein Id"].nunique()
proportion_per_genome = num_proteins / num_genome  # Delež proteinov na genom.

print(f"number of orders: {num_orders}")
print(f"number of families: {num_families}")
print(f"number of genomes: {num_genome}")


families_per_order = merged_df.groupby("order")["family"].nunique()
genomes_per_order = merged_df.groupby("order")["Organism Name"].nunique()
genomes_per_family = merged_df.groupby("family")["Organism Name"].nunique()


prot_per_order = merged_df.groupby("order")["Protein Id"].nunique()
prot_per_family = merged_df.groupby("family")["Protein Id"].nunique()

print(prot_per_order)


# Summary of counts
summary = {
    "Total orders": num_orders,
    "Total Families": num_families,
    "Total Genomes": num_genome,
    "Total Proteins": num_proteins,
    "Families per order": families_per_order,
    "genomes per order": genomes_per_order,
    "genomes per family": genomes_per_family,
    "Protein per order": prot_per_order,
    "Protein per family": prot_per_family,
}

print(f"Number of genomes: {phylogeny_df['Organism Name'].nunique()}")
print(f"NUmber of macpf containing genomes: {clipdf['Organism Name'].nunique()}")

""" Izračun deleža genomov s proteinom po posameznem redu"""
num_genomes_per_order = phylogeny_df.groupby("order")["Organism Name"].nunique()
genomes_with_protein_per_order = merged_df.groupby("order")["Organism Name"].nunique()

percentage_summary_df = pd.DataFrame(
    {
        "TotalGenomes": num_genomes_per_order,
        "GenomesWithProtein": genomes_with_protein_per_order,
    }
)
percentage_summary_df["Percentage"] = (
    percentage_summary_df["GenomesWithProtein"] / percentage_summary_df["TotalGenomes"]
) * 100
percentage_summary_df["GenomesWithProtein"] = (
    percentage_summary_df["GenomesWithProtein"].fillna(0).astype(int)
)

percentage_summary_df = percentage_summary_df.sort_values(
    by="Percentage", ascending=False
)

with pd.ExcelWriter(args.output) as writer:
    pd.DataFrame(families_per_order).to_excel(writer, sheet_name="Families per Order")
    pd.DataFrame(genomes_per_order).to_excel(writer, sheet_name="genomes per Order")
    pd.DataFrame(genomes_per_family).to_excel(writer, sheet_name="genomes per Family")
    pd.DataFrame(prot_per_order).to_excel(writer, sheet_name="Proteins per Order")
    pd.DataFrame(prot_per_family).to_excel(writer, sheet_name="Proteins per Family")
    percentage_summary_df.to_excel(writer, sheet_name="Percentage per Order")

## TO-DO:
"""
TODO: Hi kvadrat statitstika za primerjanje ali je nek red enriched oz. obogaten s proteini ali je to samo posledica naključja.
"""

print(summary)
