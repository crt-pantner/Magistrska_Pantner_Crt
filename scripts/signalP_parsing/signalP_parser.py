#!/usr/bin/env python
import json

import matplotlib.axes
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import AutoMinorLocator, FuncFormatter, MultipleLocator
import numpy as np


def to_comma(x, pos):
    """
    Changes the decimal point of ticks from a dot to a comma. 
    """
    return f"{x:g}".replace('.', ',')

with open(input("json summary file: "), "r") as file:
    data = json.load(file)

non_signal_sequence = []
parsed_data = []

for sequence in data["SEQUENCES"]:
    if data["SEQUENCES"][sequence]["Prediction"] == "Other":
        value = data["SEQUENCES"][sequence]["Likelihood"][0] #ker imamo zbrano na koncu nič, se nam izpišejo verjetnosti, da je ta protein signalna molekula oz. signalni peptid.
        pair = [sequence, value]
        non_signal_sequence.append(pair)
    else:
        value = data["SEQUENCES"][sequence]["Likelihood"][1]
        value = float(value) #ker imamo zbrano na koncu nič, se nam izpišejo verjetnosti, da je ta protein signalna molekula oz. signalni peptid.
        pair = [sequence, value]
        parsed_data.append(pair)

names = ["sequence", "probability"]

parsed_data_frame = pd.DataFrame(data=parsed_data, columns=names)

non_signal_sequence = pd.DataFrame(data=non_signal_sequence, columns=names)



probability_signal_sequence = 1 - non_signal_sequence["probability"]


sns.set_style("darkgrid", {"grid.color": ".6", "axes.edgecolor": "black", "axes.spines.right" : "False", "axes.spines.top": "False"})
custom_font = fm.FontProperties(fname='/usr/share/fonts/Arial-Narrow/arialnarrow_bold.ttf')
font_name = custom_font.get_name()
fm.fontManager.addfont('/usr/share/fonts/Arial-Narrow/arialnarrow_bold.ttf')
matplotlib.rcParams['font.family'] = font_name
matplotlib.rcParams['font.size'] = 11
matplotlib.rcParams['pdf.fonttype'] = 42


clean_bins = np.arange(0, 0.55, 0.05)


g = sns.histplot(data=probability_signal_sequence, bins=clean_bins)
bin_width = g.patches[0].get_width()
g.set_xlabel("Verjetnost prisotnosti signalnega zaporedja")
g.set_ylabel("Število proteinov")


# Ticks
# Automatically determines the minor locator for the x and y axis.
g.xaxis.set_minor_locator(AutoMinorLocator()) 
g.yaxis.set_minor_locator(AutoMinorLocator()) 

# Let the x axis major locator be 0.5 since subplots are quite small.
g.yaxis.set_major_locator(MultipleLocator(50))
g.xaxis.set_major_locator(MultipleLocator(bin_width))

g.tick_params(axis="y", pad=1, which="both")
g.tick_params(axis="x", pad=1, which="both", labelsize=9)


# Set minor and major ticks on x and y axis, set the lenght of major and minor ticks.
g.tick_params(axis="both", which="major", bottom=True, left=True, length=6)
g.tick_params(axis="both", which="minor", bottom=True, left=True, length=3)


# Decimal places in axis lables need to be with commas, not dots as by default.
g.xaxis.set_major_formatter(FuncFormatter(to_comma))
g.yaxis.set_major_formatter(FuncFormatter(to_comma))

# Make the grid so that minor ticks are also shown.
g.grid(True, which="minor", color="lightgray", linestyle="-", linewidth=0.5)

# Set the x and y limits on the axes so that ticks are not cut off between values.
plt.ylim(0,250)
plt.xlim(0,1)

#plt.show()

plt.savefig("histogram_no_signal.png")