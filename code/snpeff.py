def main():
    bestanden = ["files/0006.chr21.snpEff.vcf", "files/0052.chr21.snpEff.vcf"]
    bestand_lijst = parse(bestanden)
    # bestand_opener(bestand_lijst)
    bestand(bestand_lijst)


def parse(bestanden):
    """
    In deze functie worden alle gewenste variants uit de data gehaald.
    Deze worden weer omgeschreven tot een neiuwe file
    input: bestanden - lijst met alle vcf bestanden
    """
    bestand_lijst = []
    for bestand in bestanden:
        bestand_open = open(bestand)
        #maakt een bestand aan met "variant" er achter ter verduidelijking
        variant_bestand = open(bestand + "variant", "w")
        #zorgt ervoor dat de bestandsnaam in de lijst voorkomt
        bestand_lijst.append(bestand + "variant")
        # variant_bestand.write("#"+bestand+"variant")
        for line in bestand_open:
            #zoekt missense en frameshift variants om deze lines in het
            #nieuwe bestand te zetten
            if "missense_variant" in line or "frameshift_variant" in line:
                # print(line)
                variant_bestand.write(line)
        bestand_open.close()
        variant_bestand.close()
    return bestand_lijst


def bestand(bestandlijst):
    """
    """
    variant_data06 = []
    variant_data52 = []
    gen_data06 = []
    gen_data52 = []
    bestand1 = bestand_lijst[0]
    bestand2 = bestand_lijst[1]
    variant_bestand = open(bestand1)
    for line in variant_bestand:
        stripped = line.strip()
        variant_data06.append(stripped.split("\t"))
    variant_bestand2 = open(bestand2)
    for line in variant_bestand2:
        stripped = line.strip()
        variant_data52.append(stripped.split("\t"))
    for x in range(10):
        lijntje = variant_data06[x][7].split(";")
        lijn = lijntje[2].split("|")
        gen_data06.append(lijn[4])
        lijntjex = variant_data06[x][7].split(";")
        lijnx = lijntjex[2].split("|")
        gen_data52.append(lijnx[4])
    return gen_data06, gen_data52)

# def bestand_opener(bestand_lijst):
    # variant_data = []
    # for bestand in bestand_lijst:
    #     variant_bestand = open(bestand)
    #     variant_data.append(bestand)
    #     for line in variant_bestand:
    #         stripped = line.strip()
    #         variant_data.append(stripped.split("\t"))
    # print(variant_data)
main()

