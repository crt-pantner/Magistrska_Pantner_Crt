import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
data = "D:/Documents/Magistrska/DeepLooc/pf06355_rez/pf06355_rez_najnovejsi.csv"

dataframe = ""

with open(data, "r") as deep_loc_data:
    dataframe = pd.read_csv(data, delimiter=",")

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

columns = ['Cytoplasm',
       'Nucleus', 'Extracellular', 'Cell membrane', 'Mitochondrion', 'Plastid',
       'Endoplasmic reticulum', 'Lysosome/Vacuole', 'Golgi apparatus',   
       'Peroxisome', 'Peripheral', 'Transmembrane', 'Lipid anchor', 'Soluble']

print(dataframe["Mitochondrion"])

sns.set_theme(style="darkgrid")
sns.set_style("ticks")

fig, axs = plt.subplots(2, 4, figsize=(10,10))


g = sns.histplot(data=dataframe, color=colors[0],  x="Cytoplasm", ax=axs[0, 0], kde=True)
g.set_xlabel("Citoplazma")
g.set_ylabel("Število proteinov")
nucleus = sns.histplot(data=dataframe, color=colors[1],  x="Nucleus", ax=axs[0, 1], kde=True)
nucleus.set_xlabel("Jedro")
nucleus.set_ylabel("Število proteinov")
mitochondrion = sns.histplot(data=dataframe, color=colors[2], x="Mitochondrion", ax=axs[0, 2], kde=True)
mitochondrion.set_xlabel("Mitohondrij")
mitochondrion.set_ylabel("Število proteinov")
plastid = sns.histplot(data=dataframe, color=colors[3], x="Plastid", ax=axs[0, 3], kde=True)
plastid.set_xlabel("Plastid")
plastid.set_ylabel("Število proteinov")
er =sns.histplot(data=dataframe, color=colors[4], x="Endoplasmic reticulum", ax=axs[1, 0], kde=True)
er.set_xlabel("Endoplazmatski retikel")
er.set_ylabel("Število proteinov")
lizosom = sns.histplot(data=dataframe, color=colors[5],  x="Lysosome/Vacuole", ax=axs[1, 1], kde=True)
lizosom.set_xlabel("Lizosom")
lizosom.set_ylabel("Število proteinov")
golgi = sns.histplot(data=dataframe, color=colors[6],  x="Golgi apparatus", ax=axs[1, 2], kde=True)
golgi.set_xlabel("Goglijev aparat")
golgi.set_ylabel("Število proteinov")
peroksisom = sns.histplot(data=dataframe, color=colors[7],  x="Peroxisome", ax=axs[1, 3], kde=True)
peroksisom.set_xlabel("Peroksisom")
peroksisom.set_ylabel("Število proteinov")

plt.show()


fig, axs = plt.subplots(2, 3, figsize=(10,10))


periferni = sns.histplot(data=dataframe, color=colors[8],  x="Peripheral", ax=axs[0, 0], kde=True)
periferni.set_xlabel("Preiferni")
periferni.set_ylabel("Število proteinov")
transmembranski = sns.histplot(data=dataframe, color=colors[9],  x="Transmembrane", ax=axs[0, 1], kde=True)
transmembranski.set_xlabel("Transmembranski")
transmembranski.set_ylabel("Število proteinov")
lipid_anchor = sns.histplot(data=dataframe, color=colors[10],  x="Lipid anchor", ax=axs[0, 2], kde=True)
lipid_anchor.set_xlabel("Lipidno sidro")
lipid_anchor.set_ylabel("Število proteinov")
topen = sns.histplot(data=dataframe, color=colors[11],  x="Soluble", ax=axs[1, 0], kde=True)
topen.set_xlabel("Topen")
topen.set_ylabel("Število proteinov")
izvenceličen = sns.histplot(data=dataframe, color=colors[12], x="Extracellular", ax=axs[1, 1], kde=True)
izvenceličen.set_xlabel("Izvencelično")
izvenceličen.set_ylabel("Število proteinov")
celična_membrana = sns.histplot(data=dataframe, color=colors[13], x="Cell membrane", ax=axs[1, 2], kde=True)
celična_membrana.set_xlabel("Celična membrana")
celična_membrana.set_ylabel("Število proteinov")

plt.show()