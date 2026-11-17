import copy
import json
import re
import string
import sys

from Bio import SeqIO


class InvalidNameError(Exception):
    "Raised when the name of the sequence contains invalid characters"


def main():

    jobs = []

    input_file = sys.argv[1]

    job_number = 0

    for seq_record in SeqIO.parse(input_file, "fasta"):
        new_seq_record = rename_sequence_record(seq_record)
        jobs.append(job_creator(new_seq_record))

        if len(jobs) == 20:
            job_number += 1
            write_to_file(jobs, job_number)
            jobs.clear()
    # Write any remaining jobs that didn't fill a full batch of 20
    if jobs:
        job_number += 1
        write_to_file(jobs, job_number)
    

    
def rename_sequence_record(seq_rec):
    original_seq_record = copy.deepcopy(seq_rec)
    sequence = seq_rec.seq

    seq_rec.seq = sequence.rstrip("*")

    cleaned_name = re.sub(r'[^a-zA-Z0-9 _:\-]', '_', seq_rec.id)

    cleaned_name = cleaned_name.lower()

    seq_rec.id = re.sub(r'_+', '_', cleaned_name)
    
    new_seq_rec = copy.deepcopy(seq_rec)

    check_sequence_name(original_seq_record, new_seq_rec)

    save_name_mapping(old_name=original_seq_record.id, new_name=new_seq_rec.id)

    return seq_rec


def check_sequence_name(original_seq_rec, new_seq_rec):
    try:
        allowed_characters = set(string.ascii_letters + string.digits + "_-: ")
        if not set(new_seq_rec.id) <= allowed_characters:
            raise InvalidNameError
    
    except InvalidNameError:
            with open("non-ran-jobs.txt", "a") as file:
                print("The sequence name contains invalid characters, skipping sequence and writing name to file")
                file.writelines(str(original_seq_rec.id) + "\n")

def save_name_mapping(old_name, new_name):
    with open("sequence_name_mapping.csv", "a") as outfile:
        outfile.write(f"{old_name},fold_{new_name}_model_0\n")
    
def job_creator(seq_record):
    job = {
            "name": seq_record.id,
            "modelSeeds": [],
            "sequences": [
            {
                "proteinChain": {
                "sequence": str(seq_record.seq),
                "count": 1,
                }
            },
            ],
            "dialect": "alphafoldserver",
            "version": 1
        }
    return job

def write_to_file(jobs, job_number):
    with open(f"job_{job_number}.json", "w") as file:
        print(job_number)
        json.dump(jobs, file, indent=4)



if __name__ == "__main__":
    main()