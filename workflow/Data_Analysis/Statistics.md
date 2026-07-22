#### 3.6.1. Pridobimo filogenijo za aegerolizin-vsebujoče proteine

**Pomembno, vhodna datoteka s filogenijo (se nahaja za -i zastavico) mora vsebovati informacije o filogeniji za celotno Basidiomycota deblo**

```bash
mkdir -p basidiomycota_phylogeny

# Perform phylogeny lookup on NCBI
python3 ../../scripts/NCBI_taxonomy/taxonomy_v7_pandas_gemini.py -i ../../data/basidiomycota_for_taxonomy.txt -o ../cleaning/basidiomycota_phylogeny/basidiomycota_taxonomy.csv
```

#### 3.6.3. Pridobimo statistiko

```bash
# Run script that obtains statistics
python3 ../../scripts/stat/stat_v2.py -m macpf/3_hmmer/3_4_after_hmmer/3.4.5_macpf_after_hmmer.csv -p basidiomycota_phylogeny/basidiomycota_taxonomy.csv -o macpf/3_hmmer/3_4_after_hmmer/3.6.3_macpf_statistics_all.xlsx
```

### 