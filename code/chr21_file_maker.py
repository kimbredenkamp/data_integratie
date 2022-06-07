def main():
    bestanden = ["files/PGPC_0006_S1.flt.vcf", "files/PGPC_0052_S1.flt.vcf"]
    chromosoom_pakker(bestanden)

def chromosoom_pakker(bestanden):
    """
    Om de bestanden klaar te maken voor snpEff moet eerst alle
    informatie dat bij Chromosoom 21 in een apart bestand gezet worden
    input: bestanden - lijst met alle bestandsnamen
    output: nieuw bestand - voor elk bestand wordt er een nieuw bestand
    aangemaakt met alleen maar de informatie voor chr21
    """
    for bestand in bestanden:
        bestand_open = open(bestand)
        #maakt een nieuw bestand aan met 21 er achter
        nieuw_bestand = open(bestand+"21", "w")
        for line in bestand_open:
            #neemt alle headers mee en alle lines met chr21
            if line.startswith("#") or line.startswith("chr21"):
                #schrijft de lines door naar het nieuwe bestand
                nieuw_bestand.write(line)
        bestand_open.close()
        nieuw_bestand.close()

main()
