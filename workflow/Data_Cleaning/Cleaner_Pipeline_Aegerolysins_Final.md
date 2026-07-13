# Cevovod za Čiščenje Aegerolizinov

## DEPENDENCIES

in environment.yml

## Data Acquisition

1. Pridobimo podatke MACPF
   1. Search by keywords, prenesi csv, protein fasta, transcript fasta, genomic fasta
   2. struktura mape:
      - Datoteke prenesi znotraj podmape macpf/keywords
      - datoteko vsako prenesi v podmapo poimenovano glede na keyword
      - datoteke poimenuj: keyword_tip, npr: pleurotolysin_protein.gz etc.

## IMENA:

SAMPLE.STEP_NUMBER.DESCRIPTION.EXTENSION
Ukaze poganjamo iz direktorija **results/cleaning**

# Data Cleaning

### 1.1. Cleaning FASTA headers

- Na tej točki imamo v fasta datoteki s proteini v imenu posameznega proteina, t.i. fasta headerju še veliko nepotrebnih podatkov, ki se jih moramo znebiti.

```
input: FASTA datoteka s sekvencami vseh proteinov: "pf06355.fasta"
output: FASTA datoteka s sekvencami vseh proteinov z ID namesto celotnega imena: "1.1_cleaned_ids.fasta"
```

```bash
mkdir aegerolysins/1_cleaned
# Keep only ids in fasta headers
seqkit seq -i ../../data/aegerolysins/keywords/pf06355/pf06355_protein.fasta > aegerolysins/1_cleaned/1.1_only_ids.fasta

# Save id-only headers
seqkit seq -n aegerolysins/1_cleaned/1.1_only_ids.fasta > aegerolysins/1_cleaned/1.1_only_ids_headers.txt

# Clean ids: Swap invalid characters (/) with "_"

seqkit replace -p "[ /]" -r "_" aegerolysins/1_cleaned/1.1_only_ids.fasta > aegerolysins/1_cleaned/1.1_cleaned_ids.fasta

# Save swapped headers

seqkit seq -n aegerolysins/1_cleaned/1.1_cleaned_ids.fasta > aegerolysins/1_cleaned/1.1_cleaned_ids_headers.txt
```

#### 1.1.1. Statistika

- Pridobimo statistiko po čiščenju FASTA headerjev.

```
input: FASTA z združenimi aegerolizini, samo id-ji: 1.1_cleaned_ids.fasta
output: datoteka z statistiko o tem, koliko je macpfov združenih, pred odstranjevanjem glede na ID: 1.1.1_cleaned_headers_stats.tsv
```

```bash
# Directory management
mkdir aegerolysins/seqkit_stats

seqkit stats -a -T aegerolysins/1_cleaned/1.1_cleaned_ids.fasta > aegerolysins/seqkit_stats/1.1.1_cleaned_headers_stats.tsv
```

#### 1.2.1 Cleaning CSV file

Ker smo zamenjali vse nedovoljene znake z podčrtajom, moramo enako storiti tudi v csv datoteki.

```bash
sed 's|/|_|g' ../../data/aegerolysins/keywords/pf06355/pf06355_csv.csv > aegerolysins/1_cleaned/1.2.1_cleaned_ids_csv.csv
```



## 2. Odstranjevanje imenskih duplikatov

- Preverimo, ali je med sekvencami kakšen imenski duplikat.

### 2.1. Odstranjevanje imenskih duplikatov iz fasta datoteke

- Imenski duplikati so proteini, ki imajo enako ime in posledično tudi enako sekvenco.

```
input: FASTA datoteka aegerolizinov z ID-ji - "1.4_protein_ids_combined.fasta"
output: 
	- Datoteka s seznamom in številom posameznih imenskih duplikatov - "2.1_1_aegerolysin_protein_namedupes.txt"
	- FASTA datoteka z imenskimi duplikati - "2.1_2_aegerolysin_protein_namedupes.fasta"
	- FASTA datoteka z odstranjenimi imenskimi duplikati - "2.1_3_aegerolysin_protein_nonamedupes.fasta"
```

```bash
# Directory management
mkdir aegerolysins/2_name_copies

# Removing duplicates
seqkit rmdup -n -D aegerolysins/2_name_copies/2.1_1_aegerolysin_protein_namedupes.txt -d aegerolysins/2_name_copies/2.1_2_aegerolysin_protein_namedupes.fasta aegerolysins/1_cleaned/1.1_cleaned_ids.fasta > aegerolysins/2_name_copies/2.1_3_aegerolysin_protein_nonamedupes.fasta
```

#### 2.1.1. Statistika

- Pridobimo statistiko FASTA datoteke po tem ko smo odstranili imenske duplikate

```
input: FASTA datoteka z odstranjenimi imenskimi duplikati: "2.1_3_macpf_protein_nonamedupes.fasta"
output: statistika porteinov brez imenskih duplikatov:      "2.1.1_macpf_protein_nonamedupes_stats.tsv"
```

```bash
seqkit stats -a -T aegerolysins/2_name_copies/2.1_3_aegerolysin_protein_nonamedupes.fasta > aegerolysins/seqkit_stats/2.1.1_aegero_protein_nonamedupes_stats.tsv
```



### 2.2. Odstranjevanje imenskih duplikatov iz CSV datoteke:

```
input: Prečišččena datoteka CSV z metapodatki: "1.2.1_cleaned_ids_csv.csv"
output: Prečiščena datoteka CSV z metapodatki brez imenskih duplikatov: "2.2_macpf_nonamedupes.csv"
```

```bash
# Running duplicate_cleaner_csv script
python ../../scripts/csv_utils/csv_cleaner.py -i aegerolysins/1_cleaned/1.2.1_cleaned_ids_csv.csv -o aegerolysins/2_name_copies/2.2_aegerolysins_nonamedupes.csv

```

### 2.3 Checkpoint 

- Preverimo, ali je število proteinov v CSV datoteki enako številu proteinov v fasta datoteki

```bash
# Directory management
mkdir aegerolysins/logs

# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 aegerolysins/2_name_copies/2.2_aegerolysins_nonamedupes.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > aegerolysins/logs/2.3_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(cat aegerolysins/seqkit_stats/2.1.1_aegero_protein_nonamedupes_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> aegerolysins/logs/2.3_log.txt

cat aegerolysins/logs/2.3_log.txt
```

## 3. HMMER

- S pomočjo HMMER programske opreme poiščemo vse proteinske domene, ki se pojavljajo na našem naboru proteinov, in odstranimo tiste, ki ne vsebujejo aegerolizinske domene.

### 3.1. Poženemo HMMER skripto

```
input: FASTA datoteka z odstranjenimi imenskimi duplikati: "2.1_3_aegerolysin_protein_nonamedupes.fasta"
ouptut: 
/hmmer/hmmer_results/ - rezultati zadetkov v json formatu za posamezen protein

3_hmmer/proteins.txt - datoteka s podatki o tem, kateri proteini so se obdelali
3_hmmer/not_processed.txt - datoteka s proteini, ki se niso procesirali
3_hmmer/no_domains.txt - datoteka s proteini, na katerih ni bilo zaznane nobene domene.
```

```bash
# Directory management
mkdir aegerolysins/3_hmmer
cd aegerolysins/3_hmmer

python ../../../../scripts/HMMER_API/hmmer_api_v4.py -seq ../2_name_copies/2.1_3_aegerolysin_protein_nonamedupes.fasta
```

### 3.2 Pridobimo poročilo o zadetkih

- Pregledamo datoteke json  z rezultati o zadetkih na našem naboru proteinov in izdelamo poročilo z začetkom in koncem ujemanja posamezne proteinske domene z našim proteinom, ter PFAM identifikacijskimi številkami.

```
input: Datoteka sama poišče JSON datoteke o zadetkih v podmapi /hmmer_results/
output: "aegerolysin_containing_proteins.csv" - proteini, ki imajo aegerolizinsko domeno
	- "macpf_containing_proteins.csv" - proteini, ki imajo macpf domeno
	- "significant_hits_remport.xlsx" - poročilo o signifikantnih zadetkih
    - "empty_proteins.xlsx" - seznam proteinov, na katerih HMMER ni našel nobenih domen.
```

```bash
# Executing script
python3 ../../../../scripts/HMMER_api_json_to_tab/json_to_tab.py --dir hmmer_results/
```

### 3.4. Izločimo proteine, ki nimajo aegerolizinske domene

- Ta korak ni striktno nujen, saj vsebujejo vsi proteini, ki smo jih prenesli s pomočjo pfam številke aegerolizinsko domeno, vendar ga lahko vseeno izvedemo, za vsak slučaj.

#### 3.4.1. Izločanje iz FASTA datoteke

- S pomočjo HMMER rezultatov izločimo iz FASTA datoteke proteine, ki nimajo aegerolizinskih domen
  - HMMER skripta nam vrne

```
input: "aegerolysin_containing_proteins.csv"
output:
FASTA datoteka aegerolizin vsebujočih proteinov: "3.4.1_after_hmmer.fastaa"
Statistika za aegerolysin vsebujoče proteine: "3.4.2_aegerolysins_after_hmmer.tsv
FASTA datoteka z ne-aegerolizin vsebujočimi proteini: "3.4.3_aegerolysin_non_containing.fasta"
Statitika izločenih proteinov: "3.4.3_aegero_non_containing.tsv"
```

```bash
# Directory management
cd ../..
mkdir aegerolysins/3_hmmer/3_4_after_hmmer

# Getting aegerolysin-containig proteins
seqkit grep -f aegerolysins/3_hmmer/aegerolysin_containing_proteins.csv aegerolysins/2_name_copies/2.1_3_aegerolysin_protein_nonamedupes.fasta > aegerolysins/3_hmmer/3_4_after_hmmer/3.4.1_after_hmmer.fasta
```

#### 3.4.2 Statistika aegerolizin-vsebujočih

```bash
# Obtaining statistics for aegeroliysin-containg proteins
seqkit stats --all --tabular aegerolysins/3_hmmer/3_4_after_hmmer/3.4.1_after_hmmer.fasta > aegerolysins/seqkit_stats/3.4.2_aegerolysins_after_hmmer.tsv
```

#### 3.4.3 Pridobivanje ne-aegerolizin vsebujočih proteinov

```bash
# Keeping non-macpf containing proteins
seqkit grep --invert-match --pattern-file aegerolysins/3_hmmer/aegerolysin_containing_proteins.csv aegerolysins/2_name_copies/2.1_3_aegerolysin_protein_nonamedupes.fasta > aegerolysins/3_hmmer/3_4_after_hmmer/3.4.3_aegerolysin_non_containing.fasta
```

#### 3.4.4. Statistika ne-MACPF vsebujočih

```bash
seqkit stats --all --tabular aegerolysins/3_hmmer/3_4_after_hmmer/3.4.3_aegerolysin_non_containing.fasta > aegerolysins/seqkit_stats/3.4.3_aegero_non_containing.tsv
```

#### 3.4.5. Izločanje iz CSV datoteke

- Iz datoteke z metapodakti naših proteinov moramo izločiti tiste, ki ne vsebujejo aegerolizinske domene.

```
input: CSV datoteka z odstranjenimi duplikati na ime "2.1_3_aegerolysin_protein_nonamedupes.fasta"
output: CSV datoteka z metapodatki samo za MACPF vsebujoče proteine: "3.4.5_aegero_after_hmmer.csv"
```

```bash
# Get first line from csv file
head -1 aegerolysins/2_name_copies/2.2_aegerolysins_nonamedupes.csv > aegerolysins/3_hmmer/3_4_after_hmmer/3.4.5_aegerolysins_after_hmmer.csv

# Get proteins with aegerolysin domain
grep --fixed-strings -f aegerolysins/3_hmmer/aegerolysin_containing_proteins.csv aegerolysins/2_name_copies/2.2_aegerolysins_nonamedupes.csv >> aegerolysins/3_hmmer/3_4_after_hmmer/3.4.5_aegerolysins_after_hmmer.csv 
```

### 3.5. Checkpoint

Preverimo, ali se po odstranjevanju aegerolizin nevsebujočih proteinov iz datoteke z metapodatki ujema s številom proteinov v FASTA datoteki.

```bash
# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 aegerolysins/3_hmmer/3_4_after_hmmer/3.4.5_aegerolysins_after_hmmer.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${n
um_seqs}" > aegerolysins/logs/3.5_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(cat aegerolysins/seqkit_stats/3.4.2_aegerolysins_after_hmmer.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_fasta: ${
num_seqs}" >> aegerolysins/logs/3.5_log.txt

cat aegerolysins/logs/3.5_log.txt
```

### 3.6. Pridobimo statistiko proteinov, ki vsebujejo aegerolizinsko domeno.

TODO: Premakni ta del 3.6. v dokument z analizo. Enako za MACPF

- Ker nas zanima, kakšna je razporeditev 
- Na tej točki imamo vse proteine, ki so realni MACPF proteini - nekaj izmed njih je duplikatov, nekaj pa je takih, ki jih zaradi politike uporabe podatkov JGI ne smemo uporabiti

#### 3.6.1. Pridobimo filogenijo za aegerolizin-vsebujoče proteine

**Pomembno, vhodna datoteka s filogenijo (se nahaja za -i zastavico) mora vsebovati informacije o filogeniji za celotno Basidiomycota deblo**

```bash
mkdir basidiomycota_phylogeny

# Perform phylogeny lookup on NCBI
python3 ../../scripts/NCBI_taxonomy/taxonomy_v7_pandas_gemini.py -i ../../data/basidiomycota_for_taxonomy.txt -o ../cleaning/basidiomycota_phylogeny/basidiomycota_taxonomy.csv
```

#### 3.6.3. Pridobimo statistiko

```
input:
Datoteka z metapodatki in filogenijo: "final_macpf_with_phylogeny.csv"
Datoteka s filogenijo za celotno izbrano taksonomsko enoto: \phylogeny.csv
output: Excel datoteka s poročilom o statistiki: "sumary_counts.xlsx"
```

```bash
# Run script that obtains statistics
python3 ../../scripts/stat/stat_v2.py -m macpf/3_hmmer/3_4_after_hmmer/3.4.5_macpf_after_hmmer.csv -p basidiomycota_phylogeny/basidiomycota_taxonomy.csv -o macpf/3_hmmer/3_4_after_hmmer/3.6.3_macpf_statistics_all.xlsx
```

### 4 Odstranimo nedovoljene proteine

- Če imamo med organizmi, ki vsebujejo aegerolizine tudi takšne, ki še niso bili objavljeni, moramo najprej pri avtorjih vprašati za dovoljenje.
- Ko pridobimo dovoljenja, pripravimo datoteko `not_allowed.txt`, v kateri so **celotna imena** tistih organizmov, ki jih ne smemo uporabljati.

#### 4.1. Odstranjevanje iz CSV datoteke

```
input: 
Datoteka TXT s seznamom genomov, ki jih ne smemo uporabiti: not_allowed.txt
Datoteka CSV 
output: SV datoteka z metapodatki samo za MACPF vsebujoče proteine: after_hmmer_metadata_macpf.csv
```

```bash
# Directory management
mkdir aegerolysins/4_permitted

# Grab the fist line from CSV file
head -1 aegerolysins/3_hmmer/3_4_after_hmmer/3.4.5_aegerolysins_after_hmmer.csv > aegerolysins/4_permitted/4.1_aegerolysins_permitted_metadata.csv


# From the csv file after hmmer, grab only the lines that are not in the not_allowed.txt file
grep --invert-match --fixed-strings -f ../../data/permissions/not_allowed.txt aegerolysins/3_hmmer/3_4_after_hmmer/3.4.5_aegerolysins_after_hmmer.csv >> aegerolysins/4_permitted/4.1_aegerolysins_permitted_metadata.csv

# Get metadata for the non-permitted proteins - aids in logging number of removed proteins downstream
grep --fixed-strings -f ../../data/permissions/not_allowed.txt aegerolysins/3_hmmer/3_4_after_hmmer/3.4.5_aegerolysins_after_hmmer.csv >> aegerolysins
/4_permitted/4.1_aegerolysins_forbidden_metadata.csv

```



##### 4.1.2: LOG

- Število sekvenc, ki smo jih obdržali, in število sekvenc, ki jih nismo smeli obdržati, zapišemo v datoteko

```bash
# Get and write number of kept sequences into the log file.
permitted_num=$(csvtk nrow aegerolysins/4_permitted/4.1_aegerolysins_permitted_metadata.csv); echo "num_of_permitted_sequences: ${permitted_num}" >> aegerolysins/logs/4.1.2_log.txt

# Get and write number of removed sequences into the log file
forbidden_num=$(csvtk nrow -H aegerolysins/4_permitted/4.1_aegerolysins_forbidden_metadata.csv); echo "num_of_forbidden(removed)_sequences: ${forbidden_num}" >> aegerolysins/logs/4.1.2_log.txt


```



#### 4.2. Odstranjevanje iz FASTA datoteke

```
input:
output:
```

```bash
# Preparing the headers for seqkit
csvtk cut -U -f  fasta_header aegerolysins/4_permitted/4.1_aegerolysins_permitted_metadata.csv > aegerolysins/4_permitted/4.2_aegerolysins_permitted_headers.txt


# Fetching only the permitted proteins
seqkit grep -f aegerolysins/4_permitted/4.2_aegerolysins_permitted_headers.txt aegerolysins/3_hmmer/3_4_after_hmmer/3.4.1_after_hmmer.fasta > aegerolysins/4_permitted/4.2_aegerolysins_permitted.fasta
## Nekateri proteini se tukaj izmuznejo. Porpravljeno ročno - predvsem tisti, ki imajo whitespace v imenu.

```

```
# BUG Nekateri proteini se v tem koraku izmuznejo - mislim da predvsem tisti, ki imajo whitespace v imenu. Glej  korak 1.1.
```

#### 4.3. Pridobivanje statistike

##### 4.3.1. Pridobivanje statistike proteinov po odstranjevanju nedovoljenih proteinov.

```bash
seqkit stats --all --tabular aegerolysins/4_permitted/4.2_aegerolysins_permitted.fasta > aegerolysins/seqkit_stats/4.3.1_aegerolysins_permitted_stats.tsv
```

##### 4.3.2. Checkpoint

Preverimo ali je število sekvenc v fasta datoteki po odstranjevanju nedovoljenih proteinov enako številu sekvenc v csv datoteki po odstranjevanju dovoljenih proteinov.

```bash
# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 aegerolysins/4_permitted/4.1_aegerolysins_permitted_metadata.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > aegerolysins/logs/4.3.2_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(cat aegerolysins/seqkit_stats/4.3.1_aegerolysins_permitted_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> aegerolysins/logs/4.3.2_log.txt

cat aegerolysins/logs/4.3.2_log.txt
```

##### 4.3.2. Pridobivanje izgubljenih proteinov in statistiko izgubljenih proteinov

```
input:
output:
```

```bash
# Get non-permitted proteins
seqkit grep --invert-match -f aegerolysins/4_permitted/4.2_aegerolysins_permitted_headers.txt aegerolysins/3_hmmer/3_4_after_hmmer/3.4.1_after_hmmer.fasta > aegerolysins/4_permitted/4.3.2_aegerolysins_non_permitted.fasta

# Get statistics for non-permitted proteins
seqkit stats --all --tabular aegerolysins/4_permitted/4.3.2_aegerolysins_non_permitted.fasta > aegerolysins/seqkit_stats/4.3.2_aegerolysins_non_permitted_stats.tsv

```

##### 4.3.3. Checkpoint

Preverimo, ali je število nedovoljenih proteinov + število dovoljenih proteinov enako številu pred izločanjem glede na dovoljenje

```bash
# Get number of sequences in fasta file before permission removal
num_seqs_before=$(cat aegerolysins/seqkit_stats/3.4.2_aegerolysins_after_hmmer.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_before
_permission: ${num_seqs_before}"  > aegerolysins/logs/4.3.3_log.txt

# Get number of sequences in fasta file that are permitted to be used
num_seqs_permitted=$(cat macpf/seqkit_stats/4.3.1_macpf_permitted_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_permitted: ${num_seqs_permitted}" >> macpf/logs/4.3.3_log.txt

# Get number of sequences that are not allwed
num_seqs_permitted=$(cat aegerolysins/seqkit_stats/4.3.1_aegerolysins_permitted_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs
_permitted: ${num_seqs_permitted}" >> aegerolysins/logs/4.3.3_log.txt

cat aegerolysins/logs/4.3.3_log.txt

```

## 5. Odstranjevanje glede na sekvenco 

TODO od tukaj naprej - 12. 7. 2026

- Sedaj imamo končni seznam proteinov, vendar pa je nekaj takih proteinov, ki so si med sabo glede na sekvenco identični - odstranimo jih.

### 5.1. Odstranjevanje iz fasta datoteke

```
input:
output: 
Končna datoteka z macpf za nadalnje analize: macpf/final/final_macpf.fasta
Datoteka s številom in podatki sekvenčnih duplikatov: "duplicate_sequences_seq.txt"
FASTA datoteka s sekvenčnimi duplikati: "duplicate_sequnces_seq.fasta"
```

```bash
# Directory management
mkdir macpf/5_seqdupes

# Remove sequence duplicates
seqkit rmdup -s -D macpf/5_seqdupes/5.1_duplicate_sequences_seq.txt -d macpf/5_seqdupes/5.1_duplicate_sequences_seq.fasta  macpf/4_permitted/4.2_macpf_permitted.fasta > macpf/5_seqdupes/5.1_macpf_noseqdupes.fasta
```

## 5.2. Odstranjevanje iz csv datoteke

input:
CSV datoteka z dovoljenimi proteini: "permitted_metadata_macpf.csv"
FASTA datoteka brez sekvenčnih duplikatov: "final_macpf.fasta"
output: CSV metadata datoteka brez sekvenčnih duplikatov: "final_macpf.csv"

```bash
# Get header
head -1 macpf/4_permitted/4.1_macpf_permitted_metadata.csv > macpf/5_seqdupes/5.2_macpf_noseqdupes_metadata.csv

# Get fasta headers from fasta file
seqkit seq -n macpf/5_seqdupes/5.1_macpf_noseqdupes.fasta > macpf/5_seqdupes/5.2_macpf_noseqdupes_headers.txt

grep -f macpf/5_seqdupes/5.2_macpf_noseqdupes_headers.txt macpf/4_permitted/4.1_macpf_permitted_metadata.csv >> macpf/5_seqdupes/5.2_macpf_noseqdupes_metadata.csv
```

#### 5.1. Statistika končnih in odstranjenih proteinov.

##### 5.1.1 Statistika odstranjenih proteinov

```
input: FASTA datoteka z duplikatnimi sekvencami: "duplicate_sequnces_seq.fasta"
output: TSV datoteka s statistiko o duplikatnih sekvencah "duplicate_seqs_seq.tsv"
```

```bash
# Get statistics of sequence duplicates
seqkit stats -a -T macpf/5_seqdupes/5.1_duplicate_sequences_seq.fasta > macpf/seqkit_stats/5.1.1_macpf_seqdups_stats.tsv

```

##### 5.1.2. Statistika končnih proteinov

```
input: FASTA datoteka končna: "final_macpf.fasta"
output: statistika končna: "seqkit_stats_final.tsv"
```

```
seqkit stats -a -T macpf/5_seqdupes/5.1_macpf_noseqdupes.fasta > macpf/seqkit_stats/5.1.2_macpf_noseqdupes_s
tats.tsv
```

##### 5.1.3. Checkpoint

```bash
# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 macpf/5_seqdupes/5.2_macpf_noseqdupes_metadata.csv | cut -d "," -f 2 | wc -l); echo "n
um_sequences_csv: ${num_seqs}" > macpf/logs/5.1.3_log.txt


# Exporting number of sequences in seqkit stats file
num_seqs=$(cat macpf/seqkit_stats/5.1.2_macpf_noseqdupes_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-
header); echo "num_seqs_fasta: ${num_seqs}" >> macpf/logs/5.1.3_log.txt

cat macpf/logs/5.1.3_log.txt
```

### 5.3 Statistika končna

Pridobimo statistiko vsebnosti proteinov

```bash
python3 ../../scripts/stat/stat_v2.py -m macpf/5_seqdupes/5.2_macpf_noseqdupes_metadata.csv -p basidiomycota_phylogeny/basidiomycota_taxonomy.csv -o macpf/5_seqdupes/5.3_macpf_noseqdupes_statistics.xlsx 
```

## 5.4 združimo datoteko z metapodatki in filogenijo za lažje delo pri uvažanju podatkov v TreeViewer. PRESTAVI ČISTO NA KONEC

```bash
python3 ~/Development/NCBI_taxonomy/helpers/csv_merger/metadata_merger.py -p basidiomycota_phylogeny/basidiomycota_taxonomy.csv -m macpf/5_final/5.2_macpf_final_metadata.csv -o macpf/5_final/5.3_macpf_final_metadata_phylogeny.csv
```

## 6. Dodajanje Pleurotus pulmunarius

### 6.1. Dodajanje fasta sekvence pul b: odstranjevanje ID-ja in dodajanje k datotekam brez duplikatnih sekvenc iz prejšnjega koraka.

```bash
mkdir macpf/6_pleurotus_pulmonarius

# Kopiramo datoteke očiščenih in dedupliciranih proteinov ter preimenujemo
cp macpf/5_seqdupes/5.1_macpf_noseqdupes.fasta macpf/6_pleurotus_pulmunarius/6.1_macpfs_pul_b.fasta

# Očištimo sekvenco pul_b (ohranimo samo ID) in dodamo k ostalim sekvencam.
seqkit seq -i ../../data/pleurotus_pulmonarius_ncbi/pul_b/pul_b_protein.fasta >> macpf/6_pleurotus_pulmunarius/6.1_macpfs_pul_b.fasta

```

#### 6.1.1 Statistika

```
seqkit stats -a -T macpf/6_pleurotus_pulmunarius/6.1_macpfs_pul_b.fasta > macpf/seqkit_stats/6.1.1_macpf_pul_b_stats.tsv
```

#### 6.1.2 Checkpoint

Preverimo, ali je sedaj v novi fasta datoteki ena sekvenca več, kot je bila na koncu koraka 5.

```bash
# Get stats for file with deduplicated sequences
num_seqs=$(cat macpf/seqkit_stats/5.1.2_macpf_noseqdupes_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_fasta_deudplicated: ${num_seqs}" >> macpf/logs/6.1.2_log.txt

# Get stats after adding plu_b
num_seqs=$(cat macpf/seqkit_stats/6.1.1_macpf_pul_b_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_fasta_with_plu_b: ${num_seqs}" >> macpf/logs/6.1.2_log.txt

cat macpf/logs/6.1.2_log.txt
```

### 6.2. Ustvarjanje datoteke z metapodatki za pul b.

- Ta korak sem naredil ročno s pomočjo Excela. V datoteko sem dodal samo tiste podatke, ki so nujno potrebni za izdelavo proteinskega drevesa.

Najprej pridobimo glavo csv datoteke iz prejšnjih korakov, za namen poenotenja strukturiranja podatkov:

```
# Get header row
head -1 macpf/5_seqdupes/5.2_macpf_noseqdupes_metadata.csv > macpf/6_pleurotus_pulmunarius/6.2_pul_b_metadata.csv
```

- Nato odpremo v poljubnem urejevalniku csv datotek in dodamo fasta header ter ime organizma.
- Fasta header prekopiramo iz konca datoteke `"6.1_macpfs_pul_b.fasta"`
- Organism ID je skrajšana verzija imena - Plepul1
- organism name je celotno ime vrste, enako velja za "Genus species", najdemo v originalni fasta datoteki, prenešeni iz NCBI, v oglatih oklepajih `"pul_b_protein.fasta"`
- Name vzamemo iz _summary datoteke - `"pul_summary.txt"`
- protein_id pa je enak kot pri shranjevanju (pul_b)

### 6.3 Pridobivanje HMMER za protein

```bash
# Znotraj direktorija 6_pleurotus_pulmunarius
cd macpf/6_pleurotus_pulmunarius/

# Poženemo hmmer skripto
python3 ../../../../scripts/HMMER_API/hmmer_api_v4.py -seq ../../../../data/pleurotus_pulmonarius_ncbi/pul_b/pul_b_protein.fasta

# Pridobimo statistiko za HMMER
python3 ../../../../scripts/HMMER_api_json_to_tab/json_to_tab.py -dir hmmer_results/

# Pridobimo sliko
python3 ../../../../scripts/hmmer_features/features.py hmmer_results/KAF4577132.1_hmmerrez.json 6.3.1_pul_b_svg.svg
```

### 6.4. Pridobivanje filogenije

```
# Pripravljanje datoteke za pridobivanje 
echo "Pleurotus pulmonarius" > for_phylogeny.txt

# Lookup phylogeny with script
python3 ../../../../scripts/NCBI_taxonomy/taxonomy_v7_pandas_gemini.py -i for_phylogeny.txt -o pleurotus_pulmonarius_phlogeny.csv

```

### 6.5 Združevanje metapodatkov v eno datoteko

Korak nam olajša delo pri upodabljanju drevesa s pomočjo programa TreeViewer.

```bash
# Create temporary directory for metadata
mkdir macpf/6_pleurotus_pulmunarius/6.5_combined_metadata/

# Copy metadata to temporary directory
cp macpf/5_seqdupes/5.2_macpf_noseqdupes_metadata.csv macpf/6_pleurotus_pulmunarius/6.5_combined_metadata/
cp macpf/6_pleurotus_pulmunarius/6.2_pul_b_metadata.csv macpf/6_pleurotus_pulmunarius/6.5_combined_metadata/

# Merging the metadata files
awk 'FNR==1 && NR!=1{next;}{print}' macpf/6_pleurotus_pulmunarius/6.5_combined_metadata/*csv > macpf/6_pleurotus_pulmunarius/6.5_macpf_noseqdupes_pulb.csv

# Remove temporary directory
rm -r 6.5_macpf_noseqdupes_pulb.csv
```

#### 6.5.2. Checkpoint

Preverimo, ali je število sekvenc v csv datoteki enako številu sekvenc v fasta datoteki.

```bash
# Preparing log directory
mkdir macpf/logs

# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 macpf/6_pleurotus_pulmunarius/6.5_macpf_noseqdupes_pulb.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > macpf/logs/6.5.2_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(cat macpf/seqkit_stats/6.1.1_macpf_pul_b_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> macpf/logs/6.5.2_log.txt 

cat macpf/logs/6.5.2_log.txt

```

## . HMMER slike

```bash
# Create directory for macpf containing proteins.
mkdir macpf/5_final/5.5_macpf_contianing_hmmer_results

for f in $(cat macpf/5_final/5.2_macpf_final_headers.txt); do find macpf/3_hmmer/hmmer_results/ -type f -name "${f}.json" -exec cp {} macpf/5_final/5.5_macpf_contianing_hmmer_results/ \;; done

mkdir macpf/5_final/5.6_slike

for file in $(find macpf/5_final/5.5_macpf_contianing_hmmer_results/ -iname "*"); do base=$(basename $file .json); svg="${base}.svg"; python3 /home/crt/Development/hmmer_viz/features.py $file "macpf/3_hmmer/hmmer_svgs/${svg}"; done
```

## 7. Outgroups

### 7.1. Dodajanje outgroup genomov k sekvencam macpf in pleurotus pulmunarius

- Združimo torej outgroup sekvence skupaj s sekvencami, ki smo jih pridobili v koraku združevanja 6.1

```bash
mkdir results/cleaning/macpf/7_outgroups/

# Kopiranje združenih datotek iz koraka 6.1
cp results/cleaning/macpf/6_pleurotus_pulmunarius/6.1_macpfs_pul_b.fasta results/cleaning/macpf/7_outgroups/7.1_meged.fasta

# Prečiščevanje in dodajanje sekvenc pul_b
seqkit seq data/outgroups/nig_b.fasta >> results/cleaning/macpf/7_outgroups/7.1_meged.fasta 

```

### 7.2. Pridobivanje statistike

- Pridobimo statistiko novonastale fasta datoteke

#### 7.2.1. Statistika števila outgroup proteinov

- Preverimo, koliko outgroup proteinov bi naj dodali v novo datoteko.

```bash
seqkit stats -a -T data/outgroups/nig_b.fasta >> results/cleaning/macpf/seqkit_stats/7.2.1_outgroup_stats.tsv
```

#### 7.2.2. Statistika števila proteinov po združevanju s sekvencami iz prejšnjih korakov.

```bash
seqkit stats -a -T results/cleaning/macpf/7_outgroups/7.1_meged.fasta >> results/cleaning/macpf/seqkit_stats/7.2.2_outgroups_added_stats.tsv
```

7.2.3 Preverimo, ali je sedaj število sekvenc po dodatku outgroupov za število outgroup sekvenc večje od števila sekvenc v datoteki iz koraka 6.1. po združevanju s sekvencami _Pleurotus pulmunarius_

```bash
# Check number of sequences before adding outgroups
num_seqs=$(cat results/cleaning/macpf/seqkit_stats/6.1.1_macpf_pul_b_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_before_outgroups: ${num_seqs}" >> results/cleaning/macpf/logs/7.2.3_log.txt


# Check number of sequences of outgroups
num_seqs=$(cat results/cleaning/macpf/seqkit_stats/7.2.1_outgroup_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_outgrou`ps: ${num_seqs}" >> results/cleaning/macpf/logs/7.2.3_log.txt

# Check number of sequences after adding outgroups
num_seqs=$(cat results/cleaning/macpf/seqkit_stats/7.2.2_outgroups_added_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_added_outgroups: ${num_seqs}" >> results/cleaning/macpf/logs/7.2.3_log.txt

# See log
cat results/cleaning/macpf/logs/7.2.3_log.txt
```

### 7.3. Dodamo metapodatke

- Ta korak sem naredil ročno s pomočjo Excela. V datoteko sem dodal samo tiste podatke, ki so nujno potrebni za izdelavo proteinskega drevesa.

Najprej pridobimo glavo csv datoteke iz prejšnjih korakov, za namen poenotenja strukturiranja podatkov:

```
# Get header row
head -1 macpf/5_seqdupes/5.2_macpf_noseqdupes_metadata.csv > macpf/?_pleurotus_pulmunarius/?_pul_b_metadata.csv
```

- Nato odpremo v poljubnem urejevalniku csv datotek in dodamo fasta header ter ime organizma.
- Fasta header prekopiramo iz konca datoteke `"6.1_macpfs_pul_b.fasta"`
- Organism ID je skrajšana verzija imena - Plepul1
- organism name je celotno ime vrste, enako velja za "Genus species", najdemo v originalni fasta datoteki, prenešeni iz NCBI, v oglatih oklepajih `"pul_b_protein.fasta"`
- Name vzamemo iz _summary datoteke - `"pul_summary.txt"`
- protei

## References
