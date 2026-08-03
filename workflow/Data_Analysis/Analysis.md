# Sankey diagram

Sankey diagram smo narisali s pomočjo spletnega programa Sankey matic

Rezultati so shranjeni v direktoriju /results/analysis/graphs

# Phylogenetic distribution

Filogenetsko distribucijo smo izračunali s pomočjo namensko napisane skripte
### 5.3 Statistika končna

Pridobimo statistiko vsebnosti proteinov


TODO: MOVE THIS TO ANALYSIS

```bash
python ../../scripts/stat/stat_v2.py -m aegerolysins/5_seqdupes/5.2_aegerolysins_noseqdupes_metadata.csv -p basidiomycota_phylogeny/basidiomycota_taxonomy.csv -o aegerolysins/5_seqdupes/5.3_aegero_noseqdupes_statistics.xlsx
```