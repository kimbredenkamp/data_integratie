def main():
    bestanden = ["files/PGPC_0006_S1.flt.vcf", "files/PGPC_0052_S1.flt.vcf"]
    chromosoom_pakker(bestanden)

def chromosoom_pakker(bestanden):
    for bestand in bestanden:
        bestand_open = open(bestand)
        nieuw_bestand = open(bestand+"21", "w")
        for line in bestand_open:
            if line.startswith("#") or line.startswith("chr21"):
                nieuw_bestand.write(line)
        bestand_open.close()
        nieuw_bestand.close()

main()
