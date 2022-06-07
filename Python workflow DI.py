#Gijsbert Keja, Femke Nijman en Kim Bredenkamp
#07/06/22
#Deze applicatie parst data en vult/fetcht data uit een database
import psycopg2
import psycopg2
import tabula
import datetime
import random

def main():
    person_6_id = 1
    person_21_id = 2
    person_52_id = 3
    bestanden_SNP = ["0006.chr21.snpEff.vcf", "0052.chr21.snpEff.vcf"]
    pdf_bestanden = ['PGPC-6.pdf', 'PGPC-21.pdf', 'PGPC-52.pdf']

    csv_lijst = bestand_omzetten(pdf_bestanden)
    profile, conditions = bestand_inlezen(csv_lijst)
    bestand_lijst = parse(bestanden_SNP)
    gen_data06, gen_data52 = snp_parser(bestand_lijst)
    # measurement_vullen(gen_data06, gen_data52, person_6_id, person_52_id)
    # database_vullen(profile,variant_data, person_6_id, person_21_id, person_52_id)
    raceConceptId, genderConceptId = database_fetch()
    concept_id_mapping(raceConceptId, genderConceptId)




def bestand_omzetten(pdf_bestanden):
    """
    Functie waarin alle pdf bestanden met behulp van tabula worden omgezet naar csv.
    Hierna worden alle bestandsnamen van deze bestanden in een lijst gezet
    die gebruikt worden door bestand_inlezen

    input: pdf_bestanden - lijst van alle nodige bestanden
    return: csv_lijst - lijst met alle csv bestandsnamen
    """
    csv_lijst = []
    for bestand in pdf_bestanden:
        print(bestand)
        df = tabula.read_pdf(bestand, pages='all')[0]
        print(df)
        tabula.convert_into(bestand, "{}.csv".format(bestand),
                            output_format="csv", pages="all")
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
                for i in range(5):
                    next_line = next(bestand_open).strip()
                    #print(next_line.split(','))
                    #gaat door totdat het andere onderdeel is gevonden
                    conditions.append(next_line.split(','))
    return profile, conditions

def parse(bestanden_SNP):
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
    return gen_data06, gen_data52


def measurement_vullen(gen_data06, gen_data52, person_6_id, person_52_id):
    """
Deze functie mapt de measurement table van de OMOP CDM database.
Hier wordt gekozen om per patient 10 genen te worden gemapt in de measurement_source_value column.
    :param gen_data06:dit is een lijst met 10 genen van de snps van patient 06
    :type gen_data06: list
    :param gen_data52: dit is een lijst met 10 genen van de snps van patient 52
    :type gen_data52: list
    :param person_6_id: dit is de id van patient 06
    :type person_6_id: int
    :param person_52_id: dit is de id van patient 52
    :type person_52_id: int
    :return:
    :rtype:
    """
    connection = psycopg2.connect(user="DI_groep_2",
                                  password="blaat1234",
                                  host="postgres.biocentre.nl",
                                  port="5900", database="onderwijs")

    cursor = connection.cursor()
    datump6 = datetime.datetime(2016, 11, 1)
    datump52 = datetime.datetime(2016, 12, 28)
    measurement_insert_query = """ INSERT INTO di_groep_2.measurement (measurement_id, person_id, measurement_concept_id, measurement_date, measurement_type_concept_id, measurement_source_value, value_as_concept_id, value_source_value ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    for x in range(10):
        record_to_insertp6meas = (random.randint(0, 9000000), person_6_id, 0, datump6, 0, gen_data06[x], 0, 0)
        record_to_insertp52meas = (random.randint(0, 9000000), person_52_id, 0, datump52, 0, gen_data52[x], 0, 0)
        cursor.execute(measurement_insert_query, record_to_insertp6meas)
        cursor.execute(measurement_insert_query, record_to_insertp52meas)
    connection.commit()
    cursor.close()
    connection.close()


def database_vullen(profile, person_6_id, person_21_id, person_52_id):
    """
    Hier wordt de person table gevuld met de verschillende profile lijst inhoud
    :param profile: lijst van de observational data van de 3 patienten
    :type profile: list (2d lijst)
    :param person_6_id: dit is de id van patient 06
    :type person_6_id: int
    :param person_21_id:dit is de id van patient 21
    :type person_21_id:int
    :param person_52_id:dit is de id van patient 52
    :type person_52_id: int
    :return:
    :rtype:
    """
    connection = psycopg2.connect(user="DI_groep_2",
                                  password="blaat1234",
                                  host="postgres.biocentre.nl",
                                  port="5900", database="onderwijs")
    cursor = connection.cursor()
    person_insert_query = """ INSERT INTO di_groep_2.person (person_id, year_of_birth, month_of_birth, gender_concept_id, race_concept_id, person_source_value, gender_source_value, gender_source_concept_id, race_source_value, ethnicity_source_value, ethnicity_concept_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    record_to_insert6person = (person_6_id, profile[0][1], profile[0][2], 0,0,0,0,0,0,0,0)
    record_to_insert21person = (person_21_id, profile[1][1], profile[1][2], 0,0,0,0,0,0,0,0)
    record_to_insert52person = (person_52_id, 0, 0, 0,0,0,0,0,0,0,0)
    cursor.execute(person_insert_query, record_to_insert6person)
    cursor.execute(person_insert_query, record_to_insert21person)
    cursor.execute(person_insert_query, record_to_insert52person)
    condition_insert_query = """INSERT INTO di_groep_2.condition_occurrence (condition_occurrence_id, person_id, condition_start_date, condition_type_concept_id, condition_source_value, condition_concept_id) values (%s,%s,%s,%s,%s,%s)"""
    datum = datetime.datetime(1900,1,1)
    record_to_insert6condition = (1, person_6_id, datum,0, 0, 0)
    record_to_insert21condition = (2, person_21_id,datum,0, 0, 0)
    record_to_insert52condition = (3, person_52_id,datum, 0, 0,0)
    cursor.execute(condition_insert_query, record_to_insert6condition)
    cursor.execute(condition_insert_query, record_to_insert21condition)
    cursor.execute(condition_insert_query, record_to_insert52condition)
    cursor.close()
    connection.close()

def database_fetch():
    """
Hier wordt de concept IDs van gender en race opgehaald om later weer in
een andere tabel te mappen
    :return:
    raceConceptId: de ID van de Race
    genderConceptID: de ID van de gender
    :rtype: int
    """
    connection = psycopg2.connect(user="DI_groep_2",
                                  password="blaat1234",
                                  host="postgres.biocentre.nl",
                                  port="5900", database="onderwijs")
    cursor = connection.cursor()
    fetch_query_race = """select * from di_groep_2.concept_class where concept_class_name = 'Race' """
    fetch_query_gender = """ select * from di_groep_2.concept_class where concept_class_name = 'Gender' """
    cursor.execute(fetch_query_race)
    resultaat_race = cursor.fetchall()
    cursor.execute(fetch_query_gender)
    resultaat_gender = cursor.fetchall()
    connection.commit()
    raceConceptId = resultaat_race[0][2]
    genderConceptId = resultaat_gender[0][2]
    cursor.close()
    connection.close()
    return raceConceptId, genderConceptId

def concept_id_mapping(raceConceptId, genderConceptId):
    """
hier worden de race concept id en de gender concept id gemapt naar de
person tabel.
    :param raceConceptId: Id van de Race concept wat eerder ris opgehaald
    :type raceConceptId: int
    :param genderConceptId: Id van de gender concept wat eerder ris opgehaald
    :type genderConceptId: int
    :return: 
    :rtype:
    """
    connection = psycopg2.connect(user="DI_groep_2",
                                  password="blaat1234",
                                  host="postgres.biocentre.nl",
                                  port="5900", database="onderwijs")
    cursor = connection.cursor()
    update_concept_race = """UPDATE di_groep_2.person SET race_concept_id = %s WHERE person_source_value = %s"""
    value = (raceConceptId, '0')
    cursor.execute(update_concept_race, value)
    update_concept_gender = """UPDATE di_groep_2.person SET gender_concept_id = %s WHERE person_source_value = %s"""
    value = (genderConceptId, '0')
    cursor.execute(update_concept_gender, value)
    connection.commit()
    cursor.close()
    connection.close()


main()

