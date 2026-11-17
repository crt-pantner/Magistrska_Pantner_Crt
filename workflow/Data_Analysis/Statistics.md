3.6.1. Pridobimo filogenijo za aegerolizin-vsebujoče proteine

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

## Proteinske lastnosti

Za namen izračunanja proteinskih lastnosti in pridobivanja grafa proteinskih lastnosti (to je ..) smo uporabili skripto, ki za posamezen protein izračuna posamezno lastnost in nato vse združi na en graf. Za ta namen smo uporabili Biopython knjižnico.

```Shell
python ../../scripts/protein_properties/protein_properties_v2.py ../cleaning/aegerolysins/7_outgroups/7.1_3_final_aeggero_all_outgroups_pula.fasta fig.png Save to csv? ([Y / N]) Y
```

## Znotrajcelično nahajanje

To bi moglo bit signalP

TODO: DeepLoc naredi graf

Za izračun predvidenega znotrajceličnega nahajanja proteinov smo uporabili DeepLock 2.1 iz spletne strani DTU. https://services.healthtech.dtu.dk/services/DeepLoc-2.1/

Rezultate smo nato shranili in "parsirali" s pomočjo posebej narejene skripte, ter rezultate shranili v xlsx formatu.

## Predikcije terciarne strukture

Predikcije terciarne strukture smo izvedli s pomočjo AlphaFold serverja.

```bash
python ../../../scripts/alphafold_job_maker/alphafold_job_maker.py ../../cleaning/aegerolysins/7_outgroups/7.1_3_final_aeggero_all_outgroups_pula.fasta
```

Za to, a sem lahko proteine prenesel v alphafold server, sem moral preimenovati outgroup proteine, saj so imena vsebovala nedovoljene znake ("[ in ]").

Predikcije smo izračunali prez prednastavljenega "semena" (angl. seed) in smo torej uporabljali avtomatično izbiro semena.

Predikcije za protein jgi|Monpe1_1|83513|MPER_08048m.01 nismo izvedli, saj sekvenca vsebuje nedovoljene znake.

## GenePainter

Za genepainter smo odstranili najprej proteine, ki so daljši ali krajši od 10% mediane dolžine aegerolizinov.

V ta namen smo napisali skripto, ki nas vpraša po tem kakšen procent želimo izločiti in izloči vse sekvence. v datoteki removed_sequences_log.txt se nam izpiše poročilo z odstranjenimi sekvencami in z statistiko - kakšen je bil modus, kakšna je bila zgornja meja in spodnja meja ter koliko sekvenc se je odstranilo in koliko sekvenc ohranilo. V našem primeru je bil modus za aegerolizine enak 139 bp, zgornja meja 152.9 bp in spodnja meja 125.1 bp. Ohranilo se je 159 sekvenc in 79 sekvenc se je odstranilo.

Pri tem si shranimo tudi graf porazdelitve dolžine sekvenc pred in po odstranjevanju

```bash
# Generate graph after removal of sequences
seqkit watch kept_sequences.fasta -O graph_after_removal.png

# Generate graph before removal of sequences.
seqkit watch 
../../../cleaning/aegerolysins/7_outgroups/7.1_3_final_aeggero_all_outgroups_pula.fasta -O graph_before_removal.png
```


### GenePainter workflow
 
GenePainter je zelo muhast program, zato smo ga morali tretirati nekoliko drugače. GenePainter potrebuje za svoj vnos datoteke gff3, ki se v imenu popolnoma ujemajo z glavami fasta v datoteki s poravnavo več zaporedij. Hkrati ima GenePainter omejeno število znakov, ki jih lahko prikaže na grafu, zato smo najprej s pomočjo #TODO custom made programa iz datotek gff3 datotek posameznega proteina izločili samo vnose, ki so se ujemali z našim protein ID-ji prisotnimi v poravnavi. Program nato poišče gff3 datoteko za posamezen protein, ga "prevede" v format, ki ga GenePainter sprejme, ter nato sharni v novo GFF datoteko. Pri tem skrajša ime proteina na kratko ime organizma ter protein id. Hkrati program nato izpiše še novo MSA datoteko, v kateri spremeni fasta glavo posameznega proteina na način, da se popolnoma ujema z imenom novonastale GFF datoteke. Datoteke MSA in GFF nato služijo kot vhodne datoteke za GenePainter.

```bash
mkdir -p test
python /run/media/crt/Crt_Omarchy/@home/crt-desktop/Development/Magistrska_Pantner_Crt/scripts/gene_painter_extraction_script/gene_painter_extraction.py --msa ../alignment_renamed.fasta --gff /run/media/crt/Crt_Omarchy/@home/crt-desktop/Databases/basidiomycota_download_merged/ --o "test" -a "test" -d /run/media/crt/Crt_Omarchy/@home/crt-desktop/Databases/gffutils_databases/
mv test/ results/
```



Naslednji korak je, da preiskusimo, ali katera izmed sekvenc zaradi svoje sestave povzroča napake pri GenePainterjevem izračunu intronskih pozicij. To smo naredili s pomočjo for zanke, ki najprej za vsak protein v novem direktoriju ustvari mapo, nato vanj prenese gff datoteko in hkrati iz vhodne MSA datoteke, namenjene za GenePainter izžame še sekvenco proteina. Na ta način lahko iterativno poganjamo GenePainter samo na eni sekvenci in pri tem beležimo, kateri protein se izvaja. Če je se pri nekem proteinu pojavi napaka, nam zanka to javi in lahko ta protein odstranimo iz nabora podatkov. 
Ukaz za razhroščevanje je na voljo v `/scripts/Gene_Painter_Troubleshoot/troubleshoot_command.txt`. 

Ko izolčimo proteine, lahko poženemo GenePainter z ukazom:

```bash
ruby ~/Programs/gene_painter/gene_painter.rb -i results/new_msa.fasta -p results/ --svg --svg-format both -o genepainter_res --statistics
```

