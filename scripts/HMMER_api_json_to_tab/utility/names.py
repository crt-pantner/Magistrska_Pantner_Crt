"""
Po končanju HMMER skripte imamo imena v spremenjeni obliki - vsi presledkti in vsi drugi znaki se prepišejo v podčrtaj. 
Da lahko uvozimo v excel imena bolj enostavno, je to skripta, ki nam izvozi prvotno ime fasta headerjev in jim pripiše končno ime z zamenjavami.
"""
import re

from Bio import SeqIO
import argparse
from pathlib import Path
from Bio.SeqRecord import SeqRecord
import pandas as pd

# postavi argumente za argparse
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-seq",
        required=True,
        type=str,
        help="Path to fasta file with proteins that you have submitted for HMMER server."
    )
    args = parser.parse_args()
    return args

# S pomoočjo argumenta za vhodno datoteko, pretvori v Path
def open_fasta_file(location) -> list[SeqRecord]:
    # Handles opening the fasta file
    input_fasta_file = Path(location).resolve()
    

    seq_records = []

    for seq_record in SeqIO.parse(input_fasta_file, "fasta"):
        seq_records.append(seq_record)
    
    return(seq_records)


# Po tem ko odpreš datoteko naloži v Bio SqIO in poišči fasta headerje

# Za vsak fasta header ga shrani v dict - prvo polje ime, naslednje polje substituirano ime

# Izvozi dict s pomočjo pandas.

def main():
    arguments = get_arguments()
    seq_objects = open_fasta_file(location=arguments.seq)

    names = {}

    for seq_record in seq_objects:
        old_name = str(seq_record.id)
        new_name = old_name.replace("|", "_")
        new_name = re.sub(r'[\\/*?:"<>|]', "_", new_name)
        names.update({old_name: new_name})
    print(names)

    df = pd.DataFrame.from_dict(data=names, orient='index', columns=["new_name"])
    df.index.name = "old_name"
    
    df.to_csv("names_list.csv")


if __name__ == "__main__":
    main()