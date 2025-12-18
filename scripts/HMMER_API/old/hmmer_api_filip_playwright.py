import requests
import time
import json
import time
from playwright.sync_api import sync_playwright, TimeoutError
from Bio import SeqIO
import sys
import os
import time
from tqdm import tqdm
import xml.etree.ElementTree as ET

def export_placeholder_svg(name, lenght):
    """
    Generates a simple SVG representing a protein sequence as a rectangle,
    scaled by the observed correlation factor.
    """
    scaling_factor = 0.4925
    svg_width_base = lenght * scaling_factor
    svg_height = 20
    margin = 5
    final_svg_width = svg_width_base + (2 * margin)
    final_viewbox_width = final_svg_width

    svg_template = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{final_svg_width}" height="{svg_height}" viewBox="0 0 {final_viewbox_width} {svg_height}" style="width: {final_svg_width*2}px; height: {svg_height*2}px;">
  <g transform="translate({margin} 10)" data-entity="sequence">
    <rect x="0" y="-2.5" width="{svg_width_base}" height="5" fill="#d8d8d8" rx="2.5" ry="2.5"></rect>
  </g>
</svg>
"""
    return svg_template.strip()


def add_labels(svg): # Adds the xmlns namespace for the svg (ensures opening of svg in browser) and replaces the label.
    
    root = ET.fromstring(svg)
    if 'xmlns' not in root.attrib:
        root.set('xmlns', "http://www.w3.org/2000/svg")
    
    for elem in root.iter('text'):
        print(elem.text)
    
    return ET.tostring(root, encoding='unicode')

def extract_svg(url, name, lenght):
    
    #Formatting the name on the svg and output name
    orig_name = name

    name = name.split("_")
    name = name[1] + "_" + name[2]
    

    with sync_playwright() as p:
        browser = p.chromium.launch() # or headless=False for visual debugging
        page = browser.new_page()
        page.goto(url=url)

        # Define the selector for the SVG when hits ARE found
        svg_selector = "div > svg"

        # Define the selector for the "No matches found" paragraph
        no_matches_selector =  "h4.vf-text.vf-text-heading--4.vf-u-margin__bottom--0:has-text('Sequence Features and Matches') + div > p.vf-text.vf-text-body--5:has-text('No matches found')"
        try:
            # IF no matches are found the page should load quickly, so if timeout of 1s is exceeded, matches are most likely found.
            no_matches_element_handle = page.wait_for_selector(no_matches_selector, timeout=1000)
            no_matches_text = no_matches_element_handle.evaluate("element => element.textContent")
            
            

            print(f"[{name}] '{no_matches_text}' detected. Generating placeholder SVG.")
            svg = export_placeholder_svg(name, lenght)
            with open(f"{name}_placeholder.svg", "w") as f:
                f.write(svg)
            print(f"Placeholder SVG for {name} saved.")



        except TimeoutError: 
            svg_element_handle = page.wait_for_selector(svg_selector)
            svg_content = svg_element_handle.evaluate("element => element.outerHTML")

            svg_content = add_labels(svg_content)
            with open(f"{name}.svg", "w") as out_svg:
                out_svg.write(svg_content)

        browser.close()
        

def get_sequences(input_fasta_file):
    seq_records = []

    for seq_record in SeqIO.parse(input_fasta_file, "fasta"):
        seq_records.append(seq_record)
    
    return(seq_records)

#returns fasta file path from command line arguments
def get_fasta_file():
    try:
        path_to_file = sys.argv[1]
        return path_to_file
    except IndexError:
        sys.exit("Missing path to fasta file")


#Returns the url for svg extraction and saves domain data
def get_hmmer_data(sequence, name):
# API endpoint
    url = "https://www.ebi.ac.uk/Tools/hmmer/api/v1/search/hmmscan"
    
    headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
            }
    payload = {
    "input": sequence,
    "database": "pfam",
    "treshold":"evalue",
    "E":"10",
    "domE":"30"
            }

    # Submit sequence
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        #Contains UUID of our result
        result = response.json()    
        #Get UUID for results
        uuid = result["id"]
        
        
        if uuid:
            print(f"Job submitted! UUID: {uuid}")

            # Fetch results
            result_url = f"https://www.ebi.ac.uk/Tools/hmmer/api/v1/result/{uuid}"
            webpage_url = f"https://www.ebi.ac.uk/Tools/hmmer/results/{uuid}/score"
            print(f"Fetching results from: {result_url}")
            result_response = requests.get(result_url)
            print(result_response)
            
            
            # Export results into json
            if result_response.status_code == 200:
                with open(f"{name}.json", "w", encoding="utf-8") as file:
                    json.dump(result_response.json(), file)
                quit()
                return(webpage_url)

            else:
                print(f"Error fetching results: {result_response.status_code}")
        else:
            print("UUID not found in response.")
    else:
        print(f"Error: {response.status_code}")


def main():
    
    file_path = get_fasta_file()
    sequences = get_sequences(file_path)
    record_num = len(sequences)
    for sequence in tqdm(sequences):
        
        sequence_lenght = len(sequence.seq)
        
        seq = str(sequence.seq)
        id = str(sequence.id).replace("|", "_")
        id = id.replace("/", "_")
        if os.path.exists(f"{id}.json") == False:
            
            return_url = get_hmmer_data(seq, name=id)
            extract_svg(url=return_url, name=id, lenght=sequence_lenght)
        else:
            print("Path exists, skipping")
            pass
        record_num = record_num - 1
        
        
        print(f"Remaining records: {record_num}")
        

        

if __name__ == "__main__":
    main()