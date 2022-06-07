import tabula

def main():
    bestanden = ['files\PGPC-6.pdf', 'files\PGPC-21.pdf', 'files\PGPC-52.pdf']
    csv_lijst = bestand_omzetten(bestanden)
    bestand_inlezen(csv_lijst)

def bestand_omzetten(bestanden):
    """
    Functie waarin alle pdf bestanden met behulp van tabula worden omgezet naar csv.
    Hierna worden alle bestandsnamen van deze bestanden in een lijst gezet
    die gebruikt worden door bestand_inlezen

    input: bestanden - lijst van alle nodige bestanden
    return: csv_lijst - lijst met alle csv bestandsnamen
    """
    csv_lijst = []
    for bestand in bestanden:
        # df = tabula.read_pdf(bestand, pages='all')[0]
        tabula.convert_into(bestand, "{}.csv".format(bestand), output_format="csv", pages="all")
        csv_lijst.append("{}.csv".format(bestand))
    return csv_lijst

def bestand_inlezen(csv_lijst):
    """
    In deze functie wordt de Profile en Conditions informatie uit
    de csv bestsanden gehaald.
    input: csv_lijst - lijst van alle csv bestanden
    """
    #lists voor de profiles en conditions
    profile = []
    conditions = []
    #loopt over de csv bestanden
    for bestand in csv_lijst:
        bestand_open = open(bestand)
        for line in bestand_open:
            #kijkt naar het Profile onderdeel aan de hand van verjaardag
            if "Birth month" in line:
                #wanneer dit is herkend, sla deze lijn over om
                #alleen de belangrijke informatie mee te nemen
                next_line = next(bestand_open).strip()
                profile.append(next_line.split(','))
            if "Conditions" in line:
                #Kijkt naar het conditions onderdeel
                for i in range(10):
                    next_line = next(bestand_open).strip()
                    # print(next_line.split(','))
                    #gaat door totdat het andere onderdeel is gevonden
                    if "Participant" not in next_line:
                        conditions.append(next_line.split(','))
main()
