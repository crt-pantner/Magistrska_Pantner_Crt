import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


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


print(non_signal_sequence)
    



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

non_signal_sequence = pd.DataFrame(data=non_signal_sequence, columns=names)

filtered_df = non_signal_sequence[non_signal_sequence["probability"] >= 0.05]

sns.set_theme(style="darkgrid")
sns.set_style("ticks")
sns.set_palette("viridis")
g = sns.histplot(data=non_signal_sequence)
g.set_xlabel("Probability of sequence being 'OTHER'")
g.set_ylabel("Count")


plt.savefig("histogram_no_signal.png")
