import pandas as pd

# Utility script, zaradi načina shranjevanja se mi pretvorijo hmmer rezultati iz pipe znaka v podčrtaj, ta skripta poskrbi, da se pretvorijo nazaj.

# Preberi seznam imen z fasta headerji ter pretvorjenimi imeni (iz names.py)
df = pd.read_csv("names_list.csv", sep=",", header=0)

# Preberi datoteki za aegerolizine in macpf
macps_df = pd.read_csv("macpf_containing_proteins.csv", sep=",", names=["new_name"])
aegerolysin_df = pd.read_csv("aegerolysin_containing_proteins.csv", sep=",", names=["new_name"])

# Združi oba seznama glede na "new_name" in shrani samo tiste, ki so enaki med obema seznamoma. S tem se znebimo tistih, ki nimajo macpf domene
merged_macpf_df = df.merge(macps_df, on="new_name", how="inner")

# Exportaj v csv datoteko, ki jo lahko nato uporabimo za seqkit.
merged_macpf_df.to_csv("macpf_containing_protein_headers.csv", sep=",", header=False, columns=["old_name"], index=False)

# Enako stori še za aegerolizine.
merged_aegerolysin_df = df.merge(aegerolysin_df, on="new_name", how="inner")

merged_aegerolysin_df.to_csv("aegerolyisin_containing_protein_headers.csv", sep=",", header=False, columns=["old_name"], index=False)