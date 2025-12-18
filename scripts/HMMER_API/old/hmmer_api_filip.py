import requests
import time
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from Bio import SeqIO
import sys

def extract_svg(url,name):
    driver = webdriver.Chrome()  # Ensure you have chromedriver installed
    try:
        driver.get(url)
        
        # Wait for JavaScript rendering (increase time if needed)
        time.sleep(5)  

        # Find the SVG inside #domGraph
        svg_element = driver.find_element(By.CSS_SELECTOR, "#domGraph")

        if svg_element:
            svg_content = svg_element.get_attribute("outerHTML")  # Extract the full SVG
            
            svg_content = svg_content.replace(f"{url}","")

            # Save to an SVG file
            with open(f"{name}.svg", "w", encoding="utf-8") as file:
                file.write(svg_content)

            print(f"SVG extracted and saved as '{name}.svg'")
        else:
            print("No SVG found in #domGraph")
    
    except Exception as e:
        print("Error:", e)

    finally:
        driver.quit()

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
    url = "https://www.ebi.ac.uk/Tools/hmmer/search/hmmscan"

    payload = {"hmmdb": "pfam", "seq": sequence}
    headers = {"Accept": "application/json"}


    # Submit sequence
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        with open(f"{name}.json", "w", encoding="utf-8") as file:
            json.dump(result, file, indent=2)
        #print("Full JSON Response:", json.dumps(result, indent=2))  # Debugging

        result = result.get("results")  # Extract first result
        uuid = result.get("uuid")  # Extract UUID
        #print("UUID:", uuid)  # Debugging
        
        if uuid:
            print(f"Job submitted! UUID: {uuid}")

            # Wait before fetching results
            time.sleep(10)  # Increase if needed

            # Fetch results
            result_url = f"https://www.ebi.ac.uk/Tools/hmmer/results/{uuid}/score"
            print(f"Fetching results from: {result_url}")
            result_response = requests.get(result_url)

            if result_response.status_code == 200:
                #print("Results:\n", result_response.text)
            #    print(result_response)
                return(result_url)



            else:
                print(f"Error fetching results: {result_response.status_code}")
        else:
            print("UUID not found in response.")
    else:
        print(f"Error: {response.status_code}")


def main():
    file_path = get_fasta_file()
    sequences = get_sequences(file_path)
    for sequence in sequences:
        seq = str(sequence.seq)
        id = str(sequence.id).replace("|", "_")
        return_url = get_hmmer_data(seq, name=id)
        extract_svg(url=return_url, name=id)

if __name__ == "__main__":
    main()