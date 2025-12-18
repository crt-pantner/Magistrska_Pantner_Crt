import pandas as pd
import sys

path_to_input = sys.argv[1]

clipdf = pd.read_csv(path_to_input)


print(clipdf.columns)

num_orders = clipdf["order"].nunique()
num_families = clipdf["family"].nunique()
num_species = clipdf["Organism Name"].nunique()
num_proteins = clipdf["Protein Id"].nunique()

"""print(f"number of orders: {num_orders}")
print(f"number of families: {num_families}")
print(f"number of species: {num_species}")"""

families_per_order = clipdf.groupby("order")["family"].nunique()
species_per_order = clipdf.groupby("order")["Organism Name"].nunique()
species_per_family = clipdf.groupby("family")["Organism Name"].nunique()



prot_per_order = clipdf.groupby("order")["Protein Id"].nunique()
prot_per_family = clipdf.groupby("family")["Protein Id"].nunique()


# Summary of counts
summary = {
    "Total orders": num_orders,
    "Total Families": num_families,
    "Total Species": num_species,
    "Total Proteins": num_proteins,
    "Families per order": families_per_order,
    "Species per order": species_per_order,
    "Species per family": species_per_family,
    "Protein per order": prot_per_order,
    "Protein per family": prot_per_family
}

with pd.ExcelWriter("summary_counts.xlsx") as writer:
    pd.DataFrame(families_per_order).to_excel(writer, sheet_name="Families per Order")
    pd.DataFrame(species_per_order).to_excel(writer, sheet_name="Species per Order")
    pd.DataFrame(species_per_family).to_excel(writer, sheet_name="Species per Family")
    pd.DataFrame(prot_per_order).to_excel(writer, sheet_name="Proteins per Order")
    pd.DataFrame(prot_per_family).to_excel(writer, sheet_name="Proteins per Family")




print(summary)
