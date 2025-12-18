import requests
import json
from playwright.sync_api import sync_playwright, TimeoutError
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from tqdm import tqdm
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import re
import time

class PendingError(Exception):
    pass

def get_arguments():
    # Handles command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-seq",
        required=True,
        type=str,
        help="Path to fasta file with proteins for HMMER server."
    )
    args = parser.parse_args()
    return args


def open_fasta_file(location) -> list[SeqRecord]:
    # Handles opening the fasta file
    input_fasta_file = Path(location).resolve()
    

    seq_records = []

    for seq_record in SeqIO.parse(input_fasta_file, "fasta"):
        seq_records.append(seq_record)
    
    return(seq_records)

def export_hmmer_data(json_data, org_name):
    
    current_dir = Path.cwd()
    
    save_dir = current_dir / "hmmer_results"

    
    save_dir.mkdir(exist_ok=True)
    
    output_file = save_dir / f"{org_name.replace('|', '_')}_hmmerrez.json"
    
    with open(output_file, "w", encoding="utf-8") as hmmrez_file:
        json.dump(json_data.json(), hmmrez_file)

    return output_file

def status_checker(result_data):
    
    
    
    if result_data["status"] == "PENDING":
        raise PendingError("Results are pending, retrying")
        
    



def get_hmmer_data(sequence):
    
    # API endpoint
    url = "https://www.ebi.ac.uk/Tools/hmmer/api/v1/search/hmmscan"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
            }
    payload = {
        "input": str(sequence.seq),
        "database": "pfam",
        "domE":1,
        "domT":5,
        "E":1,
        "incdomE":0.03,
        "incdomT":22,
        "incE": 0.01,
        "incT":25,
        "threshold":"cut_ga"
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


def get_placeholder_svg(organism):
    """
    Generates a basic SVG showing a sequence bar and organism ID label.
    """
    id = organism.id

    length = len(organism.seq)
    scaling_factor = 0.4925
    svg_width_base = length * scaling_factor
    svg_height = 20
    margin = 5
    final_svg_width = svg_width_base + (2 * margin)

    # Put label just below the bar
    label_x = margin + svg_width_base / 2
    label_y = 15  # reasonably within viewBox

    svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{final_svg_width}" height="{svg_height}" viewBox="0 0 {final_svg_width} {svg_height}" style="width: {final_svg_width*2}px; height: {svg_height*2}px;">
  <g transform="translate({margin} 10)" data-entity="sequence">
    <rect x="0" y="-2.5" width="{svg_width_base}" height="5" fill="#d8d8d8" rx="2.5" ry="2.5"/>
  </g>
  <text x="{label_x}" y="{label_y}" text-anchor="middle" font-size="7.5" font-family="Sans-Serif" fill="black">{id}</text>
</svg>
"""
    return svg_template


def export_placeholder_svg(svg, organism):
    cwd = Path.cwd()

    image_path = cwd / "images" / "no_domains"

    image_path.mkdir(parents=True, exist_ok=True)
    
    output_file = image_path / f"{organism.id.replace('|', '_')}_nores"

    # Export the svg to a new file
    with open(f"{output_file}.svg", "w") as out_svg:
        out_svg.write(svg)

    # Export the names of proteins containing no significant domains to a list for easier processing.
    with open("no_domains.txt", "a") as out_txt:
        out_txt.write(f"{organism.id}\n")

def export_svg(svg, organism, lable):
    cwd = Path.cwd()

    folder = "labeled_images" if lable==True else "images"

    output_dir = cwd / folder
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{organism.id.replace('|', '_')}.svg"
    output_file = output_dir / filename

    with open(output_file, "w", encoding="utf-8") as out_svg:
        out_svg.write(svg)

def extract_svg(url, organism):
    with sync_playwright() as p:
        browser = p.chromium.launch() # Opens chromium browser in background
        page = browser.new_page()
        page.goto(url=url)

        # Define the selector for svg
        svg_selector = "div > svg"

        #Define selector if no matches are found on the sequence
        no_matches_selector =  "h4.vf-text.vf-text-heading--4.vf-u-margin__bottom--0:has-text('Sequence Features and Matches') + div > p.vf-text.vf-text-body--5:has-text('No matches found')"
        try:
            no_matches_element_handle = page.wait_for_selector(no_matches_selector, timeout=1000)
            no_matches_text = no_matches_element_handle.evaluate("element => element.textContent")
            no_matches_svg = get_placeholder_svg(organism)
            export_placeholder_svg(no_matches_svg, organism=organism)
            return no_matches_svg, False

            

        except TimeoutError:
            svg_element_handle = page.wait_for_selector(svg_selector)
            svg_content = svg_element_handle.evaluate("element => element.outerHTML")
            
            return svg_content, True

def add_labels(svg, organism):
    # Parse SVG string
    root = ET.fromstring(svg)

    # Define SVG namespace
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # Find all text elements using namespace
    for elem in root.findall(".//svg:text", ns):
        elem.text = organism.id  # or any label you want

    # Return modified SVG as string
    return ET.tostring(root, encoding='unicode')

def add_namespace(svg, continuation): # Adds xmlns namespace for browser viewing.
    if continuation == True:
        root = ET.fromstring(svg)
        if "xmlns" not in root.attrib:
            root.set("xmlns", "http://www.w3.org/2000/svg")
        return ET.tostring(root, encoding="unicode")
    else:
        pass


def main():
    arguments = get_arguments()
    # Open the fasta file with sequences and return list of BioSeqio objects 
    seq_objects = open_fasta_file(location=arguments.seq)

    done_proteins = []

    cwd = Path.cwd()
    proteins_path = cwd / "proteins.txt"

    print(proteins_path)
    
    if proteins_path.exists() == True:
        with open("proteins.txt", "r") as file:
            for line in file:
                line = line.strip("\n")
                done_proteins.append(re.sub(r'[\\/*?:"<>|]', '_', line))
    else:
        with open(proteins_path, "w") as file:
            pass
    
    print(done_proteins)
    
    
    # Parse the fasta file with sequences and return protein objects
    for sequence in tqdm(seq_objects):
        sequence.id = re.sub(r'[\\/*?:"<>|]', '_', sequence.id)
        if sequence.id not in done_proteins:
            
            with open("proteins.txt", "a") as file:
                file.write(f"{sequence.id}\n")
            # Submit request to HMMER API, save the hmmer results, get back webpage url for scraping
                webpage_url = get_hmmer_data(sequence)
            
            

            # Parse the webpage for results
            svg, continuation = extract_svg(webpage_url, sequence)
            
            
            
            if continuation == True:
                svg = add_namespace(svg=svg, continuation=continuation)
                export_svg(svg=svg, organism=sequence, lable=False)
                labeled_svg = add_labels(svg, organism=sequence)
                export_svg(labeled_svg, sequence, lable=True)
            time.sleep(1)
    


        

        
        
        
        

        

if __name__ == "__main__":
    main()