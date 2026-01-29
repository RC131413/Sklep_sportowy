import psycopg2
from faker import Faker
import random

fake = Faker('pl_PL')

ziarno = 42
random.seed(ziarno)
Faker.seed(ziarno)

conn = psycopg2.connect(
    dbname = 'Sklep_sportowy',
    user = 'postgres',
    password = '123456',
    host = 'localhost',
    port = '5432'
    )

cur = conn.cursor()


def setup_database():
    global conn, cur

    try:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            sql_schema = f.read()

        cur.execute(sql_schema)
        conn.commit()
        print("Tabele zostały utworzone pomyślnie.")
    except Exception as e:
        print(f"Błąd podczas tworzenia tabel: {e}")
        conn.rollback()

def generuj_adresy(n):
    for i in range(n):
        kraj = "Polska"
        region = fake.administrative_unit()
        miasto = fake.city()
        ulica = fake.street_name()
        kod = fake.postcode()

        cur.execute(
            "INSERT INTO Adres (kraj, region, miasto, ulica, kod_pocztowy) VALUES (%s, %s, %s, %s, %s)",
            (kraj, region, miasto, ulica, kod)
        )
    conn.commit()
    print(f"Dodano {n} adresów.")

def generuj_kategorie():
    kategorie = ['Obuwie', 'Odzież', 'Sprzęt']
    for kat in kategorie:
        cur.execute(
            "INSERT INTO Kategoria (nazwa_kategorii) VALUES (%s)",
            (kat,)
        )
    conn.commit()
    print("Dodano kategorie produktów.")


def generuj_klientow(n):
    for i in range(1, n + 1):
        id_adresu = i
        imie = fake.first_name()
        nazwisko = fake.last_name()
        email = fake.unique.email()
        telefon = fake.phone_number()

        cur.execute(
            "INSERT INTO Klient (ID_adresu, imie, nazwisko, email, telefon) VALUES (%s, %s, %s, %s, %s)",
            (id_adresu, imie, nazwisko, email, telefon)
        )
    conn.commit()
    print(f"Dodano {n} klientów.")


def generuj_dostawcow(n, start_adres_id):
    for i in range(n):
        nazwa_firmy = fake.company()
        email = fake.company_email()
        telefon = fake.phone_number()
        id_adresu = start_adres_id + i

        cur.execute(
            "INSERT INTO Dostawca (ID_adresu, nazwa_dostawcy, email, telefon) VALUES (%s, %s, %s, %s)",
            (id_adresu, nazwa_firmy, email, telefon)
        )
    conn.commit()
    print(f"Dodano {n} dostawców.")

def generuj_produkty(n):
    kolory = ['Czarny', 'Biały', 'Niebieski', 'Szary', 'Czerwony', 'Zielony']
    marki = ['Nike', 'Adidas', 'Puma', 'Reebok', '4F']

    for i in range(n):
        id_kat = random.randint(1, 3)
        marka = random.choice(marki)
        kolor = random.choice(kolory)
        opis = fake.sentence(nb_words=5)

        if id_kat == 1:  # OBUWIE
            nazwa = f"{fake.word().capitalize()} Runner"
            rozmiar = str(random.randint(36, 46))
        elif id_kat == 2:  # ODZIEŻ
            nazwa = f"{fake.word().capitalize()} Shirt"
            rozmiar = random.choice(['S', 'M', 'L', 'XL', 'XXL'])
        else:  # SPRZĘT
            nazwa = f"{fake.word().capitalize()} Pro"
            rozmiar = "Uni"

        cur.execute(
            """INSERT INTO Produkt (ID_kategorii, nazwa, marka, opis, rozmiar, kolor) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (id_kat, nazwa, marka, opis, rozmiar, kolor)
        )
    conn.commit()
    print(f"Dodano {n} produktów.")

def generuj_date():
    licznik = 0
    for rok in range(2021, 2025):
        for m in range(1, 13):
            kwartal = (m - 1) // 3 + 1
            for d in range(1, 29):
                cur.execute(
                    "INSERT INTO Data (rok, kwartal, miesiac, dzien) VALUES (%s, %s, %s, %s)",
                    (rok, kwartal, m, d)
                )
                licznik += 1
    conn.commit()
    print(f"Wygenerowano {licznik} dni (lata 2021-2024).")


def generuj_sprzedaz(n, ile_p, ile_k, ile_dat, ile_dos):
    for i in range(n):
        id_p = random.randint(1, ile_p)
        id_k = random.randint(1, ile_k)
        id_d = random.randint(1, ile_dat)
        id_dos = random.randint(1, ile_dos)

        ilosc = random.randint(1, 5)
        cena_podst = float(random.randint(50, 600))

        # 20% szans na wystąpienie
        if random.random() < 0.20:
            rabat = round(cena_podst * random.uniform(0.05, 0.25), 2)
        else:
            rabat = 0.0

        cena_ost = round((cena_podst - rabat) * ilosc, 2)

        cur.execute(
            """INSERT INTO Sprzedaż (ID_produktu, ID_klienta, ID_daty, ID_dostawcy,
                                     ilosc, cena_podstawowa, rabat, cena_ostateczna)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (id_p, id_k, id_d, id_dos, ilosc, cena_podst, rabat, cena_ost)
        )
    conn.commit()
    print(f"Tabelę faktów {n} transakcji.")

setup_database()

generuj_adresy(60)
generuj_kategorie()
generuj_klientow(50)
generuj_dostawcow(10, 51)
generuj_produkty(100)
generuj_date()
generuj_sprzedaz(1000, 100, 50, 1344, 10)