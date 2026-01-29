DROP TABLE IF EXISTS Sprzedaż CASCADE;
DROP TABLE IF EXISTS Klient CASCADE;
DROP TABLE IF EXISTS Produkt CASCADE;
DROP TABLE IF EXISTS Adres CASCADE;
DROP TABLE IF EXISTS Kategoria CASCADE;
DROP TABLE IF EXISTS Data CASCADE;
DROP TABLE IF EXISTS Dostawca CASCADE;
DROP VIEW IF EXISTS Widok_Zawezony CASCADE;

CREATE TABLE Adres (
    ID_adresu SERIAL PRIMARY KEY,
    kraj VARCHAR(50) NOT NULL,
    region VARCHAR(50),
    miasto VARCHAR(50) NOT NULL,
    ulica VARCHAR(100),
    kod_pocztowy VARCHAR(10)
);

CREATE TABLE Kategoria (
    ID_kategorii SERIAL PRIMARY KEY,
    nazwa_kategorii VARCHAR(50) NOT NULL
);

CREATE TABLE Produkt (
    ID_produktu SERIAL PRIMARY KEY,
    ID_kategorii INT REFERENCES Kategoria(ID_kategorii),
    nazwa VARCHAR(100) NOT NULL,
    marka VARCHAR(50),
    opis TEXT,
    rozmiar VARCHAR(10),
    kolor VARCHAR(20)
);

CREATE TABLE Klient (
    ID_klienta SERIAL PRIMARY KEY,
    ID_adresu INT REFERENCES Adres(ID_adresu),
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    telefon VARCHAR(20)
);

CREATE TABLE Dostawca (
    ID_dostawcy SERIAL PRIMARY KEY,
    ID_adresu INT REFERENCES Adres(ID_adresu),
    nazwa_dostawcy VARCHAR(100),
    email VARCHAR(100),
    telefon VARCHAR(20)
);

CREATE TABLE Data (
    ID_daty SERIAL PRIMARY KEY,
    rok INT,
    kwartal INT,
    miesiac INT,
    dzien INT
);

CREATE TABLE Sprzedaż (
    ID_sprzedaży SERIAL PRIMARY KEY,
    ID_produktu INT REFERENCES Produkt(ID_produktu),
    ID_klienta INT REFERENCES Klient(ID_klienta),
    ID_daty INT REFERENCES Data(ID_daty),
    ID_dostawcy INT REFERENCES Dostawca(ID_dostawcy),
    ilosc INT CHECK (ilosc > 0),
    cena_podstawowa DECIMAL(10,2),
    rabat DECIMAL(10,2) DEFAULT 0,
    cena_ostateczna DECIMAL(10,2)
);