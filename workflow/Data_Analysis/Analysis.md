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
mafft --maxiterate 5000 --localpair --thread -1 ../cleaning/aegerolysins/7_outgroups/7.1_3_final_aeggero_all_outgroups_pula.fasta > aegerolysins_alignment_maxiter_5000_localpair.fasta
```

































