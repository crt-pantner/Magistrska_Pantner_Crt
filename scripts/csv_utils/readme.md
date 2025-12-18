Nekaj pomožnih skript za cevovod čiščenja aegerolizinov oz. MACPF proteinov prenesenih iz JGI mycocosm, natančneje za csv datoteke z metapodatkih o proteinih.

## csv_cleaner.py
- Uporablja se za modifikacijo datoteke (dodajanja fasta glav in imen vrst) z metapodatki pridobljene iz JGI. 
- Skripta rekreira FASTA header-je, ki jih najdemo v datoteki s proteini, kar je uporabno za downstream korake tekom čiščenja podatkov.
- Skripta poskusi ustvariti tudi podatke za ime organizma, vendar pri nekaterih primerih ne uspe (recimo če je Organism Name v datoteki z metapodatki sestavljen iz več kot rodovnega in vrstnega imena.)
- Skripta nato izvozi datoteko z metapodatki v novo csv datoteko.


## duplicate_cleaner_csv.py
- Skripta, ki iz datoteke z metapodatki odstrani vse proteine z enakim imenom - na podlagi FASTA headerja (dodanega v datoteko z metapodatki s pomočjo csv_cleaner.py)
- Vhodna datoteka je datoteka z metapodatki, prečiščena.
