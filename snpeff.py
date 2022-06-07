def main():
    bestanden = ["files/0006.chr21.snpEff.vcf", "files/0052.chr21.snpEff.vcf"]
    bestand_lijst = parse(bestanden)
    bestand_opener(bestand_lijst)

def parse(bestanden):
    bestand_lijst = []
    for bestand in bestanden:
        bestand_open = open(bestand)
        variant_bestand = open(bestand+"variant", "w")
        bestand_lijst.append(bestand+"variant")
        for line in bestand_open:
            if "missense_variant" in line or "frameshift_variant" in line:
                # print(line)
                variant_bestand.write(line)
        bestand_open.close()
        variant_bestand.close()
    return bestand_lijst

def bestand_opener(bestand_lijst):
    variant_data = []
    for bestand in bestand_lijst:
        variant_bestand = open(bestand)
        for line in variant_bestand:
            stripped = line.strip()
            variant_data.append(stripped.split("\t"))
    print(variant_data)

main()
