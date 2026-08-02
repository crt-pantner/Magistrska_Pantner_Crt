from Bio.SeqUtils.ProtParam import ProteinAnalysis
from Bio import SeqIO
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import peptides




input_file = sys.argv[1]

seqdata = []

for record in SeqIO.parse(input_file, "fasta"):

        record.seq = record.seq.rstrip("*")
        if "X" in record.seq:
            with open("not_imported.txt", "w") as outfile:
                outfile.write(f"Not imported, contains X - ambiguous amino acids, ID: {record.id}")
            pass
        else:
            seqdata.append(record)
        

        



seqdata_dict = []

for protein in seqdata:
    seqdata_dict.append({"ID":protein.id, "sequence":protein.seq})


for_pandas = {}

for protein in seqdata_dict:
    
    sequence_str = str(protein["sequence"])
    prot_param_obj = ProteinAnalysis(sequence_str)
    peptide_obj = peptides.Peptide(sequence_str)
    
    cisteines = prot_param_obj.count_amino_acids()["C"]
    aromaticity = prot_param_obj.aromaticity()
    molecular_weight = prot_param_obj.molecular_weight()
    instability_index = prot_param_obj.instability_index()
    isoelectric_point = prot_param_obj.isoelectric_point()
    gravy = prot_param_obj.gravy()
    charge = prot_param_obj.charge_at_pH(pH=7)
    aliphatic_index = peptide_obj.aliphatic_index()
    for_pandas.update({protein["ID"]:[cisteines, aromaticity, molecular_weight, instability_index, isoelectric_point, gravy, charge, aliphatic_index]})



data_frame = pd.DataFrame.from_dict(for_pandas, orient='index', columns=["cisteines", "aromaticity", "molecular_weight", "instability_index", "isoelectric_point", "gravy", "charge", "aliphatic_index"])

data_frame = data_frame.apply(pd.to_numeric, errors="coerce")

average_row = data_frame.mean(numeric_only=True).round(2)
median_row = data_frame.median(numeric_only=True).round(2)

average_data_frame = data_frame.copy()
average_data_frame.loc["Average"] = average_row
average_data_frame.loc["median"] = median_row



if input("Save to csv? ([Y / N]) ").strip().lower() == "y":
    average_data_frame.round(2)
    average_data_frame.to_excel("values.xlsx", index=True)

sns.set_theme(style="darkgrid")
sns.set_style("ticks")
sns.set_style()






fig, axs = plt.subplots(2, 4, figsize=(10,10))
    



cisteines = sns.histplot(data=data_frame, color="#1F363D",  x="cisteines", ax=axs[0, 0], discrete=True, kde=True)
cisteines.axvline(x=data_frame["cisteines"].mean())
cisteines.axvline(x=data_frame["cisteines"].median(),color="#ff8811")
cisteines.set_xlabel("Cysteine count")

aromaticity = sns.histplot(data=data_frame, color="#1F363D",  x="aromaticity", ax=axs[0, 1], kde=True)
aromaticity.axvline(x=data_frame["aromaticity"].mean())
aromaticity.axvline(x=data_frame["aromaticity"].median(), color="#ff8811")
aromaticity.set_xlabel("Aromaticity index")

mw = sns.histplot(data=data_frame, color="#ff8811", x="molecular_weight", ax=axs[0, 2], kde=True)
mw.set_xlabel("Molecular weight")
mw.axvline(x=data_frame["molecular_weight"].mean())
mw.axvline(x=data_frame["molecular_weight"].median(),color="#ff8811")

instab = sns.histplot(data=data_frame, color="#9AD1D4", x="instability_index", ax=axs[0, 3], kde=True)
instab.set_xlabel("Instability index")
instab.axvline(x=data_frame["instability_index"].mean())
instab.axvline(x=data_frame["instability_index"].median(),color="#ff8811")

isoel = sns.histplot(data=data_frame, color="#62c370", x="isoelectric_point", ax=axs[1, 0], kde=True)
isoel.set_xlabel("Isoelectric point")
isoel.axvline(x=data_frame["isoelectric_point"].mean())
isoel.axvline(x=data_frame["isoelectric_point"].median(),color="#ff8811")

gravy = sns.histplot(data=data_frame, color="#CC3363", x="gravy", ax=axs[1, 1], kde=True)
gravy.axvline(x=data_frame["gravy"].mean())
gravy.axvline(x=data_frame["gravy"].median(),color="#ff8811")
gravy.set_xlabel("Gravy")

naboj =sns.histplot(data=data_frame, color="#A62639", x="charge", ax=axs[1, 2], kde=True)
naboj.axvline(x=data_frame["charge"].mean())
naboj.axvline(x=data_frame["charge"].median(),color="#ff8811")
naboj.set_xlabel("Charge")

alifat = sns.histplot(data=data_frame, color="#1F363D",  x="aliphatic_index", ax=axs[1, 3], kde=True)
alifat.axvline(x=data_frame["aliphatic_index"].mean())
alifat.axvline(x=data_frame["aliphatic_index"].median(),color="#ff8811")
alifat.set_xlabel("Aliphatic index")





#plt.show()
plt.savefig(sys.argv[2], dpi=300    )
