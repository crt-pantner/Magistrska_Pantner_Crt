# Sankey diagram

Sankey diagram smo narisali s pomočjo spletnega programa Sankey matic

Rezultati so shranjeni v direktoriju /results/analysis/graphs

# Phylogenetic distribution

Filogenetsko distribucijo smo izračunali s pomočjo namensko napisane skripte
### 5.3 Statistika končna

Pridobimo statistiko vsebnosti proteinov

```bash
python ../../scripts/stat/stat_v2.py -m aegerolysins/5_seqdupes/5.2_aegerolysins_noseqdupes_metadata.csv -p basidiomycota_phylogeny/basidiomycota_taxonomy.csv -o aegerolysins/5_seqdupes/5.3_aegero_noseqdupes_statistics.xlsx
```



## Poravnava

Poravnavo smo naredili s pomočjo programske opreme mafft verzije 7.525:

Ker predvidevamo, da aegerolizinske proteine sestavljajo večinoma proteini z eno domeno (kar sicer dokažemo tudi z HMMER-jem), ki je bolj ali manj variabilna in se lahko sekvence med njo dobro poravnajo, medtem ko algoritem ignorira ostale "flanking" dele sekvenc, ki se med sabo ne morejo poravnati.

```bash
mafft --maxiterate 5000 --localpair --thread -1 cleaning/aegerolysins/8_seqdupes/8.3_final_aegerolysins_deduplicated_seqs.fasta > alignment/aegerolysins/aegerolysins_alignment_maxiter_5000_localpair.fasta
```

## Izbor substitucijskega modela

Pred izračunom drevesa smo opravili izbor substitucijskega modela s pomočjo modeltest-ng

```bash
modeltest-ng -d aa -i alignment/aegerolysins/aegerolysins_alignment_maxiter_5000_localpair.fasta -o tree/aegerolysins/modeltest/modeltest_aegero --processes 8  --template raxml --verbose
```

zastavica "-d" definira, da imamo zaporedje sestavljeno iz aminokislin, "--proccesses 8" pomeni, da smo uporabili osem jeder za izračun najboljšega substritucijskega modela in "--template raxml" nam zagotavlja, da izbor poteka med substitucijskimi modeli, ki jih lahko raxml-ng uporablja, kar pomeni

RAXML-NG

```bash
# Check that the MSA file is okay
mkdir -p tree/aegerolysins/raxml-ng/check

raxml-ng --check --msa alignment/aegerolysins/aegerolysins_alignment_maxiter_5000_localpair.fasta --model WAG+G4 --prefix tree/aegerolysins/raxml-ng/check/aegerolysins_check

# Parse the MSA file and get recommended number of threads
mkdir -p tree/aegerolysins/raxml-ng/parse
 
raxml-ng --parse --msa alignment/aegerolysins/aegerolysins_alignment_maxiter_5000_localpair.fasta --model WAG+G4 --prefix tree/aegerolysins/raxml-ng/parse/aegerolysins_parse

# Run the tree calculation
mkdir -p tree/aegerolysins/raxml-ng/tree
raxml-ng --all --msa alignment/aegerolysins/aegerolysins_alignment_maxiter_5000_localpair.fasta --model WAG+G4 --prefix tree/aegerolysins/raxml-ng/tree/aegerolysins_final_tre
e --threads 8 --bs-metric fbp,tbe

```

















