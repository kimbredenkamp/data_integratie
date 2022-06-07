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
    profile = []
    conditions = []
    for bestand in csv_lijst:
        # print(bestand)
        bestand_open = open(bestand)
        for line in bestand_open:
            if "Birth month" in line:
                next_line = next(bestand_open).strip()
                profile.append(next_line.split(','))
            if "Conditions" in line:
                for i in range(5):
                    next_line = next(bestand_open).strip()
                    # print(next_line.split(','))
                    conditions.append(next_line.split(','))
    print(profile)
    print(conditions)

main()
