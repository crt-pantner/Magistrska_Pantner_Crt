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

```bash
mkdir -p aegerolysins/1_cleaned
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

```bash
# Directory management
mkdir -p aegerolysins/seqkit_stats

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

```bash
# Directory management
mkdir -p aegerolysincat  | s/2_name_copies

# Removing duplicates
seqkit rmdup -n -D aegerolysins/2_name_copies/2.1_1_aegerolysin_protein_namedupes.txt -d aegerolysins/2_name_copies/2.1_2_aegerolysin_protein_namedupes.fasta aegerolysins/1_cleaned/1.1_cleaned_ids.fasta > aegerolysins/2_name_copies/2.1_3_aegerolysin_protein_nonamedupes.fasta
```

#### 2.1.1. Statistika

- Pridobimo statistiko FASTA datoteke po tem ko smo odstranili imenske duplikate

```bash
seqkit stats -a -T aegerolysins/2_name_copies/2.1_3_aegerolysin_protein_nonamedupes.fasta > aegerolysins/seqkit_stats/2.1.1_aegero_protein_nonamedupes_stats.tsv
```



### 2.2. Odstranjevanje imenskih duplikatov iz CSV datoteke:

```bash
# Running duplicate_cleaner_csv script
python ../../scripts/csv_utils/csv_cleaner.py -i aegerolysins/1_cleaned/1.2.1_cleaned_ids_csv.csv -o aegerolysins/2_name_copies/2.2_aegerolysins_nonamedupes.csv

```

### 2.3 Checkpoint 

- Preverimo, ali je število proteinov v CSV datoteki enako številu proteinov v fasta datoteki

```bash
# Directory management
mkdir -p aegerolysins/logs

# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 aegerolysins/2_name_copies/2.2_aegerolysins_nonamedupes.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > aegerolysins/logs/2.3_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/2.1.1_aegero_protein_nonamedupes_stats.tsv | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> aegerolysins/logs/2.3_log.txt

cat aegerolysins/logs/2.3_log.txt
```

## 3. HMMER

- S pomočjo HMMER programske opreme poiščemo vse proteinske domene, ki se pojavljajo na našem naboru proteinov, in odstranimo tiste, ki ne vsebujejo aegerolizinske domene.

### 3.1. Poženemo HMMER skripto

```bash
# Directory management
mkdir -p aegerolysins/3_hmmer
cd aegerolysins/3_hmmer

python ../../../../scripts/HMMER_API/hmmer_api_v4.py -seq ../2_name_copies/2.1_3_aegerolysin_protein_nonamedupes.fasta
```

### 3.2 Pridobimo poročilo o zadetkih

- Pregledamo datoteke json  z rezultati o zadetkih na našem naboru proteinov in izdelamo poročilo z začetkom in koncem ujemanja posamezne proteinske domene z našim proteinom, ter PFAM identifikacijskimi številkami.

```bash
# Executing script
python3 ../../../../scripts/HMMER_api_json_to_tab/json_to_tab.py --dir hmmer_results/
```

### 3.4. Izločimo proteine, ki nimajo aegerolizinske domene

- Ta korak ni striktno nujen, saj vsebujejo vsi proteini, ki smo jih prenesli s pomočjo pfam številke aegerolizinsko domeno, vendar ga lahko vseeno izvedemo, za vsak slučaj.

#### 3.4.1. Izločanje iz FASTA datoteke

- S pomočjo HMMER rezultatov izločimo iz FASTA datoteke proteine, ki nimajo aegerolizinskih domen
  - HMMER skripta nam vrne

```bash
# Directory management
cd ../..
mkdir -p aegerolysins/3_hmmer/3_4_after_hmmer

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
num_seqs=$(tail -n +2 aegerolysins/3_hmmer/3_4_after_hmmer/3.4.5_aegerolysins_after_hmmer.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > aegerolysins/logs/3.5_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/3.4.2_aegerolysins_after_hmmer.tsv | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> aegerolysins/logs/3.5_log.txt

cat aegerolysins/logs/3.5_log.txt
```

### 3.6. Pridobimo statistiko proteinov, ki vsebujejo aegerolizinsko domeno.

TODO: Premakni ta del 3.6. v dokument z analizo. Enako za MACPF

- Ker nas zanima, kakšna je razporeditev 
- Na tej točki imamo vse proteine, ki so realni MACPF proteini - nekaj izmed njih je duplikatov, nekaj pa je takih, ki jih zaradi politike uporabe podatkov JGI ne smemo uporabiti

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

### 4 Odstranimo nedovoljene proteine

- Če imamo med organizmi, ki vsebujejo aegerolizine tudi takšne, ki še niso bili objavljeni, moramo najprej pri avtorjih vprašati za dovoljenje.
- Ko pridobimo dovoljenja, pripravimo datoteko `not_allowed.txt`, v kateri so **celotna imena** tistih organizmov, ki jih ne smemo uporabljati.

#### 4.1. Odstranjevanje iz CSV datoteke

```bash
# Directory management
mkdir -p aegerolysins/4_permitted

# Grab the fist line from CSV file
head -1 aegerolysins/3_hmmer/3_4_after_hmmer/3.4.5_aegerolysins_after_hmmer.csv > aegerolysins/4_permitted/4.1_aegerolysins_permitted_metadata.csv

# From the csv file after hmmer, grab only the lines that are not in the not_allowed.txt file
grep --invert-match --fixed-strings -f ../../data/permissions/not_allowed.txt aegerolysins/3_hmmer/3_4_after_hmmer/3.4.5_aegerolysins_after_hmmer.csv >> aegerolysins/4_permitted/4.1_aegerolysins_permitted_metadata.csv

# Get metadata for the non-permitted proteins - aids in logging number of removed proteins downstream
grep --fixed-strings -f ../../data/permissions/not_allowed.txt aegerolysins/3_hmmer/3_4_after_hmmer/3.4.5_aegerolysins_after_hmmer.csv >> aegerolysins/4_permitted/4.1_aegerolysins_forbidden_metadata.csv

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
num_seqs=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/4.3.1_aegerolysins_permitted_stats.tsv | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> aegerolysins/logs/4.3.2_log.txt

cat aegerolysins/logs/4.3.2_log.txt
```

##### 4.3.2. Pridobivanje izgubljenih proteinov in statistiko izgubljenih proteinov

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
num_seqs_before=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/3.4.2_aegerolysins_after_hmmer.tsv | csvtk del-header); echo "num_seqs_before_permission: ${num_seqs_before}"  > aegerolysins/logs/4.3.3_log.txt

# TODO 21. 7. 2026 ob 20:09: popravi tole, tukaj notri so še neki macpf - napačna datoteka.
# Get number of sequences in fasta file that are permitted to be used
num_seqs_permitted=$(cat macpf/seqkit_stats/4.3.1_macpf_permitted_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_permitted: ${num_seqs_permitted}" >> aegerolysins/logs/4.3.3_log.txt

# Get number of sequences that are not allwed
num_seqs_permitted=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/4.3.1_aegerolysins_permitted_stats.tsv | csvtk del-header); echo "num_seqs_permitted: ${num_seqs_permitted}" >> aegerolysins/logs/4.3.3_log.txt

cat aegerolysins/logs/4.3.3_log.txt

```

## 5. Odstranjevanje glede na sekvenco 

- Sedaj imamo končni seznam proteinov, vendar pa je nekaj takih proteinov, ki so si med sabo glede na sekvenco identični - odstranimo jih.

### 5.1. Odstranjevanje iz fasta datoteke

```bash
# Directory management
mkdir -p aegerolysins/5_seqdupes

# Remove sequence duplicates
seqkit rmdup --dup-num-file aegerolysins/5_seqdupes/5.1_duplicate_sequences_counts.txt --dup-seqs-file aegerolysins/5_seqdupes/5.1_duplicate_sequences_seq.fasta aegerolysins/4_permitted/4.2_aegerolysins_permitted.fasta > aegerolysins/5_seqdupes/5.1_aegero_noseqdupes.fasta
```

## 5.2. Odstranjevanje iz csv datoteke

```bash
# Get header
head -1 aegerolysins/4_permitted/4.1_aegerolysins_permitted_metadata.csv > aegerolysins/5_seqdupes/5.2_aegerolysins_noseqdupes_metadata.csv

# Get fasta headers from fasta file
seqkit seq --name aegerolysins/5_seqdupes/5.1_aegero_noseqdupes.fasta > aegerolysins/5_seqdupes/5.2_aegerolysins_noseqdupes_headers.txt

grep -f aegerolysins/5_seqdupes/5.2_aegerolysins_noseqdupes_headers.txt aegerolysins/4_permitted/4.1_aegerolysins_permitted_metadata.csv >> aegerolysins/5_seqdupes/5.2_aegerolysins_noseqdupes_metadata.csv 
```

#### 5.1. Statistika končnih in odstranjenih proteinov.

##### 5.1.1 Statistika odstranjenih proteinov

```bash
# Get statistics of sequence duplicates
seqkit stats --all --tabular aegerolysins/5_seqdupes/5.1_duplicate_sequences_seq.fasta > aegerolysins/seqkit_stats/5.1.1_aegerolsyins_seqdups_stats.tsv

```

##### 5.1.2. Statistika končnih proteinov

```bash
seqkit stats --all --tabular aegerolysins/5_seqdupes/5.1_aegero_noseqdupes.fasta > aegerolysins/seqkit_stats/5.1.2_aegero_noseqdupes_stats.tsv
```

##### 5.1.3. Checkpoint

```bash
# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 aegerolysins/5_seqdupes/5.2_aegerolysins_noseqdupes_metadata.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > aegerolysins/logs/5.1.3_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/5.1.2_aegero_noseqdupes_stats.tsv | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> aegerolysins/logs/5.1.3_log.txt

cat aegerolysins/logs/5.1.3_log.txt
```

### 5.3 Statistika končna

Pridobimo statistiko vsebnosti proteinov

```bash
python ../../scripts/stat/stat_v2.py -m aegerolysins/5_seqdupes/5.2_aegerolysins_noseqdupes_metadata.csv -p basidiomycota_phylogeny/basidiomycota_taxonomy.csv -o aegerolysins/5_seqdupes/5.3_aegero_noseqdupes_statistics.xlsx
```

## 5.4 združimo datoteko z metapodatki in filogenijo za lažje delo pri uvažanju podatkov v TreeViewer. PRESTAVI ČISTO NA KONEC

```bash
python3 ~/Development/NCBI_taxonomy/helpers/csv_merger/metadata_merger.py -p basidiomycota_phylogeny/basidiomycota_taxonomy.csv -m macpf/5_final/5.2_macpf_final_metadata.csv -o macpf/5_final/5.3_macpf_final_metadata_phylogeny.csv
```

## 6. Dodajanje Pleurotus pulmunarius

Dodajanje fasta sekvence pul b: odstranjevanje ID-ja in dodajanje k datotekam brez duplikatnih sekvenc iz prejšnjega koraka.

```bash
mkdir -p aegerolysins/6_pleurotus_pulmonarius

# Kopiramo datoteke očiščenih in dedupliciranih proteinov ter preimenujemo
cp aegerolysins/5_seqdupes/5.1_aegero_noseqdupes.fasta aegerolysins/6_pleurotus_pulmonarius/6.1_aegero_nodupes_pul.fasta

# Kopiramo vse sekvence za pul a in jih shranimo v eno datoteko
for file in $(find ../../data/pleurotus_pulmonarius_ncbi/* -iname "pul_a*.fasta"); do seqkit seq -i $file >> aegerolysins/6_pleurotus_pulmonarius/pul_a_seqs.fasta; done

# Dodamo združene pul a sekvence k dedupliciranim sekvencam
seqkit seq aegerolysins/6_pleurotus_pulmonarius/pul_a_seqs.fasta >> aegerolysins/6_pleurotus_pulmonarius/6.1_aegero_nodupes_pula.fasta
```

#### 6.1.1 Statistika

```bash
seqkit stats --all --tabular aegerolysins/6_pleurotus_pulmonarius/6.1_aegero_nodupes_pula.fasta > aegerolysins/seqkit_stats/6.1.1_aegero_pul_a_stats.tsv
```

#### 6.1.2 Checkpoint

Preverimo, ali je sedaj v novi fasta datoteki ena sekvenca več, kot je bila na koncu koraka 5.

```bash
# Get stats for file with deduplicated sequences
num_seqs=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/5.1.2_aegero_noseqdupes_stats.tsv | csvtk del-header); echo "num_seqs_fasta_deudplicated: ${num_seqs}" >> aegerolysins/logs/6.1.2_log.txt

num_seqs=$(seqkit stats --all --tabular aegerolysins/6_pleurotus_pulmonarius/pul_a_seqs.fasta | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_of_pul_a_seqs: ${num_seqs}" >> aegerolysins/logs/6.1.2_log.txt

# Get stats after adding plu_a
num_seqs=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/6.1.1_aegero_pul_a_stats.tsv | csvtk del-header); echo "num_seqs_fasta_with_pul_a_prots: ${num_seqs}" >> aegerolysins/logs/6.1.2_log.txt

cat aegerolysins/logs/6.1.2_log.txt
```

### 6.2. Ustvarjanje datoteke z metapodatki za pul a-je 

- Ta korak sem naredil ročno s pomočjo Excela. V datoteko sem dodal samo tiste podatke, ki so nujno potrebni za izdelavo proteinskega drevesa.

Najprej pridobimo glavo csv datoteke iz prejšnjih korakov, za namen poenotenja strukturiranja podatkov:

```
# Get header row
head -1 aegerolysins/5_seqdupes/5.2_aegerolysins_noseqdupes_metadata.csv > aegerolysins/6_pleurotus_pulmonarius/6.2_pul_a_metadata.csv
```

- Nato odpremo v poljubnem urejevalniku csv datotek in dodamo fasta header ter ime organizma.
- Fasta header prekopiramo iz datoteke `"pul_a_seqs.fasta"`
- Organism ID je skrajšana verzija imena - "Plepul1"
- organism name je celotno ime vrste, enako velja za "Genus species", najdemo v originalni fasta datoteki, prenešeni iz NCBI, v oglatih oklepajih `"pul_b_protein.fasta"` - "Pleurotus pulmonarius"
  - "Name" je kar enak protein id-ju `"pul_summary.txt"`

- "protein_id" za posamezen protein je enak, kot pri shranjevanju datotek:
  - "pul_a1"
  - "pul_a2"
  - "pul_a3"


### 6.3 Pridobivanje HMMER za protein

```bash
# Znotraj direktorija 6_pleurotus_pulmunarius
cd aegerolysins/6_pleurotus_pulmonarius/
mkdir -p HMMER
cd HMMER

# Poženemo hmmer skripto
python ../../../../../scripts/HMMER_API/hmmer_api_v4.py -seq ../pul_a_seqs.fasta

# Pridobimo statistiko za HMMER
python ../../../../../scripts/HMMER_api_json_to_tab/json_to_tab.py --dir hmmer_results/

# Pridobimo slik
python ../../scripts/hmmer_features/features.py --dir aegerolysins/6_pleurotus_pulmonarius/HMMER/hmmer_results/ --output aegerolysins/6_pleurotus_pulmonarius/HMMER/hmmer_pics/
```

### 6.4. Pridobivanje filogenije

```
# Pripravljanje datoteke za pridobivanje 
echo "Pleurotus pulmonarius" > aegerolysins/6_pleurotus_pulmonarius/6.4_pleurotus_pulmonarius_for_phylogeny.txt

# Lookup phylogeny with script
python ../../scripts/NCBI_taxonomy/taxonomy_v7_pandas_gemini.py -i aegerolysins/6_pleurotus_pulmonarius/6.4_pleurotus_pulmonarius_for_phylogeny.txt -o aegerolysins/6_pleurotus_pulmonarius/6.4_phylogeny_Plepul1.csv

```

### 6.5 Združevanje metapodatkov v eno datoteko

Korak nam olajša delo pri upodabljanju drevesa s pomočjo programa TreeViewer.

```bash
# Create temporary directory for metadata
mkdir -p aegerolysins/6_pleurotus_pulmonarius/6.5_combined_metadata

# Copy metadata to temporary directory
cp aegerolysins/5_seqdupes/5.2_aegerolysins_noseqdupes_metadata.csv aegerolysins/6_pleurotus_pulmonarius/6.5_combined_metadata/

cp aegerolysins/6_pleurotus_pulmonarius/6.2_pul_a_metadata.csv aegerolysins/6_pleurotus_pulmonarius/6.5_combined_metadata/


# Merging the metadata files
awk 'FNR==1 && NR!=1{next;}{print}' aegerolysins/6_pleurotus_pulmonarius/6.5_combined_metadata/*csv > aegerolysins/6_pleurotus_pulmonarius/6.5_aegerolysin_noseqdupes_pula.csv

# Remove temporary directory
rm -rf aegerolysins/6_pleurotus_pulmonarius/6.5_combined_metadata/
```

#### 6.5.2. Checkpoint

Preverimo, ali je število sekvenc v csv datoteki enako številu sekvenc v fasta datoteki.

```bash
# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 aegerolysins/6_pleurotus_pulmonarius/6.5_aegerolysin_noseqdupes_pula.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > aegerolysins/logs/6.5.2_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/6.1.1_aegero_pul_a_stats.tsv | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> aegerolysins/logs/6.5.2_log.txt 

cat aegerolysins/logs/6.5.2_log.txt
```

## 7. Outgroups

### Združevanje vseh datotek:

Najprej združimo vse datoteke z metapodatki aegerolizinov in macpf-ov skupaj, in enako storimo za proteinske fasta datoteke.

```bash
mkdir -p outgroups

# Merge CSV metadata
csvtk concat  ../../data/outgroups/*csv > outgroups/1_all_outgroups_metadata_csv.csv

# Reformat CSV metadata
python ../../scripts/csv_utils/csv_cleaner.py -i outgroups/1_all_outgroups_metadata_csv.csv -o outgroups/1.1_all_outgroups_cleaned_metadata.csv

# Merge protein FASTA files.
seqkit seq ../../data/outgroups/*protein.fasta > outgroups/2_all_outgroups_protein.fasta
```



### 7.1. Dodajanje outgroup genomov k sekvencam macpf in pleurotus pulmunarius

- Združimo torej outgroup sekvence skupaj s sekvencami, ki smo jih pridobili v koraku združevanja 6.1

```bash
mkdir -p aegerolysins/7_outgroups

# 7.1_1: Get aegerolysin protids.
csvtk cut -d " " -f 2 ../../data/outgroups/aegerolysin_outgroups.txt | csvtk cut -d "|" -f 2 > aegerolysins/7_outgroups/7.1_1_aegero_outgroup_protids.txt

# 7.1_2: Get only aegerolysin outgroup sequences
seqkit grep -r -f aegerolysins/7_outgroups/7.1_1_aegero_outgroup_protids.txt outgroups/2_all_outgroups_protein.fasta > aegerolysins/7_outgroups/7.1_2_aegerolysin_outgroups.fasta

# 7.1_3: Kopiranje združenih datotek iz koraka 6.1
seqkit seq aegerolysins/6_pleurotus_pulmonarius/6.1_aegero_nodupes_pul.fasta aegerolysins/7_outgroups/7.1_2_aegerolysin_outgroups.fasta  > aegerolysins/7_outgroups/7.1_3_final_aeggero_all_outgroups_pula.fasta

```

### 7.2. Pridobivanje statistike

- Pridobimo statistiko novonastale fasta datoteke

#### 7.2.1. Statistika števila outgroup proteinov

- Preverimo, koliko outgroup proteinov bi naj dodali v novo datoteko.

```bash
seqkit stats --all --tabular aegerolysins/7_outgroups/7.1_2_aegerolysin_outgroups.fasta > aegerolysins/seqkit_stats/7.2.1_outgroup_stats.tsv
```

#### 7.2.2. Statistika števila proteinov po združevanju s sekvencami iz prejšnjih korakov.

```bash
seqkit stats --all --tabular aegerolysins/7_outgroups/7.1_3_final_aeggero_all_outgroups_pula.fasta > aegerolysins/seqkit_stats/7.2.2_all_stats.tsv
```

7.2.3 Preverimo, ali je sedaj število sekvenc po dodatku outgroupov za število outgroup sekvenc večje od števila sekvenc v datoteki iz koraka 6.1. po združevanju s sekvencami _Pleurotus pulmunarius_

```bash
# Check number of sequences before adding outgroups
num_seqs=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/6.1.1_aegero_pul_a_stats.tsv | csvtk del-header); echo "num_seqs_before_adding_outgroups: ${num_seqs}" > aegerolysins/logs/7.2.3_log.txt

# Check number of sequences of outgroups
num_seqs=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/7.2.1_outgroup_stats.tsv | csvtk del-header); echo "num_seqs_outgroups: ${num_seqs}" >> aegerolysins/logs/7.2.3_log.txt

# Check number of sequences after adding outgroups
num_seqs=$(csvtk cut -t -f "num_seqs" aegerolysins/seqkit_stats/7.2.2_all_stats.tsv | csvtk del-header); echo "num_seqs_added_outgroups: ${num_seqs}" >> aegerolysins/logs/7.2.3_log.txt

# See log
cat aegerolysins/logs/7.2.3_log.txt

```

### 7.3. Dodamo metapodatke 

```bash
# Get headers for extracting aegerolysin metadata from all metadata
seqkit seq -n aegerolysins/7_outgroups/7.1_2_aegerolysin_outgroups.fasta > aegerolysins/7_outgroups/7.3_aegerolysin_outgroup_headers.txt

# 7.3_1:
# Grab header
head -1 aegerolysins/6_pleurotus_pulmonarius/6.5_aegerolysin_noseqdupes_pula.csv > aegerolysins/7_outgroups/7.3_1_aegero_outgroups.csv

# Append aegerolysin outgroups
grep --fixed-strings -f aegerolysins/7_outgroups/7.3_aegerolysin_outgroup_headers.txt outgroups/1.1_all_outgroups_cleaned_metadata.csv >> aegerolysins/7_outgroups/7.3_1_aegero_outgroups.csv

# 7.3_2 Merge with file from step 6.5 (all aegerolysins + pul a proteins.)
csvtk concat aegerolysins/6_pleurotus_pulmonarius/6.5_aegerolysin_noseqdupes_pula.csv aegerolysins/7_outgroups/7.3_1_aegero_outgroups.csv > aegerolysins/7_outgroups/7.3_2_final_aegerolysins_noseqdupes_pula_outgroups_metadata.csv

# Checkpoint
num_seqs=$(csvtk del-header aegerolysins/7_outgroups/7.3_2_final_aegerolysins_noseqdupes_pula_outgroups_metadata.csv | wc -l); echo "num_seqs_outgroups_csv: ${num_seqs}" >> aegerolysins/logs/7.2.3_log.txt

cat aegerolysins/logs/7.2.3_log.txt
```



- References
