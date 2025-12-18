import argparse
import pandas as pd

def get_arguments():
    # Argument parsing
    parser = argparse.ArgumentParser(
        prog="metadata merger", description="Merges phylogeny of organisms and metadata jgi file."
    )

    parser.add_argument(
        "-p", "--phylogeny", help="CSV file with the phylogeny obtained from taxonomy.py", required=True, dest="phylogeny"
    )  # Store the value in args.infile

    parser.add_argument(
        "-m", "--metadata", help="File with JGI metadata with which to merge the phylogeny", required=True, dest="metadata"
    )  

    parser.add_argument(
        "-o", "--output", help="Name of output file of merged phylogeny and metadata files", required=True, dest="outfile"
    )

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = get_arguments()

    metadata_path = args.metadata
    phylogeny_path = args.phylogeny
    output_path = args.outfile

    metadata_df = pd.read_csv(metadata_path)
    phylogeny_df = pd.read_csv(phylogeny_path)
    
    phylogeny_df = phylogeny_df.rename(columns={"input_species": "Organism Name"})


    merged_df = metadata_df.merge(phylogeny_df, on=["Organism Name"], how="inner")

    merged_df.to_csv(output_path, index=False)