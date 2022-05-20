import tabula

def main():
    bestanden = ['files\PGPC-6.pdf', 'files\PGPC-21.pdf', 'files\PGPC-52.pdf']
    csv_lijst = bestand_omzetten(bestanden)
    bestand_inlezen(csv_lijst)

def bestand_omzetten(bestanden):
    csv_lijst = []
    for bestand in bestanden:
        # print(bestand)
        df = tabula.read_pdf(bestand, pages='all')[0]
        # print(df)
        tabula.convert_into(bestand, "{}.csv".format(bestand), output_format="csv", pages="all")
        csv_lijst.append("{}.csv".format(bestand))
        # print(csv_lijst)

    return csv_lijst

def bestand_inlezen(csv_lijst):
    """
    Dit is echt nog een hele flop, ik dacht misschien de volgende line printen,
    moet alleen nog even kijken hoe dat precies gaat :((
    
    ik dacht als het werkend was dat ik voor de Conditions
    nextline totdat de volgende title gevonden wordt
    """
    teller = 0
    for bestand in csv_lijst:
        print(bestand)
        bestand_open = open(bestand)
        for line in bestand_open:
            teller+1
            stripped = line.strip()
            #print(stripped.split(','))
            if "Birth month" in stripped:
                print(bestand.nextLine())

main()
