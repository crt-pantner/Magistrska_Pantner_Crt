from Bio import Entrez
import time
from urllib.error import HTTPError
import pandas as pd
import os  # Uvozimo 'os' za preverjanje obstoja datoteke
import sys
import argparse

"""
Verzija V6:
- Skripta preveri, ali izhodna datoteka že obstaja.
- Če obstaja, prebere že obdelane organizme in nadaljuje tam, kjer je končala.
- Uporablja blok try...finally, da shrani napredek tudi v primeru prekinitve (npr. Ctrl+C).
- Izpis napredka je izboljšan.

## TO-DO: Specificiranje, ali že imaš kje datoteko s prenešeno filogenijo.
"""


def main():
        # Get arguments
    args = get_arguments()
    
    output_filename = args.outfile

    # === 1. KORAK: Preverimo obstoječo datoteko in naložimo že obdelane organizme ===
    processed_organisms = set()
    existing_df = pd.DataFrame()

    if os.path.exists(output_filename):
        print(
            f"Najdena je bila obstoječa datoteka '{output_filename}'. Poskušam nadaljevati z delom."
        )
        try:
            # Naložimo obstoječe podatke
            existing_df = pd.read_csv(output_filename)
            # Ustvarimo množico (set) že obdelanih vrst za hitro preverjanje
            if "input_species" in existing_df.columns:
                processed_organisms = set(existing_df["input_species"])
                print(
                    f"V datoteki je že {len(processed_organisms)} obdelanih organizmov."
                )
            else:
                print(
                    "OPOZORILO: V obstoječi datoteki manjka stolpec 'input_species'. Skripta bo morda začela znova."
                )
        except pd.errors.EmptyDataError:
            print("Obstoječa datoteka je prazna. Začenjam znova.")

    # === 2. KORAK: Preberemo vse organizme iz vhodne datoteke in jih filtriramo ===
    all_organisms = get_file(args.infile)

    # Izločimo tiste, ki so že bili obdelani
    # .strip() odstrani morebitne presledke in nove vrstice
    organisms_to_process = [
        org.strip() for org in all_organisms if org.strip() not in processed_organisms
    ]

    if not organisms_to_process:
        print("Vsi organizmi so že obdelani. Zaključujem.")
        return

    print(
        f"Skupaj organizmov: {len(all_organisms)}. Preostalo za obdelavo: {len(organisms_to_process)}."
    )

    newly_fetched_data = []  # Seznam za shranjevanje NOVO pridobljenih podatkov

    # === 3. KORAK: Glavna zanka z zanesljivim shranjevanjem ===
    try:
        total_to_process = len(organisms_to_process)
        for i, organism in enumerate(organisms_to_process, 1):
            # Preskočimo prazne vrstice
            if not organism:
                continue

            print(f"Obdelujem {i}/{total_to_process}: '{organism}'...")

            try:
                phylogeny_data = getdata(organism)
                if phylogeny_data:  # Če so podatki uspešno pridobljeni
                    names = extractnames(phylogeny_data)
                    names.update({"input_species": organism})

                    original_species = " ".join(organism.split(" ")[0:2])

                    if names.get("species") != original_species:
                        names.update({"names_match": "No"})
                    else:
                        names.update({"names_match": "Yes"})

                    newly_fetched_data.append(names)

            except RuntimeError:
                print(
                    f"  -> Ni mogoče najti taksonomije za '{organism}'. Poskušam z rodom..."
                )
                try:
                    genus = organism.split()[0]
                    phylogeny_data = getdata(genus)
                    if phylogeny_data:
                        names = extractnames(phylogeny_data)
                        names.update({"input_species": organism})
                        names.update(
                            {"names_match": "Genus_Search"}
                        )  # Dodatna informacija
                        newly_fetched_data.append(names)
                        print(f"     -> Uspešno najdeno preko rodu: {genus}")
                except (RuntimeError, IndexError):
                    print(
                        f"     -> Tudi iskanje po rodu za '{organism}' ni uspelo. Preskakujem."
                    )
                    # Lahko bi dodali tudi v poseben seznam "nenajdenih"

    finally:
        # Ta blok se izvede VEDNO: po koncu zanke, ob napaki ali ob prekinitvi (Ctrl+C)
        print("\nZaključujem zanko. Shranjevanje napredka...")
        if newly_fetched_data:
            new_df = pd.DataFrame(newly_fetched_data)

            # Združimo stare in nove podatke
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)

            # Shranimo združeno tabelo v CSV
            combined_df.to_csv(output_filename, index=False)
            print(
                f"Uspešno shranjenih {len(newly_fetched_data)} novih vnosov v '{output_filename}'."
            )
        else:
            print("Ni novih podatkov za shranjevanje.")


def get_file(input_file):
    data = []
    with open(input_file, "r") as file:
        for line in file:
            data.append(line)
    return data


def data_cleaner(data):
    try:
        line = data.strip().split(" ")
        organism = f"{line[0]} {line[1]}"
    except IndexError:
        organism = data.strip()
    return organism


def getdata(organism, retries=3, delay=5):
    Entrez.email = "example@example.com"  # Vedno povej NCBI-ju, kdo si!
    attempts = 0
    cleaned_organism_name = data_cleaner(organism)

    while attempts < retries:
        try:
            handle = Entrez.esearch(db="Taxonomy", term=f'"{cleaned_organism_name}"')
            record = Entrez.read(handle)

            if not record["IdList"]:
                raise RuntimeError(
                    f"Organizem '{cleaned_organism_name}' ni bil najden v NCBI Taxonomy."
                )

            id_list = record["IdList"]
            handle = Entrez.efetch(
                db="Taxonomy", id=id_list[0]
            )  # Uporabimo samo prvi ID
            records = Entrez.read(handle)

            lineage = records[0]["LineageEx"]
            lineage.append(
                {
                    "TaxId": records[0]["TaxId"],
                    "ScientificName": records[0]["ScientificName"],
                    "Rank": "species",
                }
            )
            return lineage

        except HTTPError as e:
            print(f"HTTP napaka: {e}. Ponovni poskus čez {delay} sekund...")
            time.sleep(delay)
            attempts += 1
        except IndexError:
            raise RuntimeError(
                f"Organizem '{cleaned_organism_name}' ni bil najden v NCBI Taxonomy."
            )

    print("Doseženo maksimalno število poskusov. Pridobivanje podatkov ni uspelo.")
    return None


def extractnames(record):
    taxonomy = {}
    for item in record:
        rank = item["Rank"]
        scientific_name = item["ScientificName"]
        taxonomy[rank] = scientific_name
    return taxonomy

def get_arguments():
    # Argument parsing
    parser = argparse.ArgumentParser(
        prog="NCBI_taxonomy", description="Obtains taxonomy information from NCBI Taxonomy server"
    )

    parser.add_argument(
        "-i", "--infile", help="Input TXT file with organisms for which to obtain taxonomy", required=True, dest="infile"
    )  # Store the value in args.infile

    parser.add_argument(
        "-o", "--outfile", help="Output csv file with taxonomy information.", required=True, dest="outfile"
    )  # Store the value in args.outfile

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
