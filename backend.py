import sqlite3
import datetime

DB_NAME = "skolsky_system.db"


def pripoj():
    return sqlite3.connect(DB_NAME)


def vytvor_tabulky():
    conn = pripoj()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pouzivatelia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            heslo TEXT NOT NULL,
            meno TEXT NOT NULL,
            rola TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS incidenty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            typ TEXT NOT NULL,
            zarizenie TEXT,
            popis TEXT NOT NULL,
            priorita TEXT NOT NULL,
            stav TEXT NOT NULL DEFAULT 'Nahlásený',
            reporter_id INTEGER,
            riesitel_id INTEGER,
            riesenie TEXT,
            datum_vytvorenia TEXT NOT NULL,
            datum_riesenia TEXT,
            FOREIGN KEY (reporter_id) REFERENCES pouzivatelia(id),
            FOREIGN KEY (riesitel_id) REFERENCES pouzivatelia(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS casove_zaznamy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            pouzivatel_id INTEGER NOT NULL,
            datum TEXT NOT NULL,
            trvanie_minuty INTEGER NOT NULL,
            popis TEXT NOT NULL,
            mesiac TEXT NOT NULL,
            FOREIGN KEY (incident_id) REFERENCES incidenty(id),
            FOREIGN KEY (pouzivatel_id) REFERENCES pouzivatelia(id)
        )
    ''')
    conn.commit()
    conn.close()


def pridaj_pouzivatela(email, heslo, meno, rola):
    conn = pripoj()
    c = conn.cursor()
    c.execute(
        "INSERT INTO pouzivatelia (email, heslo, meno, rola) VALUES (?, ?, ?, ?)",
        (email, heslo, meno, rola),
    )
    conn.commit()
    conn.close()


def prihlas(email, heslo):
    conn = pripoj()
    c = conn.cursor()
    c.execute(
        "SELECT id, meno, rola FROM pouzivatelia WHERE email = ? AND heslo = ?",
        (email, heslo),
    )
    row = c.fetchone()
    conn.close()
    return row


def vytvor_incident(typ, zarizenie, popis, priorita, reporter_id):
    conn = pripoj()
    c = conn.cursor()
    datum = datetime.date.today().isoformat()
    c.execute(
        "INSERT INTO incidenty (typ, zarizenie, popis, priorita, reporter_id, datum_vytvorenia) VALUES (?, ?, ?, ?, ?, ?)",
        (typ, zarizenie, popis, priorita, reporter_id, datum),
    )
    conn.commit()
    incident_id = c.lastrowid
    conn.close()
    return incident_id


def zmen_stav(incident_id, novy_stav, riesitel_id=None, riesenie=None):
    conn = pripoj()
    c = conn.cursor()
    datum = datetime.date.today().isoformat()
    if novy_stav == "Vyriešený":
        c.execute(
            "UPDATE incidenty SET stav = ?, riesitel_id = ?, riesenie = ?, datum_riesenia = ? WHERE id = ?",
            (novy_stav, riesitel_id, riesenie, datum, incident_id),
        )
    else:
        c.execute(
            "UPDATE incidenty SET stav = ?, riesitel_id = ? WHERE id = ?",
            (novy_stav, riesitel_id, incident_id),
        )
    conn.commit()
    conn.close()


def zoznam_incidentov(stav=None):
    conn = pripoj()
    c = conn.cursor()
    if stav:
        c.execute(
            "SELECT id, typ, popis, priorita, stav, datum_vytvorenia FROM incidenty WHERE stav = ? ORDER BY id DESC",
            (stav,),
        )
    else:
        c.execute(
            "SELECT id, typ, popis, priorita, stav, datum_vytvorenia FROM incidenty ORDER BY id DESC"
        )
    rows = c.fetchall()
    conn.close()
    return rows


def vykaz_casu(incident_id, pouzivatel_id, trvanie_minuty, popis):
    conn = pripoj()
    c = conn.cursor()
    datum = datetime.date.today().isoformat()
    mesiac = datum[:7]
    c.execute(
        "INSERT INTO casove_zaznamy (incident_id, pouzivatel_id, datum, trvanie_minuty, popis, mesiac) VALUES (?, ?, ?, ?, ?, ?)",
        (incident_id, pouzivatel_id, datum, trvanie_minuty, popis, mesiac),
    )
    conn.commit()
    conn.close()


def mesiac_vykaz(pouzivatel_id, mesiac):
    conn = pripoj()
    c = conn.cursor()
    c.execute(
        "SELECT id, incident_id, datum, trvanie_minuty, popis FROM casove_zaznamy WHERE pouzivatel_id = ? AND mesiac = ? ORDER BY datum",
        (pouzivatel_id, mesiac),
    )
    rows = c.fetchall()
    conn.close()
    return rows


def vytvor_ukazkove_dáta():
    try:
        pridaj_pouzivatela("ucitel@skola.sk", "heslo", "Anna Ucitelova", "ucitel")
        pridaj_pouzivatela("it@skola.sk", "heslo", "Peter IT", "it")
        pridaj_pouzivatela("uctovnik@skola.sk", "heslo", "Mária Martiasd", "uctovnik")
        pridaj_pouzivatela("admin@skola.sk", "heslo", "Ján Admin", "admin")
        iid = vytvor_incident("HW", "Notebook Dell", "Nezapne sa po stlačení", "vysoká", 1)
        zmen_stav(iid, "V riešení", 2)
        vykaz_casu(iid, 2, 90, "Kontrola napájacieho zdroja a výmena")
    except sqlite3.IntegrityError:
        pass


def export_mesiac(pouzivatel_id, mesiac):
    conn = pripoj()
    c = conn.cursor()
    c.execute(
        "SELECT datum, trvanie_minuty, popis FROM casove_zaznamy WHERE pouzivatel_id = ? AND mesiac = ? ORDER BY datum",
        (pouzivatel_id, mesiac),
    )
    rows = c.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    vytvor_tabulky()
    vytvor_ukazkove_dáta()
    print("Databáza vytvorená a naplnená ukážkovými dátami.")
    print("Používatelia:", prihlas("ucitel@skola.sk", "heslo"))
    print("Incidenty:", zoznam_incidentov())