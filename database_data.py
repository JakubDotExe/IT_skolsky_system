import sqlite3


DB_NAME = "skolsky_system.db"


def connect():
    return sqlite3.connect(DB_NAME)


def delete_all():
    conn = connect()
    conn.execute("DELETE FROM casove_zaznamy")
    conn.execute("DELETE FROM incidenty")
    conn.execute("DELETE FROM pouzivatelia")
    conn.execute("DELETE FROM sqlite_sequence")
    conn.commit()
    conn.close()


def reset_to_default():
    delete_all()
    conn = connect()
    users = [
        ("ucitel@skola.sk", "heslo", "Anna Učiteľová", "ucitel"),
        ("it@skola.sk", "heslo", "Peter IT", "it"),
        ("uctovnik@skola.sk", "heslo", "Mária Účtovníková", "uctovnik"),
        ("admin@skola.sk", "heslo", "Ján Admin", "admin"),
    ]
    conn.executemany(
        "INSERT INTO pouzivatelia (email, heslo, meno, rola) VALUES (?, ?, ?, ?)",
        users,
    )
    conn.execute(
        "INSERT INTO incidenty (typ, zarizenie, popis, priorita, stav, reporter_id, riesitel_id, datum_vytvorenia) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("HW", "Notebook Dell", "Nezapne sa po stlačení napájania", "vysoká", "V riešení", 1, 2, "2026-11-02"),
    )
    conn.execute(
        "INSERT INTO casove_zaznamy (incident_id, pouzivatel_id, datum, trvanie_minuty, popis, mesiac) VALUES (?, ?, ?, ?, ?, ?)",
        (1, 2, "2026-11-02", 90, "Kontrola napájacieho zdroja a výmena", "2026-11"),
    )
    conn.commit()
    conn.close()


def main():
    print("DATABASE DATA")
    print("1 - Reset all data to default")
    print("2 - Delete all data")
    choice = input("Choose: ").strip()

    if choice == "1":
        reset_to_default()
        print("All data was reset.")
    elif choice == "2":
        delete_all()
        print("All data was deleted.")


if __name__ == "__main__":
    main()
