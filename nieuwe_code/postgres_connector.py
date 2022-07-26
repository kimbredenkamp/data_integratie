# Gijsbert Keja, Femke Nijman en Kim Bredenkamp
# 07/06/22
# Deze applicatie parst data en vult/fetcht data uit een database
import psycopg2
import tabula
import datetime
import random


def main():
    """
        De main roept alle functies aan zodat het script kan werken
    """
    person_6_id = 1  # ID van participant 6
    person_21_id = 2  # ID van participant 21
    person_52_id = 3  # ID van participant 52
    bestanden_SNP = ["0006.chr21.snpEff.vcf", "0052.chr21.snpEff.vcf"]
    pdf_bestanden = ['PGPC-6.pdf', 'PGPC-21.pdf', 'PGPC-52.pdf']

    csv_lijst = bestand_omzetten(pdf_bestanden)
    profile, conditions = bestand_inlezen(csv_lijst)
    lijst_ziektes_P6, lijst_ziektes_P52 = ziekte_lijsten_generen(
        conditions)
    ziektes_aangepast_P6, ziektes_aangepast_P52 = ziekte_lijst_aanpassen(
        lijst_ziektes_P6, lijst_ziektes_P52)
    IDs_ziektes_P6, IDs_ziektes_P52 = ID_maker_ziektes(lijst_ziektes_P6,
                                                       lijst_ziektes_P52)
    bestand_lijst = parse(bestanden_SNP)
    gen_data06, gen_data52 = snp_parser(bestand_lijst)
    IDs_measurementP6, IDs_measurementP52 = ID_maker_measurement_ID(
        gen_data06, gen_data52)
    database_person_vullen(profile, person_6_id, person_21_id,
                           person_52_id)
    database_condition_vullen(lijst_ziektes_P6, lijst_ziektes_P52,
                              IDs_ziektes_P6, IDs_ziektes_P52,
                              person_6_id,
                              person_52_id)
    measurement_vullen(gen_data06, gen_data52, person_6_id,
                       person_52_id, IDs_measurementP6,
                       IDs_measurementP52)
    profile = profile_aanpassen(profile)
    totale_lijst_dicts = database_fetch(ziektes_aangepast_P6,
                                        ziektes_aangepast_P52,
                                        lijst_ziektes_P6,
                                        lijst_ziektes_P52,
                                        profile, gen_data06, gen_data52)
    concept_id_mapping(profile, lijst_ziektes_P6, lijst_ziektes_P52,
                       totale_lijst_dicts, person_6_id, person_21_id,
                       person_52_id, gen_data06, gen_data52)


def bestand_omzetten(pdf_bestanden):
    """
       Functie waarin alle pdf bestanden met behulp van tabula worden omgezet naar csv.
       Hierna worden alle bestandsnamen van deze bestanden in een lijst gezet
       die gebruikt worden door bestand_inlezen
       input: pdf_bestanden - lijst van alle nodige bestanden
       return: csv_lijst - lijst met alle csv bestandsnamen
    """
    try:
        csv_lijst = []
        for bestand in pdf_bestanden:
            print(bestand)
            df = tabula.read_pdf(bestand, pages='all')[0]
            print(df)
            tabula.convert_into(bestand, "{}.csv".format(bestand),
                                # hier wordt de PDF omgezet naar een CSV
                                output_format="csv", pages="all")
            csv_lijst.append("{}.csv".format(bestand))
        return csv_lijst
    except(Exception, ValueError, IndexError,
           TypeError, FileNotFoundError) as error:
        print(error)


def bestand_inlezen(csv_lijst):
    """
       In deze functie wordt de Profile en Conditions informatie uit
       de csv bestsanden gehaald.
       input: csv_lijst - lijst van alle csv bestanden
       """
    try:
        profile = []
        conditions = []
        for bestand in csv_lijst:
            bestand_open = open(bestand)
            for line in bestand_open:
                if "Birth month" in line:
                    next_line = next(bestand_open).strip()
                    profile.append(next_line.split(
                        ','))  # hier wordt de observationele data toegevoegd aan het profiel
                if "Conditions" in line:
                    for i in range(5):
                        next_line = next(bestand_open).strip()
                        conditions.append(next_line.split(
                            ','))  # hier wordt de ziekte data toegevoegd aan het profiel
        return profile, conditions

    except(Exception, ValueError, IndexError,
           TypeError) as error:
        print(error)


def ziekte_lijsten_generen(conditions):
    """
    Deze fucntie creëert 2 aparte lijsten van de ziektes die bij de
    patienten horen
    :param conditions: Bestand met alles ziektes van beiden patiënten
    :type conditions: list
    :return:
    :lijst_ziektes_P6: Alle ziektes behorende tot Patient 06
    :rtype: list
    :lijst_ziektes_P52: Alle ziektes behorende tot Patient 06
    :rtype: list
    """
    try:
        lijst_ziektes_P6 = []
        lijst_ziektes_P52 = []
        for x in conditions:
            if x[0] == 'PGPC-6':
                lijst_ziektes_P6.append(x[
                                            1])  # hier worden alle ziektes van patient 06 aan een lijst toegevoegd
            elif x[0] == 'PGPC-52':
                lijst_ziektes_P52.append(x[
                                             1])  # hier worden alle ziektes van patient 52 aan een lijst toegevoegd
        teller = 0
        for x in lijst_ziektes_P6:
            if lijst_ziektes_P6[
                teller] == 'MMR':  # MMR wordt weggehaald omdat MMR geen ziekte is maar een immunisatie dus die moet er uit worden gefilterd
                del lijst_ziektes_P6[teller]
            teller = teller + 1
        return lijst_ziektes_P6, lijst_ziektes_P52

    except(Exception, ValueError, IndexError,
           TypeError) as error:
        print(error)


def ziekte_lijst_aanpassen(lijst_ziektes_P6, lijst_ziektes_P52):
    """
    Deze functie maakt een vertaalslag voor de Athena database.
    Niet alle ziektes zijn direct in Athena te vinden maar wel afgeleide
    ervan dus met deze functie worden de ziektes omgezet naar afgeleide
    zodat er een hit kan worden gevonden met de Athena DB.
    :param lijst_ziektes_P6: Alle ziektes behorende tot Patient 06
    :type lijst_ziektes_P6: list
    :param lijst_ziektes_P52: Alle ziektes behorende tot Patient 52
    :type lijst_ziektes_P52: list
    :return:
    :ziektes_aangepast_P6: Lijst met ziektes van patient 6 zo aangepast dat er een hit is in de Athena DB
    :rtype: list
    :ziektes_aangepast_P52: Lijst met ziektes van patient 52 zo aangepast dat er een hit is in de Athena DB
    :rtype: list
    """
    try:
        ziektes_aangepast_P6 = []
        ziektes_aangepast_P52 = []
        teller = 0
        for x in lijst_ziektes_P6:
            if x == "Gallstones":
                ziektes_aangepast_P6.append(
                    "Gallstone")  # Gallstones is geen hit in de Athena DB maar Gallstone wel dus wordt Gallstones vervangen met Gallstone
            if x == "Osteopenia":
                ziektes_aangepast_P6.append(
                    "Osteopenia")  # Hier wordt Osteopenia gewoon toegevoegd aan de data, omdat Osteopenia wel een hit heeft in de DB maar nog steeds naar worden gezocht

            teller = teller + 1

        teller = 0
        for x in lijst_ziektes_P52:
            if x == "Moderate androgenic alopecia":
                ziektes_aangepast_P52.append("Androgenic alopecia")
            if x == "Low back pain (degenerative disk disease)":
                ziektes_aangepast_P52.append("Low back pain")
            if x == "Major depression":
                ziektes_aangepast_P52.append("Severe depression")
            if x == "Bruxism":
                ziektes_aangepast_P52.append("Bruxism (teeth grinding)")
            teller = teller + 1
        return ziektes_aangepast_P6, ziektes_aangepast_P52
    except(Exception, ValueError, IndexError,
           TypeError) as error:
        print(error)


def ID_maker_ziektes(lijst_ziektes_P6, lijst_ziektes_P52):
    """
    Deze functie maakt een custom ID voor elke ziekte zodat deze later
    in de database kan worden toegevoed, dit wordt gedaan door middel
    van een dictionary
    :param lijst_ziektes_P6: Lijst met ziektes van patient 6 zo aangepast dat er een hit is in de Athena DB
    :type: list
    :param lijst_ziektes_P52: Lijst met ziektes van patient 52 zo aangepast dat er een hit is in de Athena DB
    :type list
    :return:
    :IDs_ziektes_P6: Een dictionary met de ziektes van P6 als key en de ID als value
    :rtype: dict
    :IDs_ziektes_P52: Een dictionary met de ziektes van P52 als key en de ID als value
    :rtype: dict
    """
    try:
        IDs_ziektes_P6 = {}
        IDs_ziektes_P52 = {}
        teller_P6 = 30
        teller_P52 = 30 + len(
            lijst_ziektes_P6) + 1  # bij de teller wordt de lengte van de ziektes van P6 opgeteld zodat er geen dubbele IDs optreden
        for keys6 in lijst_ziektes_P6:
            IDs_ziektes_P6[
                keys6] = teller_P6  # hier is de ziekte de keys en de custom ID de value, zodat er makkelijk kan worden geinsert.
            teller_P6 = teller_P6 + 1
        for key52 in lijst_ziektes_P52:  # de "normale" ziektelijst wordt hier gebruikt omdat we de custom ID aan de source value linken en niet aan de zoekterm in de Athena DB
            IDs_ziektes_P52[key52] = teller_P52
            teller_P52 = teller_P52 + 1
        return IDs_ziektes_P6, IDs_ziektes_P52
    except(Exception, ValueError, IndexError,
           TypeError) as error:
        print(error)


def parse(bestanden_SNP):  # Moet Femke commenten
    """
    Deze fucntie parst de SNPs in een nieuw bestand
    :param bestanden_SNP: Een lijst met de naam van de SNP bestanden
    :type bestanden_SNP: lijst
    :return:
    :bestand_lijst: lijst met de nieuwe bestanden
    :rtype: list
    """
    try:
        bestand_lijst = []
        for bestand in bestanden_SNP:
            bestand_open = open(bestand)
            variant_bestand = open(bestand + "variant", "w")
            bestand_lijst.append(bestand + "variant")
            for line in bestand_open:
                if "missense_variant" in line or "frameshift_variant" in line:
                    variant_bestand.write(line)
            bestand_open.close()
            variant_bestand.close()
        return bestand_lijst

    except(Exception, ValueError, IndexError,
           TypeError) as error:
        print(error)


def profile_aanpassen(profile):
    """
    Deze functie past het profiel van de patiënten aan, de onnodige
    informatie die niet in de database thuis hoort wordt wegegehaald.
    Daarnaast wordt het geslacht omgezet van 1 letter naar een woord.
    Dit omdat er dan de juist term uit de Athena DB komt.
    :param profile: Een 2D lijst met in elke lijst de eigenschappen van
    de patienten
    :type: list
    :return:
    :profile: Een 2D lijst met in elke lijst de eigenschappen van
    de patient, maar dan aangepast.
    :rtype: list
    """
    try:
        teller = 0
        for x in profile:
            line = profile[teller]
            del line[
                0:3]  # de eerste 3 worden weggehaald omdat dit niet nodig is voor het zoeken naar concepts IDs, positie 3 en 4 moeten behouden worden
            del line[
                2:7]  # Omdat positie 3 en 4 nu 0 en 1 zijn wordt 2 t/m 6 weggehaald
            teller = teller + 1

        teller = 0
        for x in profile:
            if profile[teller][0] == 'F':
                profile[teller][
                    0] = 'Female'  # F geeft niet de juiste concept ID dus wordt F omgezet naar Female, idem dito hieronder maar dan voor Male
            elif profile[teller][0] == 'M':
                profile[teller][0] = 'Male'
            teller = teller + 1
        return profile

    except(Exception, ValueError, IndexError,
           TypeError) as error:
        print(error)


def snp_parser(bestand_lijst):
    """
    Deze functie haalt de gen data uit de varianten op, dit doet hij per
    persoon. Het wordt alleen gedaan bij patient 6 en 52 omdat patient 21
    geen gen data heeft.
    :param bestand_lijst: lijst van de niet gegenereerde bestanden
    :type bestand_lijst: list
    :return:
    gen_data06: dit is een lijst met 10 genen van de snps van patient 06
    gen_data52:  dit is een lijst met 10 genen van de snps van patient 52
    :rtype: list
    """
    try:
        variant_data06 = []
        variant_data52 = []
        gen_data06 = []
        gen_data52 = []
        bestand1 = bestand_lijst[0]
        bestand2 = bestand_lijst[1]
        variant_bestand = open(bestand1)
        for line in variant_bestand:
            stripped = line.strip()
            variant_data06.append(stripped.split(
                "\t"))  # hier wordt de gen data van patient 06 gesplit op tabs waardoor er een nieuwe lijst ontstaat waarop geindexeerd kan worden. Idem voor P52 daaronder
        variant_bestand2 = open(bestand2)
        for line in variant_bestand2:
            stripped = line.strip()
            variant_data52.append(stripped.split("\t"))
        for x in range(
                10):  # range van 10 omdat er maar 10 SNPs per patient hoeven worden gepakt
            gesplitte_data06 = variant_data06[x][7].split("|")
            gesplitte_data52 = variant_data52[x][7].split(
                "|")  # gesplit op | omdat er dan de mutatie kan worden gepakt en de genetische variatie (https://athena.ohdsi.org/search-terms/terms/35960420, https://athena.ohdsi.org/search-terms/terms/35947338)
            gen_data06.append(
                [gesplitte_data06[3], gesplitte_data06[
                    9]])  # Hier wordt de mutatie en de genetische variatie toegevoegd aan een 2D lijst, idem voor Patient 52 daaronder
            gen_data52.append(
                [gesplitte_data52[3], gesplitte_data52[9]])

        return gen_data06, gen_data52

    except(Exception, ValueError, IndexError,
           TypeError) as error:
        print(error)


def ID_maker_measurement_ID(gen_data06, gen_data52):
    """
    Deze functie geeft elke meting van de SNP van elke patient een
    unieke ID zodat deze in de database kan worden gezet.
    :param gen_data06: Een lijst met informatie van de SNPs, hierin
    wat voor mutatie het is (e.g. c.1234A>T) en de genetische variatie
    (e.g. POTED of TPTE). Dit is van patient 06.
    :type gen_data06: list
    :param gen_data52:Een lijst met informatie van de SNPs, hierin
    wat voor mutatie het is (e.g. c.1234A>T) en de genetische variatie
    (e.g. POTED of TPTE). Dit is van patient 52.
    :type gen_data52: list
    :return:
    :IDs_measurementP6: Een lijst met de IDs van patient 06 zijn SNPs
    :rtype: list
    :IDs_measurementP52: Een lijst met de IDs van patient 52 zijn SNPs
    :rtype: list
    """
    try:
        IDs_measurementP6 = []
        IDs_measurementP52 = []
        teller_P6 = 50
        teller_P52 = 50 + len(
            gen_data06) + 1  # bij de teller wordt de lengte van de ziektes van P6 opgeteld zodat er geen dubbele IDs optreden
        for x in gen_data06:
            IDs_measurementP6.append(
                teller_P6)  # hier wordt de ID aan een lijst van patient 6 (P6) toegevoegd
            teller_P6 = teller_P6 + 1
        for x in gen_data52:
            IDs_measurementP52.append(teller_P52)
            teller_P52 = teller_P52 + 1
        return IDs_measurementP6, IDs_measurementP52
    except(Exception, ValueError, IndexError,
           TypeError) as error:
        print(error)


def database_person_vullen(profile, person_6_id, person_21_id,
                           person_52_id):
    """
    Hier wordt de person table gevuld met de verschillende profile lijst
    inhoud
    :param profile: lijst van de observational data van de 3 patienten
    :type profile: list (2d lijst)
    :param person_6_id: dit is de id van patient 06
    :type person_6_id: int
    :param person_21_id:dit is de id van patient 21
    :type person_21_id:int
    :param person_52_id:dit is de id van patient 52
    :type person_52_id: int
    """
    try:
        connection = psycopg2.connect(user="DI_groep_2",
                                      password="blaat1234",
                                      host="postgres.biocentre.nl",
                                      port="5900", database="onderwijs")
        cursor = connection.cursor()
        person_insert_query = """ INSERT INTO di_groep_2.person (person_id, year_of_birth, month_of_birth, gender_concept_id, race_concept_id, person_source_value, gender_source_value, gender_source_concept_id, race_source_value, ethnicity_source_value, ethnicity_concept_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        record_to_insert6person = (
            person_6_id, profile[0][2], profile[0][1], 0, 0,
            profile[0][0],
            profile[0][3], 0, profile[0][4], 0,
            0)  # hier wordt de informatie meegegven wat wordt ingevuld bij patient 6 in de person tabel, hetzelfde gebeurt hieronder voor P21 en P52
        record_to_insert21person = (
            person_21_id, profile[1][2], profile[1][1], 0, 0,
            profile[1][0],
            profile[1][3], 0, profile[1][4], 0, 0)
        record_to_insert52person = (
            person_52_id, 0, 0, 0, 0, profile[2][0], profile[2][3], 0,
            profile[2][4], 0, 0)
        cursor.execute(person_insert_query,
                       record_to_insert6person)  # hiermee wordt het SQL commando en informatie van de patient samengevoegd om de person tabel te vullen
        cursor.execute(person_insert_query, record_to_insert21person)
        cursor.execute(person_insert_query, record_to_insert52person)
        connection.commit()
        cursor.close()
        connection.close()

    except(Exception, psycopg2.DatabaseError, ValueError, IndexError,
           TypeError) as error:
        print(error)


def database_condition_vullen(lijst_ziektes_P6, lijst_ziektes_P52,
                              IDs_ziektes_P6, IDs_ziektes_P52,
                              person_6_id,
                              person_52_id):
    """
    Deze functie vult de condition_occurrence database met de benodigde
    informatie van de ziektes.
    :param lijst_ziektes_P6: Alle ziektes behorende tot Patient 06
    :type lijst_ziektes_P6: list
    :param lijst_ziektes_P52: Alle ziektes behorende tot Patient 52
    :type lijst_ziektes_P52: list
    :param IDs_ziektes_P6: dit zijn de IDs van de ziektes van patient 06
    :type IDs_ziektes_P6: dict
    :param IDs_ziektes_P52 dit zijn de IDs van de ziektes van patient 52
    :type IDs_ziektes_P52: dict
    :param person_6_id: dit is de id van patient 06
    :type person_6_id: int
    :param person_52_id: dit is de id van patient 52
    :type person_52_id: int
    """
    try:
        connection = psycopg2.connect(user="DI_groep_2",
                                      password="blaat1234",
                                      host="postgres.biocentre.nl",
                                      port="5900", database="onderwijs")
        cursor = connection.cursor()
        condition_insert_query = """INSERT INTO di_groep_2.condition_occurrence (condition_occurrence_id, person_id, condition_start_date, condition_type_concept_id, condition_source_value, condition_concept_id) values (%s,%s,%s,%s,%s,%s)"""
        datum = datetime.datetime(1970, 1,
                                  1)  # omdat er geen datum bekend is van de ziektes wordt er 1 januari 1970 ingevuld

        for x in lijst_ziektes_P6:
            record_to_insert6condition = (
                IDs_ziektes_P6.get(x), person_6_id, datum, 0, x,
                0)  # de IDs_ziekte_P6/IDs_ziekte_P52 is een dictionary waar de IDs van de ziektes worden opgehaald aan de hand van de naam van diens ziekte
            cursor.execute(condition_insert_query,
                           record_to_insert6condition)  # hier wordt met een iteratie alle ziektes en de bijbehorende gegevens van P6 in de condition_occurrence ingevuld, hieronder gebeurt hetzelfde voor patient52
        for y in lijst_ziektes_P52:
            record_to_insert52condition = (
                IDs_ziektes_P52.get(y), person_52_id, datum, 0, y, 0)
            cursor.execute(condition_insert_query,
                           record_to_insert52condition)
        connection.commit()
        cursor.close()
        connection.close()

    except(Exception, psycopg2.DatabaseError, ValueError, IndexError,
           TypeError) as error:
        print(error)


def measurement_vullen(gen_data06, gen_data52, person_6_id,
                       person_52_id, IDs_measurementP6,
                       IDs_measurementP52):
    """
    Deze functie mapt de measurement table van de OMOP CDM database.
    :param IDs_measurementP52: Dit zijn de IDs behorende tot de SNPs
    van patient 52
    :type IDs_measurementP52: list
    :param IDs_measurementP6: Dit zijn de IDs behorende tot de SNPs
    van patient 6
    :type IDs_measurementP6: list
    :param gen_data06: Een lijst met informatie van de SNPs, hierin
    wat voor mutatie het is (e.g. c.1234A>T) en de genetische variatie
    (e.g. POTED of TPTE). Dit is van patient 06.
    :type gen_data06: list (2D list)
    :param gen_data52: Een lijst met informatie van de SNPs, hierin
    wat voor mutatie het is (e.g. c.1234A>T) en de genetische variatie
    (e.g. POTED of TPTE). Dit is van patient 52.
    :type gen_data52: list (2D)
    :param person_6_id: dit is de id van patient 06
    :type person_6_id: int
    :param person_52_id: dit is de id van patient 52
    :type person_52_id: int
    """
    try:
        connection = psycopg2.connect(user="DI_groep_2",
                                      password="blaat1234",
                                      host="postgres.biocentre.nl",
                                      port="5900", database="onderwijs")

        cursor = connection.cursor()
        datump6 = datetime.datetime(2016, 11, 1)
        datump52 = datetime.datetime(2016, 12, 28)
        measurement_insert_query = """ INSERT INTO di_groep_2.measurement (measurement_id, person_id, measurement_concept_id, measurement_date, measurement_type_concept_id, measurement_source_value, value_as_concept_id, value_source_value ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        teller = 0
        for x in IDs_measurementP6:
            record_to_insertp6meas = (
                IDs_measurementP6[teller], person_6_id, 0, datump6, 0,
                # hier worden de IDs opgehaald aan de hand van een list en niet een dictionary
                gen_data06[teller][0], 0,
                gen_data06[teller][1])
            record_to_insertp52meas = (
                IDs_measurementP52[teller], person_52_id, 0, datump52,
                0,
                gen_data52[teller][0], 0,
                gen_data52[teller][1])
            cursor.execute(measurement_insert_query,
                           record_to_insertp6meas)
            cursor.execute(measurement_insert_query,
                           record_to_insertp52meas)  # hier wordt met een iteratie alle measurements en de bijbehorende gegevens van P6/P52 in de condition_occurrence ingevuld
            teller = teller + 1
        connection.commit()
        cursor.close()
        connection.close()

    except(Exception, psycopg2.DatabaseError, ValueError, IndexError,
           TypeError) as error:
        print(error)


def database_fetch(ziektes_aangepast_P6, ziektes_aangepast_P52,
                   lijst_ziektes_P6, lijst_ziektes_P52, profile,
                   gen_data06, gen_data52):
    """
    Hier worden de concept IDs van gender, race, ziektes en genetische
    variatie opgehaald om later weer in een andere tabel te mappen
    :param ziektes_aangepast_P6:  Lijst met ziektes van patient 6 zo aangepast dat er een hit is in de Athena DB
    :type ziektes_aangepast_P6: list
    :param ziektes_aangepast_P52:  Lijst met ziektes van patient 52 zo aangepast dat er een hit is in de Athena DB
    :type ziektes_aangepast_P52: list
    :param lijst_ziektes_P6: Alle ziektes behorende tot Patient 06
    :type lijst_ziektes_P6: list
    :param lijst_ziektes_P52: Alle ziektes behorende tot Patient 52
    :type lijst_ziektes_P52: list
    :param profile: lijst van de observational data van de 3 patienten
    :type profile: list (2D list)
    :param gen_data06: Een lijst met informatie van de SNPs, hierin
    wat voor mutatie het is (e.g. c.1234A>T) en de genetische variatie
    (e.g. POTED of TPTE). Dit is van patient 06.
    :type gen_data06: list (2D list)
    :param gen_data52: Een lijst met informatie van de SNPs, hierin
    wat voor mutatie het is (e.g. c.1234A>T) en de genetische variatie
    (e.g. POTED of TPTE). Dit is van patient 52.
    :type gen_data52: list (2D list)
    :return:
    :totale_lijst_dicts: Dit is een lijst met alle dictionaries gemaakt
    in de fetch functies, Hierin staan alle concepts IDs(de value) en
    keys gebaseerd obv een term die al in de database staat die gevuld
    moet worden
    :rtype: dict
    """
    try:
        del lijst_ziektes_P6[
            2]  # Positie 3 wordt weggehaald omdat er geen hits zijn bij Thyroid cancer en anders is het krom vergeleken met de lijst ziektes aangepast. En dan krijg je potentieel of verkeerde concept_IDs toegekend of een Index Error
        alle_genes_meas = [gen_data06,
                           gen_data52]  # deze worden in een lijst gezet zodat er over heen kan worden geitereerd ipv telkens dezelfde code 2 x opnieuw uittypen, hetzelfde geldt voor alle_ziektes en alle_ziektes_aangepast
        alle_ziektes = [lijst_ziektes_P6, lijst_ziektes_P52]
        alle_ziektes_aangepast = [ziektes_aangepast_P6,
                                  ziektes_aangepast_P52]
        dict_concepts_IDs_P6_con = {}  # dit is een dictionary waar in de concept ID van die ziektes van P6 wordt opgeslagen, met de concept ID als value, hetzelfde gebeurt hieronder voor patient 52
        dict_concepts_IDs_P52_con = {}
        dict_concepts_IDs_P6_prof = {}  # dit is een dictionary waar in de concept ID van de gender en het ras van P6 wordt opgeslagen, met de concept ID als value, hetzelfde gebeurt hieronder voor patient 21 en 52
        dict_concepts_IDs_P21_prof = {}
        dict_concepts_IDs_P52_prof = {}
        dict_concepts_IDs_P6_meas = {}  # dit is een dictionary waar in de concept ID van die genetische variatie van P6 wordt opgeslagen, met de concept ID als value, hetzelfde gebeurt hieronder voor patient 52
        dict_concepts_IDs_P52_meas = {}
        lijst_meas_dict = [dict_concepts_IDs_P6_meas,
                           # deze worden in een lijst gezet zodat er over heen kan worden geitereerd ipv telkens dezelfde code 2/3 x opnieuw uittypen, hetzelfde geldt voor de ziektes en profiles
                           dict_concepts_IDs_P52_meas]
        lijst_ziektes_dict = [dict_concepts_IDs_P6_con,
                              dict_concepts_IDs_P52_con]
        lijst_profiles_dict = [dict_concepts_IDs_P6_prof,
                               dict_concepts_IDs_P21_prof,
                               dict_concepts_IDs_P52_prof]

        connection = psycopg2.connect(user="DI_groep_2",
                                      password="blaat1234",
                                      host="postgres.biocentre.nl",
                                      port="5900", database="onderwijs")
        cursor = connection.cursor()

        fetch_query_concepts_ids = """select * from di_groep_2.concept WHERE concept_name = %s """
        fetch_query_concepts_ids_meas = """select * from di_groep_2.concept WHERE concept_name like %s """
        counter = 0
        for x in profile:
            teller = 0
            for y in profile[counter]:
                cursor.execute(fetch_query_concepts_ids,
                               (profile[counter][
                                    teller],))  # hier wordt er gezocht naar de concept ID van het desbetreffende term in elke dictionary van de profiles. Dus bijvoorbeeld Female wordt er uit de eerste dictionary gehaald etc etc.
                records = cursor.fetchall()
                if len(
                        records) > 0:  # dit is toegevoegd zodat als een zoekterm geen resultaat doorkrijgt de lege zoekterm niet wordt toegekend aan de dictionary
                    records = sorted(records, key=lambda ID: ID[
                        0])  # dit zorgt ervoor dat als er meerder resultaten zijn dat de concepts IDs in oplopende volgorde wordt opgehaald dus (1,2,3,4) en niet (2,3,1,4). Dit is o.a. gedaan omdat het juiste sex concept ID het laagste getal is.
                    lijst_profiles_dict[counter][records[0][1]] = \
                        records[0][
                            0]  # records bij records [0][0] krijg je het concept ID dus daarom is dit gehardcode. Hierboven worden er door alle profile dictionaries geitereerd en wordt er de concept name toegekend als key en concept ID als value
                teller = teller + 1
            counter = counter + 1

        counter = 0
        for x in alle_ziektes:  # alle ziektes is een lijst met 2 lijsten erin, een lijst heeft alle ziektes van P06 en de andere van P52
            teller = 0
            for y in alle_ziektes[
                counter]:  # hier wordt er geitereerd over eerst ziekte lijst van P06 daarna die van p52
                cursor.execute(fetch_query_concepts_ids,
                               (alle_ziektes_aangepast[counter][
                                    teller],))  # hier wordt er gezocht naar de concept ID van het desbetreffende term in elke dictionary van de ziektes van de patienten. Dus bijvoorbeeld Gallstone wordt er uit de eerste dictionary gehaald etc etc.
                records = cursor.fetchall()
                if len(records) > 0:
                    records = sorted(records,
                                     key=lambda ID: ID[0])
                    lijst_ziektes_dict[counter][
                        alle_ziektes[counter][teller]] = \
                        records[0][0]
                teller = teller + 1
            counter = counter + 1

        counter = 0
        for x in alle_genes_meas:  # dit is een lijst met meerdere 2D lijsten in de lijst dus. [[[],[]], [[],[]]]
            teller = 0
            for y in alle_genes_meas[
                counter]:  # hier wordt er geitereerd over een 2D lijst
                cursor.execute(fetch_query_concepts_ids_meas,
                               ('%' + alle_genes_meas[counter][teller][
                                   0] + '%',))  # hier wordt positie 0 gekozen omdat daar de genetische variatie instaat
                records = cursor.fetchall()
                if len(records) > 0:
                    records = sorted(records, key=lambda ID: ID[0])
                    lijst_meas_dict[counter][
                        alle_genes_meas[counter][teller][0]] = \
                        records[0][0]
                teller = teller + 1
            counter = counter + 1

        totale_lijst_dicts = [lijst_profiles_dict[0],
                              # hier worden alle dictionaries in een lijst gezet zodat ze makkelijk kunnen worden ge-exporteed uit de functie
                              lijst_profiles_dict[1],
                              lijst_profiles_dict[2],
                              lijst_ziektes_dict[0],
                              lijst_ziektes_dict[1],
                              lijst_meas_dict[0],
                              lijst_meas_dict[1]]

        cursor.close()
        connection.close()
        print(totale_lijst_dicts)
        return totale_lijst_dicts

    except(Exception, psycopg2.DatabaseError, ValueError, IndexError,
           TypeError) as error:
        print(error)


def concept_id_mapping(profile, lijst_ziektes_P6, lijst_ziektes_P52,
                       totale_lijst_dicts, person_6_id, person_21_id,
                       person_52_id, gen_data06, gen_data52):
    """
       hier worden de concept IDs gemapt naar de bijbehorende tabellen.
       :param profile:
       :type profile:
       :param lijst_ziektes_P6: Alle ziektes behorende tot Patient 06
       :type lijst_ziektes_P6: list
       :param lijst_ziektes_P52: Alle ziektes behorende tot Patient 52
       :type lijst_ziektes_P52: list
       :param totale_lijst_dicts: Dit is een lijst met alle dictionaries gemaakt
        in de fetch functies, Hierin staan alle concepts IDs(de value) en
        keys gebaseerd obv een term die al in de database staat die gevuld
        moet worden
       :type totale_lijst_dicts: dict
       :param person_6_id: dit is de id van patient 06
       :type person_6_id: int
       :param person_21_id: dit is de id van patient 21
       :type person_21_id: int
       :param person_52_id: dit is de id van patient 52
       :type person_52_id: dit is de id van patient 06
       :param gen_data06: dit is een lijst met 10 SNPS van patient 06 en de
       genetische variant van de SNP
       :type gen_data06: list (2D)
       :param gen_data52: dit is een lijst met 10 SNPS van patient 52en de
       genetische variant van de SNP
       :type gen_data52: list (2D)
       """

    alle_ziektes = lijst_ziektes_P6 + lijst_ziektes_P52
    profile[0].append(
        person_6_id)  # hier wordt de person ID toegevoegd aan de profile zodat er makkelijk informatie kan worden geupdate aan de hand van de person ID, zelfde gebeurd hieronder voor P21 en P52
    profile[1].append(person_21_id)
    profile[2].append(person_52_id)
    alle_gendata = [gen_data06,
                    gen_data52]  # deze worden in een lijst gezet zodat er over de code geitereerd kan worden en niet 2/3x dezelfde code gedupliceerd hoeft te worden
    try:

        connection = psycopg2.connect(user="DI_groep_2",
                                      password="blaat1234",
                                      host="postgres.biocentre.nl",
                                      port="5900", database="onderwijs")
        update_concept_race = """UPDATE di_groep_2.person SET race_concept_id = %s WHERE person_ID = %s"""
        update_concept_gender = """UPDATE di_groep_2.person SET gender_concept_id = %s WHERE person_ID = %s"""
        update_concept_con = """UPDATE di_groep_2.condition_occurrence SET condition_concept_id = %s WHERE condition_source_value = %s"""
        update_concept_meas = """UPDATE di_groep_2.measurement SET measurement_concept_id = %s WHERE measurement_source_value = %s"""

        cursor = connection.cursor()
        teller = 0
        for x in profile:
            race_ID = totale_lijst_dicts[teller].get(profile[teller][
                                                         1])  # hier wordt het ID van het ras opgehaald en per patient wordt dit itererend gedaan
            value = (race_ID, profile[teller][
                2])  # het ras id wordt toegekend obv het person ID
            cursor.execute(update_concept_race, value)
            teller = teller + 1

        teller = 0
        for x in profile:
            sex_ID = totale_lijst_dicts[teller].get(profile[teller][
                                                        0])  # hier wordt het ID van het geslacht opgehaald en per patient wordt dit itererend gedaan
            value = (sex_ID, profile[teller][
                2])  # het sex id wordt toegekend obv het person ID
            cursor.execute(update_concept_gender, value)
            teller = teller + 1

        counter = 3  # hier is gekozen voor een counter van 3 omdat in de totale_lijst_dicts positie 3 en 4 de dicts zijn van de ziektes van P52 en P06
        for x in range(
                2):  # range van twee is er zodat alleen dictionary 3 en 4 worden gepakt voor het toekennen van de concept ids van het geslacht
            teller = 0
            for y in alle_ziektes:
                dis_ID = totale_lijst_dicts[counter].get(
                    # hier wordt de ID van het ziekte opgehaald en per patient wordt dit itererend gedaan
                    alle_ziektes[
                        teller])  # het ziekte id wordt toegekend obv de naam van de ziekte
                value = (dis_ID, alle_ziektes[teller])
                if value[
                    0] is not None:  # dit is toegevoegd zodat als de dict None geeft, dat er door geitereerd kan worden
                    cursor.execute(update_concept_con, value)
                teller = teller + 1
            counter = counter + 1

        counter = 0
        counter_dicts = 5  # hier is gekozen voor een counter van 5 omdat in de totale_lijst_dicts positie 5 en 6 de dicts zijn van de measurements van P52 en P06
        for z in alle_gendata:
            teller = 0
            for x in alle_gendata[counter]:
                meas_ID = totale_lijst_dicts[counter_dicts].get(
                    alle_gendata[counter][teller][0])
                value = (meas_ID, alle_gendata[counter][teller][
                    0])  # 3D lijst dus moet er worden gekeken in de lijst van de lijst van de lijst
                if value[0] is not None:
                    cursor.execute(update_concept_meas)
                teller = teller + 1
            counter = counter + 1
            counter_dicts = counter_dicts + 1

        connection.commit()
        cursor.close()
        connection.close()

    except(Exception, psycopg2.DatabaseError, ValueError, IndexError,
           TypeError) as error:
        print(error)


main()
