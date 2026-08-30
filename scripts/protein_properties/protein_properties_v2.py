#!/usr/bin/env python
import sys

import matplotlib.axes
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
import peptides
import seaborn as sns
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from matplotlib.ticker import AutoMinorLocator, FuncFormatter, MaxNLocator
import argparse
from pathlib import Path


def main():

    cla = get_arguments()

    input_file = cla.input

    seqdata_dict = get_data(input_file=input_file)

    for_pandas = {}
    for protein in seqdata_dict:
        properties = calculate_properties(protein=protein)
        for_pandas.update(properties)

    cols = [
        "cisteines",
        "aromaticity",
        "molecular_weight",
        "instability_index",
        "isoelectric_point",
        "gravy",
        "charge",
        "aliphatic_index",
    ]

    column_names = [
        "Število cisteinov",
        "Indeks Aromatičnosti",
        "Molekulska Masa",
        "Indeks Nestabilnosti",
        "Izoelektrična Točka",
        "GRAVY",
        "Naboj pri pH 7",
        "Alifatski Indeks",
    ]

    dataframe, average_dataframe = prepare_dataframe(for_pandas)

    output_csv(df=average_dataframe)

    # Set the colors for graphs.
    colors = [
        "#cb4f42",
        "#50ab6d",
        "#c457b8",
        "#929d3d",
        "#7b6aca",
        "#c98443",
        "#6698d1",
        "#c45e86",
    ]

    sns.set_style(
        "darkgrid",
        {
            "grid.color": ".6",
            "axes.edgecolor": "black",
            "axes.spines.right": "False",
            "axes.spines.top": "False",
        },
    )

    reference_protein = "jgi|PleosPC15_2|1090164|estExt_fgenesh1_kg.C_070197"

    set_font()

    fig, axs = plt.subplots(
        nrows=2, ncols=4, figsize=(11.69, 8.27)
    )  # Figsize corresponds to A4

    axis: matplotlib.axes.Axes  # Only for intellisense to work properly.
    for axis, subplot, color, name in zip(axs.flatten(), cols, colors, column_names):

        # Make specific bin width for cisteine count so graph is better looking.
        if subplot == "cisteines":
            sns.histplot(
                data=dataframe, ax=axis, x=subplot, color=color, kde=True, bins=11
            )
            axis.xaxis.set_major_locator(MaxNLocator(integer=True))
        else:
            sns.histplot(data=dataframe, ax=axis, x=subplot, color=color, kde=True)
        axis.set_xlabel(name)

        # Make sure only the two left most plots have titles.
        if axis.get_subplotspec().is_first_col() == True:
            axis.set_ylabel("Število Proteinov", fontsize=10)
        else:
            axis.set(ylabel="")

        axis.plot(
            dataframe.loc[reference_protein, subplot], 0.4, marker="^", mfc="#08FF08"
        )

        # Plot mean of each graph.
        axis.axvline(dataframe[subplot].mean())

        # Format ticks
        format_ticks(ax=axis)

        # Scale axes so that it starts and ends on major locator.
        scale_axis(ax=axis, df=dataframe, subplot=subplot)

        axis.grid(True, which="minor", color="lightgray", linestyle="-", linewidth=0.5)

    plt.savefig(cla.output)
    # plt.savefig(sys.argv[2], dpi=300    )


def get_arguments():
    # Handles command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=Path,
        help="Path to Amino Acid FASTA file with proteins whose properties need to be determined.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="Name of the fig with extension.",
    )
    args = parser.parse_args()
    return args


def get_data(input_file) -> dict:
    """
    Opens a fasta file and returns a dict of p
    """
    seqdata = []
    for record in SeqIO.parse(input_file, "fasta"):

        record.seq = record.seq.rstrip("*")
        if "X" in record.seq:
            with open("not_imported.txt", "w") as outfile:
                outfile.write(
                    f"Not imported, contains X - ambiguous amino acids, ID: {record.id}"
                )
        else:
            seqdata.append(record)

    seqdata_dict = []

    for protein in seqdata:
        seqdata_dict.append({"ID": protein.id, "sequence": protein.seq})

    return seqdata_dict


def calculate_properties(protein):
    """
    Calculate and return the protein properties for each protein.
    """

    sequence_str = str(protein["sequence"])
    prot_param_obj = ProteinAnalysis(sequence_str)
    peptide_obj = peptides.Peptide(sequence_str)

    cisteines = prot_param_obj.count_amino_acids()["C"]
    aromaticity = prot_param_obj.aromaticity()
    molecular_weight = prot_param_obj.molecular_weight()
    instability_index = prot_param_obj.instability_index()
    isoelectric_point = prot_param_obj.isoelectric_point()
    gravy = prot_param_obj.gravy(scale="AbrahamLeo")
    charge = prot_param_obj.charge_at_pH(pH=7)
    aliphatic_index = peptide_obj.aliphatic_index()

    properties_dict = {
        protein["ID"]: [
            cisteines,
            aromaticity,
            molecular_weight,
            instability_index,
            isoelectric_point,
            gravy,
            charge,
            aliphatic_index,
        ]
    }

    return properties_dict


def prepare_dataframe(for_pandas):
    """Creates a panndas dataframe and include average/median summary rows."""
    dataframe = pd.DataFrame.from_dict(
        for_pandas,
        orient="index",
        columns=[
            "cisteines",
            "aromaticity",
            "molecular_weight",
            "instability_index",
            "isoelectric_point",
            "gravy",
            "charge",
            "aliphatic_index",
        ],
    )

    dataframe = dataframe.apply(pd.to_numeric, errors="coerce")

    average_row = dataframe.mean(numeric_only=True).round(2)
    median_row = dataframe.median(numeric_only=True).round(2)

    average_dataframe = dataframe.copy()
    average_dataframe.loc["Average"] = average_row
    average_dataframe.loc["median"] = median_row

    return dataframe, average_dataframe


def output_csv(df):
    """
    Output the files to csv file.
    """
    if input("Save to csv? ([Y / N]) ").strip().lower() == "y":
        df.round(2)
        df.to_excel("values.xlsx", index=True)


def set_font():
    """Imports and sets the font to "arial narrow" as the default font for the graphs."""

    # Importing and using arial narrow font.
    custom_font = fm.FontProperties(
        fname="/usr/share/fonts/Arial-Narrow/arialnarrow_bold.ttf"
    )

    # Get the name of the font for later referencing.
    font_name = custom_font.get_name()

    # Add the font.
    fm.fontManager.addfont("/usr/share/fonts/Arial-Narrow/arialnarrow_bold.ttf")

    # Set the font.
    matplotlib.rcParams["font.family"] = font_name
    # Ensure compatibility if exporting to PDF.
    matplotlib.rcParams["pdf.fonttype"] = 42


def format_ticks(ax):
    """
    Handles formating ticks on the x and y axis.
    """
    # Ticks
    # Automatically determine small ticks for x and y axis
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    # Make sure the y axis label doesn't overlap tick labels
    ax.tick_params(axis="y", pad=1, which="both")

    # Set minor and major ticks on x and y axis ON, set the lenght of major and minor ticks.
    ax.tick_params(axis="both", which="major", bottom=True, left=True, length=6)
    ax.tick_params(axis="both", which="minor", bottom=True, left=True, length=3)

    # Decimal places in axis lables need to be with commas, not dots as by default.
    ax.xaxis.set_major_formatter(FuncFormatter(to_comma))
    ax.yaxis.set_major_formatter(FuncFormatter(to_comma))


def to_comma(x, pos):
    """
    Changes the decimal point of ticks from a dot to a comma.
    """
    return f"{x:g}".replace(".", ",")


def scale_axis(ax, df, subplot):
    """
    This handles the problem of labels not showing up at the max or min value on each axis.
    For example if data ends at 10.4 the axis can get cut off at 10.5 and no major label is shown.
    Ensures also that the coordinate system izhodišče is set at the intersection between the x and y major axis, without it sometimes they are not aligned.
    """

    # Start y axis at 0
    ax.set_ylim(bottom=0)

    # Get minimum and maximum for each property from the df
    min_val = df[subplot].min()
    max_val = df[subplot].max()

    # Set major tics so that lables are shown.
    ticks = ax.xaxis.get_major_locator().tick_values(min_val, max_val)

    # Coordinate system needs to start at 0
    ax.set_xlim(ticks[0], ticks[-1])

    #
    # Grab the current Y-axis boundaries that Matplotlib automatically set for the histogram
    ymin, ymax = ax.get_ylim()

    # Ask the Y-axis locator for the "nice" round numbers that enclose this range
    yticks = ax.yaxis.get_major_locator().tick_values(ymin, ymax)

    # Lock the Y-axis to start at 0 and stop at highest generated tick
    ax.set_ylim(bottom=0, top=yticks[-1])


if __name__ == "__main__":
    main()
