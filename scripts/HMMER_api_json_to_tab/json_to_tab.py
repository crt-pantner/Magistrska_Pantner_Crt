import json
from pathlib import Path
import argparse
import pandas as pd


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-dir",
        required=True,
        type=str,
        default=".",
        help="Directory containing json hmmer result files obtained through hmmer API. By default it searches within current working directory.",
    )
    """parser.add_argument(
        "-o",
        required=True,
        type=str,
        default=".",
        help="Directory for output of result files",
    )"""

    args = parser.parse_args()
    return args


def main():
    arguments = get_arguments()

    json_folder = Path(arguments.dir)

    json_paths = []
    for path in Path(json_folder).rglob("*.json"):
        json_paths.append(path)

    valid_domains = []

    for json_file in json_paths:
        try:
            data = open_json(json_file)
            hits = data["result"]["hits"]

            for hit in hits:
                for domain in hit.get("domains", []):
                    if domain.get("significant"):
                        domain_info = {
                            "organism": json_file.stem.replace("_hmmerrez", ""),
                            "pfam_acc": hit["acc"],
                            "pfam_id": hit["metadata"]["identifier"],
                            "description": hit["metadata"]["description"],
                            "start": domain["alignment_display"]["sqfrom"],
                            "end": domain["alignment_display"]["sqto"],
                            "bitscore": domain["bitscore"],
                            "evalue": domain["ievalue"],
                            "displayed": domain.get("display", False),
                        }
                        valid_domains.append(domain_info)

            # print(len(valid_domains))

        except TypeError:
            pass

    df = pd.DataFrame(valid_domains)

    # Create cleaned dataframe with only proteins whose domains are MACPF related.
    # There may be some exceptions in this, but since we already filter by evalue while parsing, we can assume that all of these are significant.
    macpf_values = ["MACPF", "MACPF_1", "PlyB_C"]
    cleaned_df_macpf = df[df["pfam_id"].isin(macpf_values)]
    cleaned_df_aegero = df[df["pfam_id"] == "Aegerolysin"]

    # Output the results to excel file.
    output_filename = "significant_hits_report.xlsx"
    # print("Outputing report to excel..")

    with pd.ExcelWriter(output_filename) as writer:
        df.to_excel(writer, index=False, sheet_name="all_domains")
        cleaned_df_macpf.to_excel(writer, index=False, sheet_name="MACPF_containing")
        cleaned_df_aegero.to_excel(
            writer, index=False, sheet_name="aegerolysin_containing"
        )

    # Output results for macpfs for downstream processing.
    nodup_df = cleaned_df_macpf.drop_duplicates(subset="organism")
    nodup_df["organism"].to_csv(
        "macpf_containing_proteins.csv", index=False, header=False
    )

    # Output resutls for aegerolysins for downstream processing.
    nodup_df = cleaned_df_aegero.drop_duplicates(subset="organism")
    nodup_df["organism"].to_csv(
        "aegerolysin_containing_proteins.csv", index=False, header=False
    )


def open_json(path: Path):
    json_dict = {}

    with open(path, "r") as json_file:
        json_dict = json.load(json_file)

    json_dict["result"]["stats"]["id"] = path.stem.rstrip("_hmmerrez")
    # print(json_dict["result"]["stats"]["id"])

    return json_dict


if __name__ == "__main__":
    main()
