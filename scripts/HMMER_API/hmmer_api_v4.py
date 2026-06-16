import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse

import requests
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from tqdm import tqdm


class PendingError(Exception):
    pass


def get_arguments():
    # Handles command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-seq",
        required=True,
        type=str,
        help="Path to fasta file with proteins for HMMER server.",
    )
    args = parser.parse_args()
    return args


def open_fasta_file(location) -> list[SeqRecord]:
    # Handles opening the fasta file
    input_fasta_file = Path(location).resolve()

    seq_records = []

    for seq_record in SeqIO.parse(input_fasta_file, "fasta"):
        seq_records.append(seq_record)

    return seq_records


def export_hmmer_data(json_data, org_name):
    current_dir = Path.cwd()

    save_dir = current_dir / "hmmer_results"

    save_dir.mkdir(exist_ok=True)

    output_file = save_dir / f"{org_name}_hmmerrez.json"

    with open(output_file, "w", encoding="utf-8") as hmmrez_file:
        json.dump(json_data.json(), hmmrez_file)

    return output_file


def status_checker(result_data):
    if result_data["status"] == "PENDING":
        raise PendingError("Results are pending, retrying")
    elif result_data["status"] == "STARTED":
        raise PendingError("Results are started, retrying")


def get_hmmer_data(sequence):
    # API endpoint
    url = "https://www.ebi.ac.uk/Tools/hmmer/api/v1/search/hmmscan"

    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "input": str(sequence.seq),
        "database": "pfam",
        "domE": 1,
        "domT": 5,
        "E": 1,
        "incdomE": 0.03,
        "incdomT": 22,
        "incE": 0.01,
        "incT": 25,
        "threshold": "cut_ga",
    }

    # Submit a sequence
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        uuid = result["id"]

        if uuid:
            # Fetch results
            result_url = f"https://www.ebi.ac.uk/Tools/hmmer/api/v1/result/{uuid}"
            webpage_url = f"https://www.ebi.ac.uk/Tools/hmmer/results/{uuid}/score"

            while True:
                try:
                    result_response = requests.get(result_url)

                    if result_response.status_code == 200:
                        status_checker(result_response.json())

                        export_hmmer_data(result_response, org_name=sequence.id)

                        return webpage_url
                except PendingError as e:
                    print(e)
                    time.sleep(5)
                else:
                    print(f"Failed to retrieve results {result_response.status_code}")
                    time.sleep(5)
        else:
            print("UUID not found in response")
            print(result)
    else:
        print(f"Error submiting request: Error {response.status_code}")


def countdown(seconds):
    """Prints a countdown timer on a single line."""
    for i in range(seconds, 0, -1):
        # The \r moves the cursor to the start.
        # The space at the end clears any leftover characters from the previous line.
        message = f"\rWaiting {i} seconds before retrying... "
        sys.stdout.write(message)
        sys.stdout.flush()
        time.sleep(1)

    # Print a final message to overwrite the countdown
    sys.stdout.write("\rRetrying now...                      \n")
    sys.stdout.flush()


def main():
    arguments = get_arguments()
    # Open the fasta file with sequences and return list of BioSeqio objects
    seq_objects = open_fasta_file(location=arguments.seq)

    done_proteins = []

    cwd = Path.cwd()
    proteins_path = cwd / "proteins.txt"

    if proteins_path.exists():
        print("Discovered already completed proteins:")
        with open(proteins_path, "r") as file:
            for line in file:
                stripped = line.strip("\n")
                done_proteins.append(stripped)

    # Parse the fasta file with sequences and return protein objects
    for sequence in tqdm(seq_objects):
        try:
            if sequence.id not in done_proteins:
                # Submit request to HMMER API, save the hmmer results, get back webpage url for scraping
                get_hmmer_data(sequence)
                with open("proteins.txt", "a") as file:
                    print(f"Writing protein {sequence.id}.")
                    file.write(f"{sequence.id}\n")
            else:
                print(f"Protein {sequence.id} results already present, skipping.")
                pass
        except Exception as e:
            print(f"Error: {e}")
            with open("Not_done_proteins.txt", "a") as file:
                file.write(f"{sequence.id}\n")


            


if __name__ == "__main__":
    main()

    """cwd = Path.cwd()
    proteins_path = cwd / "proteins.txt"

    if proteins_path.exists():
        with open("proteins.txt", "r") as file:
            for line in file:
                line = line.strip("\n")
                sanitized_id = line.strip().split(",")[0]
                done_proteins.append(re.sub(r'[\\/*?:"<>|]', "_", sanitized_id))
    else:
        with open(proteins_path, "w") as file:
            file.write("sanitized_ID,original id\n")

    if len(done_proteins) != 0:
        print("Discovered already completed proteins:")
        for protein in done_proteins:
            print(protein)"""
