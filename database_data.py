import os
import sqlite3
from backend import DB_NAME, vytvor_tabulky


def connect():
    return sqlite3.connect(DB_NAME)


def delete_all():
    vytvor_tabulky()
    conn = connect()
    conn.execute("DELETE FROM casove_zaznamy")
    conn.execute("DELETE FROM incidenty")
    conn.execute("DELETE FROM pouzivatelia")
    conn.execute("DELETE FROM sqlite_sequence")
    conn.commit()
    conn.close()


def reset_to_default():
    vytvor_tabulky()
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


def create_new_db(with_default_data=True):
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    vytvor_tabulky()
    if with_default_data:
        reset_to_default()


def main():
    print("DATABASE DATA")
    print("1 - Reset all data to default")
    print("2 - Delete all data")
    print("3 - Recreate database from scratch (with default data)")
    print("4 - Recreate empty database from scratch")
    choice = input("Choose: ").strip()

    if choice == "1":
        reset_to_default()
        print("All data was reset.")
    elif choice == "2":
        delete_all()
        print("All data was deleted.")
    elif choice == "3":
        create_new_db(with_default_data=True)
        print("Database recreated with default data.")
    elif choice == "4":
        create_new_db(with_default_data=False)
        print("Empty database created.")
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
