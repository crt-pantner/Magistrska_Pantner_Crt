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

1. Korak:

   Medtem ko sem delal predikcije s pomočjo alphafold sem nekaj predikcij naredil preveč, zaradi česar sem moral najprej vse datoteke, ki jih potrebujem, poiskati in nato kopirati v eno podmapo. To sem storil tako, da sem s pridobil imena sekvenc za katere sem potreboval narediti predikcije. Nato sem vse nedovoljene črke v imenu spremenil v podčrtaj. S pomočjo Xlookup funkcije sem nato našel vse "_model_0.cif" datoteke, ter njihovo pot. 

   ```bash
   for line in (cat za_fold_mason.txt); set file (find ../../alphafold/aegerolysins/ -iname $line); cp $file za_fold_mason/; end
   ```

Izdelavo poravnave smo izvedli s pomočjo FoldMason programske opreme, verzije 4.dd3c235. Poravnavo več sekvenc smo izvedli pri različnih kaznih odpiranja vrzeli in sicer 5, 8 in 10. Vse poravnave smo izračunali s tisoč postopnimi izboljšavami. Ob pregledu nastale interaktivne datoteke s poravnavo zaporedja in poravnanimi predikcijami 3D strukture proteina, smo ugotovili, da je nekaj proteinov takšnih, ki imajo dve aegerolizinske domene, nekaj proteinov s podaljšanimi N in C terminalnimi deli in nekaj izjemno kratkih proteinov, brez smiselne 3D strukture. Proteine iz nabora podatkov odstranili in proteine ponovno poravnali. 



```bash
# gap-opening penalty 5

# Kazen 8
foldmason easy-msa za_fold_mason/ aegerolysins_alignment_gapopen_8_gapextend_default_maxiter_100 tmpFolder --report-mode 1 --refine-iters 1000 --gap-open 

# Gap-opening penalty 10 (default)
```

Na tej točki bi lahko iz poravnave izločili še tiste proteine, ki se ne prilegajo glede na osrednjo beta strukturo popolnoma, vendar sem se odločil, da je to out of scope za to magistrsko nalogo.
Glede na to, da je poravnava že tako ali tako zelo dobra v primerjavi z mafft-om sem s trenutno poravnavo zadovoljen. Odločil sem se, da bom nadaljeval z izgradnjo drevesa. 
To lahko omenim v končni magistrski nalogi v diskusiji. Poravnava morda ni najboljša, saj so proteini sekvenčno med sabo precej slabo identični. Poravnavo smo najprej poskušali narediti s "klasičnimi" metodami, vendar smo dobili sekvenco, katere velkik delež so sestavljali "gaps". Na podlagi tega rezultata smo posikusili poravnavo izboljšati s pomočjo metod za poravnavo na podlagi predikcije, vendar ugotovili, da še vedno velik delež poravnave sestavljajo luknje, in da se nekateri izmed proteinov ne poravnajo s svojimi beta trakovi na glavnino poravnanih proteinov.

### Prevajanje imen
Ker smo se morali za alphafold znebiti nekaterih znakov in ker alphafold k imenom sekvenc doda predpono "fold_" in končnico "_model_0" (oziroma natančneje ne doda model_številka modela, vendar mi uporabljamo "najboljši" model torej model 0) moramo preden lahko te proteine izrišemo s pomočjo GenePainterja preimenovati nazaj v originalna imena, kot so se pojavljala v vhodnih podatkih. Predvsem moramo to storiti, da lahko programatično poiščemo ustrezne vhodne gff datoteke. Skripta za izdelavo alphafold del nam že sama po sebi izpiše mapiranje med originalnimi fasta glavami in imeni, kot se pojavljajo v izhodnih alphafold datotekah

### S pomočjo sledečega ukaza pridobimo poročilo o fasta headerju, lokaciji alphafold modela na datotečnem sistemu in imeni datotek nastalih z alphafold. Na ta način lahko preverimo, ali imamo za vsak protein v fasta datoteki prisoten model

``` fish
csvtk cut -f 1,2,3 -H sequence_name_mapping.csv | while IFS=',' read -r 1 2 3 4; set location $(find ../results/alphafold/aegerolysins/ -iname "$4*model_0.cif"); set base $(basename $location); set header (string replace -r '_model_0.cif' '' "$base"); echo "$4,$location,$header" >> names.csv; end

```

Preimenovanje v poravnavi
seqkit replace --kv-file sequence_name_mappinga.csv -p "^([^\s]+)" -r "{kv}" ../results/alignment/aegerolysins/fold_mason/good_models/gapopen_20/gapextend_4/gapext_4_aa.fa

## Izbor substitucijskega modela

Pred izračunom drevesa smo opravili izbor substitucijskega modela s pomočjo modeltest-ng

```bash
mkdir results/tree/aegerolysins/fold_mason/modeltest-ng
modeltest-ng -d aa -i alignment/aegerolysins/fold_mason/good_models/gapopen_20/gapextend_4/gapext_4_aa.fa -o tree/aegerolysins/fold_mason_tree/modeltest-ng/modeltest_aegero --processes 8 --template raxml --verbose
```

zastavica "-d" definira, da imamo zaporedje sestavljeno iz aminokislin, "--proccesses 8" pomeni, da smo uporabili osem jeder za izračun najboljšega substritucijskega modela in "--template raxml" nam zagotavlja, da izbor poteka med substitucijskimi modeli, ki jih lahko raxml-ng uporablja, kar pomeni

RAXML-NG

```bash
# Check that the MSA file is okay
mkdir -p tree/aegerolysins/raxml-ng/check

raxml-ng --check --msa alignment/aegerolysins/fold_mason/good_models/gapopen_20/gapextend_4/gapext_4_aa.fa --model WAG+G4 --prefix tree/aegerolysins/fold_mason_tree/raxml-ng/check/aegerolysins_check

# Parse the MSA file and get recommended number of threads
mkdir -p tree/aegerolysins/fold_mason_tree/raxml-ng/parse
 
raxml-ng --parse --msa alignment/aegerolysins/fold_mason/good_models/gapopen_20/gapextend_4/gapext_4_aa.fa --model WAG+G4 --prefix tree/aegerolysins/fold_mason_tree/raxml-ng/parse/aegerolysins_parse

# Run the tree calculation
mkdir -p tree/aegerolysins/raxml-ng/tree
raxml-ng --all --msa alignment/aegerolysins/aegerolysins_alignment_maxiter_5000_localpair.fasta --model WAG+G4 --prefix tree/aegerolysins/raxml-ng/tree/aegerolysins_final_tre
e --threads 8 --bs-metric fbp,tbe
```

# Risanje Filogenetskega Drevesa

Najprej moramo dodati v datoteko z metapodatki podakte o mapiranju med v fasta datoteki in imeni v ne fasta 

Filogenetsko drevo smo narisali s pomočjo programske opreme TreeViewer.

Najprej moramo v našo datoteko z metapodatki vnesti še podatke o filogeniji, ki se bodo nato uporabili za barvanje drevesa.

- Skripta združi s pomočjo imena organizma datoteko csv z metapodatki in datoteko v kateri imamo shranjeno filogenijo. To naredi na podlagi vrste, v primeru da ni organizem definiran do vrste pa na podlagi rodu.

```Shell
# Prepare directories:
mkdir -p tree/tree_viewer/for_tree_viewer

python ../scripts/NCBI_taxonomy/helpers/csv_merger/metadata_merger.py -p cleaning/basidiomycota_phylogeny/basidiomycota_taxonomy.csv -m cleaning/aegerolysins/8_seqdupes/8.4_final_aegerolysins_deduplicated_metadata.csv -o tree/tree_viewer/for_tree_viewer/final_aegerolysins_with_metadata.csv
```

Naslednji korak je, da k vsakemu organizmu definiramo barvo. Barve smo izbrali s pomočjo spletnega orodja "I Want HUE", ki nam na podlagi vnesene številke vrne barve. Barve, ki smo jih uporabili so shranjene v `data/colors.txt`
