from Bio import SeqIO
import pandas as pd
import numpy as np
import statistics as st

def get_sequences(input_fasta_file):
    seq_records = []

    for seq_record in SeqIO.parse(input_fasta_file, "fasta"):
        seq_records.append(seq_record)
    
    return(seq_records)

def log_saver(line):
    with open("removed_sequences_log.txt", "a", newline="\n") as outfile:
        outfile.write(f"{line}\n")

def main():
    for_pandas = {}
    records = get_sequences(input("Path to fasta file: "))
    for entry in records:
        
        id = entry.id
        sequence = entry.seq
        lenght = len(sequence)
        dictionary = {id:[lenght]}

        for_pandas.update(dictionary)
    
    df = pd.DataFrame.from_dict(for_pandas, orient="index", columns=["lenght"])


    mode = st.mode(df.lenght)
    
    print(f"Mode = {mode}.")
    removal_window = float(input("Pick percentage of mode you want to remove. Type it in as a decimal. "))

    upper_limit = mode + mode*removal_window
    lower_limit = mode - mode*removal_window
    


    kept_records = []
    removed_records = 0
    for record in records:
        
        
        if upper_limit > int(len(record.seq)) > lower_limit:
            kept_records.append(record)
        else:
            removed_records += 1
            print(f"Removed protein: {record.id}, lenght of protein: {len(record.seq)}")
            log_saver(f"Removed protein: {record.id}, lenght of protein: {len(record.seq)}")
    
    
    print(f"Mode: {mode}")
    log_saver(f"Mode: {mode}")
    print(f"Upper limit: {upper_limit}")
    log_saver(f"Upper limit: {upper_limit}")
    print(f"Lower limit: {lower_limit}")
    log_saver(f"Lower limit: {lower_limit}")

    print(f"Number of removed records: {removed_records}")
    log_saver(f"Number of removed records: {removed_records}")

    print(f"Number of records kept: {len(kept_records)}")
    log_saver(f"Number of records kept: {len(kept_records)}")

    SeqIO.write(kept_records, "kept_sequences.fasta", "fasta")
    

    

if __name__ == "__main__":
    main()