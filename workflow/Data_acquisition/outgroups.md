Za outgroup proteine smo uporabili proteine za MACPF in aegerolizine iz genoma <i>Aspergillus niger</i>

Proteine smo pridobili iz osebnega arhiva dr. Nade Kraševec

#TODO: Uredi/napiši od kod smo dobili proteine, oz. kako to navedem
Najprej proteinske sekvence damo v novo datoteko, ločimo glede na nig_a in nig_b.
V nig_b datoteki sta proteina nigB1 in nigB2.

Nato datoteki prečistimo, tako da uporabimo ukaz seqkit seq in izberemo kot vhodno datoteko datoteko s sekvencami bodisi nigB bodisi nigA.

```bash
seqkit seq data/outgroups/nig_b.fasta
```

Proteinske sekvence smo deponirali vsako v svojo datoteko.