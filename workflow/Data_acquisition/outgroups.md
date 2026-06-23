Za outgroup proteine smo uporabili proteine iz dveh različnih razredov - Eurotiomycetes in Sordariomycetes. 
UJporabili smo štiri proteine iz Aspergillus niger NRRL3 - dva aegerolizina in dva "macpf-like" proteina.
- Ali so to že znani/delujejo preverjeno.. ali morem napisati kakšno referenco glede tega? Ali moram napisati kateri so delujoči, kateri so samo v teoriji delujoči in kateri so pari?



TODO: Dodaj informacije o outgroupih.

Vse prenešene outgroupe smo preverili s pomočjo HMMER spletnega serverja ter ugotovili, kateri rezultati so signifikantni. Prav tako smo s pomočjo skripte izrisali domene prisotne na proteinu.

Proteinske sekvence smo najprej združili v skupno datoteko![alt text](image.png)

S tem ukazom združimo datoteke v eno, seqkit seq uporabimo, zato da se izenačijo dolžine sekvenc.
for file in $(find data/outgroups/*_protein.fasta); do seqkit seq $file >> results/outgroups/outgroups_protein.fasta; done


Nato narišemo slike:
for file in $(find results/outgroups/hmmer/hmmer_results/ -iname "*.json"); do base=$(basename $file .json); svg="${base}.s
vg"; python scripts/hmmer_features/features.py -d $file -o "results/outgroups/hmmer/hmmer_pictures/${svg}"; done