import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

with open(input("json summary file: "), "r") as file:
    data = json.load(file)

parsed_data = []

for sequence in data["SEQUENCES"]:
    value = data["SEQUENCES"][sequence]["Likelihood"][0] #ker imamo zbrano na koncu nič, se nam izpišejo verjetnosti, da je ta protein signalna molekula oz. signalni peptid.
    pair = [sequence, value]
    parsed_data.append(pair)



names = ["sequence", "probability"]



parsed_data_frame = pd.DataFrame(data=parsed_data, columns=names)

filtered_df = parsed_data_frame[parsed_data_frame["probability"] <= 0.05]

sns.set_theme(style="darkgrid")
sns.set_style("ticks")
sns.set_palette("viridis")
g = sns.histplot(data=parsed_data_frame)
g.set_xlabel("Probability of signal sequence")
g.set_ylabel("Count")


plt.savefig("histogram.png")
