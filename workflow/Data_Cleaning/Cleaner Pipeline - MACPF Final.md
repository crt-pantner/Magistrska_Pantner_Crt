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
Ukaze poganjamo iz direktorija results/cleaning

# Data Cleaning



## 1. Združevanje podatkov - 1_combined
1.1 Združevanje CSV datoteke

- CSV datoteke s ključnimi besedami združimo v eno datoteko

```bash
# Directories
mkdir macpf/1_combined
cd results/cleaning/

# Finding the csv files
for file in $(find ../../data/macpf/ -iname *csv*); do echo $file; cp $file .; done

# Merging the files
awk 'FNR==1 && NR!=1{next;}{print}' *csv > macpf/1_combined/1.1_macpf_combined.csv

sed -i 's|/|_|g' macpf/1_combined/1.1_macpf_combined.csv

# Cleanup
rm *csv
```

### 1.2. Prečiščevanje CSV datoteke z metapodatki
- Skripta naredi nov stolpec v csv datoteki s fasta headerjem, kot se pojavlja v fasta datotekah, ter doda stolpec z Rodovnim in vrstnim imenom (skupaj)

```
input: združena datoteka z metapodatki: "1.1_macpf_combined.csv"
output: prečiščena datoteka z metapodatki: "1.2_macpf_cleaned.csv"
```

**Bug:** Skripta za tiste proteine, ki imajo v stolpcu `Name` več kot eno besedo ohrani v celoti, medtem ko downstram seqkit pusti (mislim da) samo prvo besedo. Do sedaj popravljeno ročno - v koraku XX seqkit javi napako v stilu "whitespace found in pattern, maybe try searching with -n"

```bash
# Activating conda env
conda activate cleaner_pipeline

# Running script
python3 ../../scripts/csv_utils/csv_cleaner.py -i macpf/1_combined/1.1_macpf_combined.csv -o macpf/1_combine
d/1.2_macpf_cleaned.csv
```

### 1.3. Združevanje FASTA datotek
- Združimo vse fasta datoteke s proteinskimi sekvencami
```
input: več fasta datotek s sekvencami proteinov (ena na en keyword)
output: ena fasta datoteka z vsemi sekvencami: 1.3_protein_combined.fasta
```

```bash
# Find and read protein FASTA files, read and concat them to 1.3_protein_combined.fasta
find ../../data/macpf/keywords/ -iname *protein* | xargs cat > macpf/1_combined/1.3_protein_combined.fasta

sed 's|/|_|g' macpf/1_combined/1.3_protein_combined.fasta
```

#### 1.3.1. Statistics
- Pridobivanje statistike o vseh prenešenih proteinih pred kakršnim koli čiščenjem
```
input: FASTA s sekvencami proteinov: "1.3_protein_combined.fasta"
output: Statistika, ločena s tabulatorjem: "1.3.1_protein_combined_stats.tsv"
```

```bash
# Directory management
mkdir macpf/seqkit_stats

# Obtaining stats of combined proteins, saving to tsv file
seqkit stats -a -T macpf/1_combined/1.3_protein_combined.fasta > macpf/seqkit_stats/1.3.1_protein_combined_stats.tsv

```

#### 1.3.2. Checkpoint
- Preverimo, ali je število proteinov v csv datoteki enako številu sekvenc v fasta datoteki.
```bash
# Preparing log directory
mkdir macpf/logs

# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 macpf/1_combined/1.2_macpf_cleaned.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > macpf/logs/1.3.2_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(cat macpf/seqkit_stats/1.3.1_protein_combined_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> macpf/logs/1.3.2_log.txt

cat macpf/logs/1.3.2_log.txt

```


### 1.4. Cleaning FASTA headers
- Na tej točki imamo v združeni fasta datoteki s proteini v imenu posameznega proteina, t.i. fasta headerju še veliko nepotrebnih podatkov, ki se jih moramo znebiti.

```
input: FASTA datoteka s sekvencami vseh proteinov: "1.3_protein_combined.fasta"
output: FASTA datoteka s sekvencami vseh proteinov z ID namesto celotnega imena: "1.4_protein_ids_combined.fasta"
```


```bash

# Removing ID-s from fasta headers
seqkit seq -i macpf/1_combined/1.3_protein_combined.fasta > macpf/1_combined/1.4_protein_ids_combined.fasta
```

#### 1.4. 1. Statistika
- Pridobimo statistiko po čiščenju FASTA headerjev.
```
input: FASTA z združenimi macpf, samo id-ji: 1.4_protein_ids_combined.fasta
output: datoteka z statistiko o tem, koliko je macpfov združenih, pred odstranjevanjem glede na ID: 1.4.1_protein_ids_combined_stats.tsv
```

```bash
seqkit stats -a -T macpf/1_combined/1.4_protein_ids_combined.fasta > macpf/seqkit_stats/1.4.1_protein_ids_combined_stats.tsv

```
#### 1.4.2. Preverjanje enakosti
- Preverimo, ali pri združevanju sekvenc s Seqkit ni prišlo do kakšne napake, in da je število sekvenc ostalo enako.

```bash
# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 macpf/1_combined/1.2_macpf_cleaned.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > macpf/logs/1.4.2_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(cat macpf/seqkit_stats/1.4.1_protein_ids_combined_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> macpf/logs/1.4.2_log.txt

cat macpf/logs/1.4.2_log.txt
```


## 2. Odstranjevanje imenskih duplikatov
- V tej točki imamo v FASTA datoteki zaradi načina podatkovnega rudarjenja sekvenc (dve ključni besedi lahko vrneta enak protein, oz. veliko proteinov vsebuje več kot eno ključno besedo, zato nekaj proteinov efektivno prenesemo dva ali več krat), več sekvenc ki so identične po imenu in sekvenci - znebimo se jih.
### 2.1. Odstranjevanje imenskih duplikatov iz fasta datoteke
- Imenski duplikati so proteini, ki imajo enako ime in posledično tudi enako sekvenco.
```
input: FASTA datoteka MACPF z ID-ji - "1.4_protein_ids_combined.fasta"
output: 
	- Datoteka s seznamom in številom posameznih imenskih duplikatov - "2.1_1_macpf_protein_namedupes.txt"
	- FASTA datoteka z imenskimi duplikati - "2.1_2_macpf_protein_namedupes.fasta"
	- FASTA datoteka z odstranjenimi imenskimi duplikati - "2.1_3_macpf_protein_nonamedupes.fasta"
```

```bash
# Directory management
mkdir macpf/2_name_copies

# Removing duplicates
seqkit rmdup -n -D macpf/2_name_copies/2.1_1_macpf_protein_namedupes.txt -d macpf/2_name_copies/2.1_2_macpf_protein_namedupes.fasta macpf/1_combined/1.4_protein_ids_combined.fasta > macpf/2_name_copies/2.1_3_macpf_protein_nonamedupes.fasta
```

#### 2.1.1. Statistika
- Pridobimo statistiko FASTA datoteke po tem ko smo odstranili imenske duplikate

```
input: FASTA datoteka z odstranjenimi imenskimi duplikati: "2.1_3_macpf_protein_nonamedupes.fasta"
output: statistika porteinov brez imenskih duplikatov:      "2.1.1_macpf_protein_nonamedupes_stats.tsv"
```

```bash
seqkit stats -a -T macpf/2_name_copies/2.1_3_macpf_protein_nonamedupes.fasta > macpf/seqkit_stats/2.1.1_macpf_protein_nonamedupes_stats.tsv
```


### 2.2. Odstranjevanje imenskih duplikatov iz CSV datoteke:
```
input: Prečišččena datoteka CSV z metapodatki: "1.2_macpf_cleaned.csv"
output: Prečiščena datoteka CSV z metapodatki brez imenskih duplikatov: "2.2_macpf_nonamedupes.csv"
```

```bash

# Running duplicate_cleaner_csv script
python3 ~/Development/csv_utils/duplicate_cleaner_csv.py -i macpf/1_combined/1.2_macpf_cleaned.csv -o macpf/2_name_copies/2.2_macpf_nonamedupes.csv

```

### 2.3. Checkpoint
- Preverimo, ali je število proteinov v CSV datoteki enako številu proteinov v fasta datoteki

```bash
# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 macpf/2_name_copies/2.2_macpf_nonamedupes.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > macpf/logs/2.3_log.txt


# Exporting number of sequences in seqkit stats file
	num_seqs=$(cat macpf/seqkit_stats/2.1.1_macpf_protein_nonamedupes_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> macpf/logs/2.3_log.txt

cat macpf/logs/2.3_log.txt
```

### 2.4. Pridobi statistiko odstranjenih proteinov
```
input: FASTA datoteka imenskih duplikatov: "2.1_2_macpf_protein_namedupes.fasta"
output: statistika imenskih duplikatov: "2.4_macpf_protein_namedupes_stats.tsv"
```

```bash
# Get statistics
seqkit stats -a -T macpf/2_name_copies/2.1_2_macpf_protein_namedupes.fasta > macpf/seqkit_stats/2.4_macpf_protein_namedupes_stats.tsv
```

### 2.5. Checkpoint
- #TO-DO: preverimo, ali je število proteinov po odstranjevanju + število imenskih duplikatov enako številu proteinov pred odstranjevanjem
## 3. HMMER
- S pomočjo HMMER programske opreme poiščemo vse proteinske domene, ki se pojavljajo na našem naboru proteinov, in odstranimo tiste, ki ne vsebujejo MACPF domene.

### 3.1. Poženemo HMMER skripto 
```
input: FASTA datoteka z odstranjenimi imenskimi duplikati: "kept_after_name_cleaning_macpf.fasta"
ouptut: 
macpf/hmmer/hmmer_results/ - rezultati zadetkov v json formatu za posamezen protein

macpf/hmmer/proteins.txt - datoteka s podatki o tem, kateri proteini so se obdelali
macpf/hmmer/not_processed.txt - datoteka s proteini, ki se niso procesirali
macpf/hmmer/no_domains.txt - datoteka s proteini, na katerih ni bilo zaznane nobene domene.
```

```bash
# Directory management
mkdir macpf/3_hmmer
cd macpf/3_hmmer

python3 ../../../../scripts/HMMER_API/hmmer_api_v4.py -seq ../2_name_copies/2.1_3_macpf_protein_nonamedupes.fasta 

```

### 3.2 Pridobimo poročilo o zadetkih
- Pregledamo datoteke json  z rezultati o zadetkih na našem naboru proteinov in izdelamo poročilo z začetkom in koncem ujemanja posamezne proteinske domene z našim proteinom, ter PFAM identifikacijskimi številkami.

```
input: Datoteka sama poišče JSON datoteke o zadetkih v podmapi /hmmer_results/
output: "aegerolysin_containing_proteins.csv" - proteini, ki imajo aegerolizinsko domeno
	- "macpf_containing_proteins.csv" - proteini, ki imajo macpf domeno
	- "significant_hits_remport.xlsx" - poročilo o signifikantnih zadetkih 
```

```bash
# Directory management, start from within 3_hmmer directory
cd ../..

# Executing script
python3 ../../../../scripts/HMMER_api_json_to_tab/json_to_tab.py -dir hmmer_results/
```
### 3.4. Izločimo proteine, ki niso MACPF
####  3.4.1. Izločanje iz FASTA datoteke
- S pomočjo HMMER rezultatov izločimo iz FASTA datoteke proteine, ki nimajo MACPF domen
  - HMMER skripta nam vrne 


```
input: "macpf_containing_proteins.csv"
output:
FASTA datoteka MACPF vsebujočih proteinov: "macpf_after_hmmer.fasta"
Statistika za MACPF vsebujoče proteine: "seqkit_stats_after_hmmer.tsv"
FASTA datoteka z izločenimi proteini: "non-macpf_containing.fasta"
Statitika izločenih proteinov: "seqkit_stats_non_macpf_containing_after_hmmer.tsv"
```


```bash

# Directory management
cd ../..
mkdir macpf/3_hmmer/3_4_after_hmmer


# Getting macpf-containig proteins
seqkit grep -f macpf/3_hmmer/macpf_containing_proteins.csv macpf/2_name_copies/2.1_3_macpf_protein_nonamedupes.fasta > macpf/3_hmmer/3_4_after_hmmer/3.4.1_macpf_after_hmmer.fasta
```

#### 3.4.2 Statistika MACPF-vsebujočih

```bash
# Obtaining statistics for macpf-containg proteins
seqkit stats -a -T macpf/3_hmmer/3_4_after_hmmer/3.4.1_macpf_after_hmmer.fasta > macpf/seqkit_stats/3.4.2_macpf_after_hmmer.tsv
```

#### 3.4.3 Pridobivanje ne-macpf vsebujočih proteinov

```bash
# Keeping non-macpf containing proteins
seqkit grep -v -f macpf/3_hmmer/macpf_containing_proteins.csv macpf/2_name_copies/2.1_3_macpf_protein_nonamedupes.fasta > macpf/3_hmmer/3_4_after_hmmer/3.4.3_macpf_non_containig.fasta
```

#### 3.4.4. Statistika ne-MACPF vsebujočih

```bash
seqkit stats -a -T macpf/3_hmmer/3_4_after_hmmer/3.4.3_macpf_non_containig.fasta > macpf/seqkit_stats/3.4.4_macpf_non_containing.tsv
```

#### 3.4.5. Izločanje iz CSV datoteke

- Iz datoteke z metapodakti naših proteinov moramo izločiti tiste, ki ne vsebujejo MACPF domene.

```
input: CSV datoteka z odstranjenimi duplikati na ime 2.2_macpf_nonamedupes.csv
output: CSV datoteka z metapodatki samo za MACPF vsebujoče proteine: 3.4.2_macpf_after_hmmer_headers.txt
```

```bash
# Get first line from csv file
head -1 macpf/2_name_copies/2.2_macpf_nonamedupes.csv > macpf/3_hmmer/3_4_after_hmmer/3.4.5_macpf_after_hmmer.csv

# Get proteins with macpfs
grep -F -f macpf/3_hmmer/macpf_containing_proteins.csv macpf/2_name_copies/2.2_macpf_nonamedupes.csv >> macpf/3_hmmer/3_4_after_hmmer/3.4.5_macpf_after_hmmer.csv
```



### 3.5. Checkpoint

Preverimo, ali se po odstranjevanju MACPF nevsebujočih proteinov iz datoteke z metapodatki ujema s številom proteinov v FASTA datoteki.
```bash
# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 macpf/3_hmmer/3_4_after_hmmer/3.4.5_macpf_after_hmmer.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > macpf/logs/3.5_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(cat macpf/seqkit_stats/3.4.2_macpf_after_hmmer.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> macpf/logs/3.5_log.txt

cat macpf/logs/3.5_log.txt
```



### 3.6. Pridobimo statistiko proteinov, ki vsebujejo MACPF domeno.
- Na tej točki imamo vse proteine, ki so realni MACPF proteini - nekaj izmed njih je duplikatov, nekaj pa je takih, ki jih zaradi politike uporabe podatkov JGI ne smemo uporabiti

#### 3.6.1. Pridobimo filogenijo za MACPF-vsebujoče proteine
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
- Če imamo med organizmi, ki vsebujejo MACPF proteine tudi takšne, ki še niso bili objavljeni, moramo najprej pri avtorjih vprašati za dovoljenje.
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
mkdir macpf/4_permitted

# Grab the fist line from CSV file
head -1 macpf/3_hmmer/3_4_after_hmmer/3.4.5_macpf_after_hmmer.csv > macpf/4_permitted/4.1_macpf_permitted_metadata.csv
## Iz nekega razloga se mi tukaj sfiži in dobim prvo vrstico csv natistnjeno dvakrat.

# Grab only the lines that are not in the not_allowed.txt file 
grep -v -F -f ../../data/permissions/not_allowed.txt macpf/3_hmmer/3_4_after_hmmer/3.4.5_macpf_after_hmmer.csv >> macpf/4_permitted/4.1_macpf_permitted_metadata.csv
```

#TO-DO: Iz nekega razloga se nekaj sfiži v tej kodi in dobim prvo vrstico csv natisnjeno dvakrat - preveri. 
#TO-DO: Preštej koliko proteinov se je s tem odstranilo

#### 4.2. Odstranjevanje iz FASTA datoteke

```
input:
output:
```

```bash
# Preparing the headers for seqkit
csvtk cut -U -f  fasta_header macpf/4_permitted/4.1_macpf_permitted_metadata.csv > macpf/4_permitted/4.2_macpf_permitted_headers.txt


# Fetching only the permitted proteins
seqkit grep -f macpf/4_permitted/4.2_macpf_permitted_headers.txt macpf/3_hmmer/3_4_after_hmmer/3.4.1_macpf_after_hmmer.fasta > macpf/4_permitted/4.2_macpf_permitted.fasta
## Nekateri proteini se tukaj izmuznejo. Porpravljeno ročno - predvsem tisti, ki imajo whitespace v imenu.

```

#TO-DO Nekateri proteini se v tem koraku izmuznejo - mislim da predvsem tisti, ki imajo whitespace v imenu. Glej  korak 1.1.

#### 4.3. Pridobivanje statistike
##### 4.3.1. Pridobivanje statistike proteinov po odstranjevanju nedovoljenih proteinov.

```bash
seqkit stats -a -T macpf/4_permitted/4.2_macpf_permitted.fasta > macpf/seqkit_stats/4.3.1_macpf_permitted_stats.tsv
```

##### 4.3.2. Checkpoint

Preverimo ali je število sekvenc v fasta datoteki po odstranjevanju nedovoljenih proteinov enako številu sekvenc v csv datoteki po odstranjevanju dovoljenih proteinov.

```bash
# Checking and exporting number of sequences in csv file
num_seqs=$(tail -n +2 macpf/4_permitted/4.1_macpf_permitted_metadata.csv | cut -d "," -f 2 | wc -l); echo "num_sequences_csv: ${num_seqs}" > macpf/logs/4.3.2_log.txt

# Exporting number of sequences in seqkit stats file
num_seqs=$(cat macpf/seqkit_stats/4.3.1_macpf_permitted_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_fasta: ${num_seqs}" >> macpf/logs/4.3.2_log.txt

cat macpf/logs/4.3.2_log.txt
```





##### 4.3.2. Pridobivanje izgubljenih proteinov in statistiko izgubljenih proteinov

```
input:
output:
```

```bash
# Get non-permitted proteins
seqkit grep -v -f macpf/4_permitted/4.2_macpf_permitted_headers.txt macpf/3_hmmer/3_4_after_hmmer/3.4.1_macpf_after_hmmer.fasta > macpf/4_permitted/4.3.2_macpf_non_permitted.fasta

# Get statistics for non-permitted proteins
seqkit stats -a -T macpf/4_permitted/4.3.2_macpf_non_permitted.fasta > macpf/seqkit_stats/4.3.2_macpf_non_permitted_stats.tsv

```

##### 4.3.3. Checkpoint

Preverimo, ali je število nedovoljenih proteinov + število dovoljenih proteinov enako številu pred izločanjem glede na dovoljenje

```bash
# Get number of sequences in fasta file before permission remova
num_seqs_before=$(cat macpf/seqkit_stats/3.4.2_macpf_after_hmmer.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_before_permission: ${num_seqs_before}"  > macpf/logs/4.3.3_log.txt

# Get number of sequences in fasta file that are permitted to be used
num_seqs_permitted=$(cat macpf/seqkit_stats/4.3.1_macpf_permitted_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_permitted: ${num_seqs_permitted}" >> macpf/logs/4.3.3_log.txt

# Get number of sequences that are not allwed
num_seqs_forbidden=$(cat macpf/seqkit_stats/4.3.2_macpf_non_permitted_stats.tsv | csvtk cut -t -f "num_seqs" | csvtk del-header); echo "num_seqs_forbidden: ${num_seqs_forbidden}" >> macpf/logs/4.3.3_log.txt

cat macpf/logs/4.3.3_log.txt

```

## 5. Odstranjevanje glede na sekvenco

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