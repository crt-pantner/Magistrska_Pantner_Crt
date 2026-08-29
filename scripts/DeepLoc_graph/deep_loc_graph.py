#!/usr/bin/env python
import sys

import matplotlib.axes
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import AutoMinorLocator, FuncFormatter, MultipleLocator

data = sys.argv[1]

dataframe = ""

with open(data, "r") as deep_loc_data:
    dataframe = pd.read_csv(data, delimiter=",", index_col=0)

colors = ["#d94983",
"#59b445",
"#bf50b5",
"#9eb841",
"#7762cd",
"#c4a736",
"#6384c7",
"#dd7d34",
"#4abfcc",
"#cc423c",
"#60c084",
"#c483c5",
"#6a7f34",
"#9d4765",
"#37855c",
"#dc7c7b",
"#d0a768",
"#95632d"]

# Prepare order in which graphs will be shown on the plot
columns = ['Plastid', 
            'Transmembrane', 
            'Peroxisome', 
            'Endoplasmic reticulum', 
            'Lysosome/Vacuole', 
            'Golgi apparatus', 
            'Cell membrane', 
            'Lipid anchor', 
            'Nucleus', 
            'Peripheral', 
            'Mitochondrion', 
            'Cytoplasm', 
            'Extracellular', 
            'Soluble']

# Prepare slovenian translation of each sublocalisation.
column_names = [
    "Plastid",
    "Transmembransko",
    "Peroksisom",
    "Endoplazmatski retikel",
    "Lizosom/vakuola",
    "Golgijev aparat",
    "Celična membrana",
    "Lipidno sidro",
    "Jedro",
    "Periferno",
    "Mitohondrij",
    "Citoplazma",
    "Zunajcelično",
    "Topno"
]


def to_comma(x, pos):
    """
    Changes the decimal point of ticks from a dot to a comma. 
    """
    return f"{x:g}".replace('.', ',')


sns.set_style("darkgrid", {"grid.color": ".6", "axes.edgecolor": "black", "axes.spines.right" : "False", "axes.spines.top": "False"})

# Importing and using arial narrow font.
custom_font = fm.FontProperties(fname='/usr/share/fonts/Arial-Narrow/arialnarrow_bold.ttf')
font_name = custom_font.get_name()
fm.fontManager.addfont('/usr/share/fonts/Arial-Narrow/arialnarrow_bold.ttf')
matplotlib.rcParams['font.family'] = font_name
matplotlib.rcParams['pdf.fonttype'] = 42



reference_protein = "jgi_PleosPC15_2_1090164_estExt_fgenesh1_kg.C_070197"

# Prepare number canvas with 14 subplots, figsize being A4
fig, axs = plt.subplots(nrows=2, ncols=7, figsize=(11.69,8.27))

# Manually defined so the graph is as big as it can be on the A4 page
plt.tight_layout(h_pad=2, w_pad=0.5)
plt.subplots_adjust(bottom=0.08, left=0.05)


axis: matplotlib.axes.Axes # Only for intellisense to work properly.
for axis, subplot, color, name in zip(axs.flatten(), columns, colors, column_names):
    sns.histplot(data=dataframe, ax=axis, x=subplot, color=color, kde=True)

    axis.set_xlabel(name, fontsize=10)
    # Make sure all the subplots' x axes are from 0 to 1 (since they are probability values.)
    axis.set(xlim=(0,1))
    subplot_spec = axis.get_subplotspec()
    if subplot_spec is not None and subplot_spec.is_first_col():
        axis.set_ylabel("Število Proteinov", fontsize=10)
    else:
        axis.set(ylabel="")

    probability = float(dataframe.loc[reference_protein, subplot]) # type: ignore

    axis.plot(probability,0.4, marker="^", mfc="#08FF08")
    axis.axvline(dataframe[subplot].mean())

    # Ticks
    # Automatically determines the minor locator for the x and y axis.
    axis.xaxis.set_minor_locator(AutoMinorLocator()) 
    axis.yaxis.set_minor_locator(AutoMinorLocator()) 

    # Let the x axis major locator be 0.5 since subplots are quite small.
    axis.xaxis.set_major_locator(MultipleLocator(0.5))

    axis.tick_params(axis="y", pad=1, which="both")

    # Set minor and major ticks on x and y axis, set the lenght of major and minor ticks.
    axis.tick_params(axis="both", which="major", bottom=True, left=True, length=6)
    axis.tick_params(axis="both", which="minor", bottom=True, left=True, length=3)
    
    
    # Decimal places in axis lables need to be with commas, not dots as by default.
    axis.xaxis.set_major_formatter(FuncFormatter(to_comma))
    axis.yaxis.set_major_formatter(FuncFormatter(to_comma))

    # Make the grid so that minor ticks are also shown.
    axis.grid(True, which="minor", color="lightgray", linestyle="-", linewidth=0.5)

plt.savefig("deep_loc_graph.pdf")