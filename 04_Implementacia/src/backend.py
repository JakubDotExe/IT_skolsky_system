import sqlite3
import datetime
import os

DB_NAME = "skolsky_system.db"


def pripoj():
    return sqlite3.connect(DB_NAME)


def vytvor_tabulky():
    conn = pripoj()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS pouzivatelia (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, heslo TEXT NOT NULL, meno TEXT NOT NULL, rola TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS incidenty (id INTEGER PRIMARY KEY AUTOINCREMENT, typ TEXT NOT NULL, zarizenie TEXT, popis TEXT NOT NULL, priorita TEXT NOT NULL, stav TEXT NOT NULL DEFAULT 'Nahlásený', reporter_id INTEGER, riesitel_id INTEGER, riesenie TEXT, datum_vytvorenia TEXT NOT NULL, datum_riesenia TEXT, FOREIGN KEY (reporter_id) REFERENCES pouzivatelia(id), FOREIGN KEY (riesitel_id) REFERENCES pouzivatelia(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS casove_zaznamy (id INTEGER PRIMARY KEY AUTOINCREMENT, incident_id INTEGER NOT NULL, pouzivatel_id INTEGER NOT NULL, datum TEXT NOT NULL, trvanie_minuty INTEGER NOT NULL, popis TEXT NOT NULL, mesiac TEXT NOT NULL, FOREIGN KEY (incident_id) REFERENCES incidenty(id), FOREIGN KEY (pouzivatel_id) REFERENCES pouzivatelia(id))")
    conn.commit()
    conn.close()


def pridaj_pouzivatela(email, heslo, meno, rola):
    conn = pripoj()
    conn.execute("INSERT INTO pouzivatelia (email, heslo, meno, rola) VALUES (?, ?, ?, ?)", (email, heslo, meno, rola))
    conn.commit()
    conn.close()


def prihlas(email, heslo):
    conn = pripoj()
    row = conn.execute("SELECT id, meno, rola FROM pouzivatelia WHERE email = ? AND heslo = ?", (email, heslo)).fetchone()
    conn.close()
    return row


def vytvor_incident(typ, zarizenie, popis, priorita, reporter_id):
    conn = pripoj()
    date = datetime.date.today().isoformat()
    cursor = conn.execute("INSERT INTO incidenty (typ, zarizenie, popis, priorita, reporter_id, datum_vytvorenia) VALUES (?, ?, ?, ?, ?, ?)", (typ, zarizenie, popis, priorita, reporter_id, date))
    conn.commit()
    incident_id = cursor.lastrowid
    conn.close()
    return incident_id


def zmen_stav(incident_id, novy_stav, riesitel_id, riesenie=""):
    conn = pripoj()
    if novy_stav == "Vyriešený":
        conn.execute("UPDATE incidenty SET stav = ?, riesitel_id = ?, riesenie = ?, datum_riesenia = ? WHERE id = ?", (novy_stav, riesitel_id, riesenie, datetime.date.today().isoformat(), incident_id))
    else:
        conn.execute("UPDATE incidenty SET stav = ?, riesitel_id = ? WHERE id = ?", (novy_stav, riesitel_id, incident_id))
    conn.commit()
    conn.close()


def zoznam_incidentov(stav=None):
    conn = pripoj()
    if stav:
        rows = conn.execute("SELECT id, typ, popis, priorita, stav, datum_vytvorenia FROM incidenty WHERE stav = ? ORDER BY id DESC", (stav,)).fetchall()
    else:
        rows = conn.execute("SELECT id, typ, popis, priorita, stav, datum_vytvorenia FROM incidenty ORDER BY id DESC").fetchall()
    conn.close()
    return rows


def vykaz_casu(incident_id, pouzivatel_id, trvanie_minuty, popis):
    conn = pripoj()
    date = datetime.date.today().isoformat()
    conn.execute("INSERT INTO casove_zaznamy (incident_id, pouzivatel_id, datum, trvanie_minuty, popis, mesiac) VALUES (?, ?, ?, ?, ?, ?)", (incident_id, pouzivatel_id, date, trvanie_minuty, popis, date[:7]))
    conn.commit()
    conn.close()


def zmaz_pouzivatela(user_id):
    conn = pripoj()
    conn.execute("DELETE FROM pouzivatelia WHERE id = ?", (user_id,))
    if conn.execute("SELECT COUNT(*) FROM pouzivatelia").fetchone()[0] == 0:
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'pouzivatelia'")
    conn.commit()
    conn.close()


def zmaz_incident(incident_id):
    conn = pripoj()
    conn.execute("DELETE FROM casove_zaznamy WHERE incident_id = ?", (incident_id,))
    conn.execute("DELETE FROM incidenty WHERE id = ?", (incident_id,))
    if conn.execute("SELECT COUNT(*) FROM incidenty").fetchone()[0] == 0:
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'incidenty'")
    if conn.execute("SELECT COUNT(*) FROM casove_zaznamy").fetchone()[0] == 0:
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'casove_zaznamy'")
    conn.commit()
    conn.close()


def zmaz_casovy_zaznam(time_id):
    conn = pripoj()
    conn.execute("DELETE FROM casove_zaznamy WHERE id = ?", (time_id,))
    if conn.execute("SELECT COUNT(*) FROM casove_zaznamy").fetchone()[0] == 0:
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'casove_zaznamy'")
    conn.commit()
    conn.close()


def uprav_incident(incident_id, stav):
    conn = pripoj()
    conn.execute("UPDATE incidenty SET stav = ? WHERE id = ?", (stav, incident_id))
    conn.commit()
    conn.close()


def uprav_pouzivatela(user_id, email, heslo, meno, rola):
    conn = pripoj()
    conn.execute("UPDATE pouzivatelia SET email = ?, heslo = ?, meno = ?, rola = ? WHERE id = ?", (email, heslo, meno, rola, user_id))
    conn.commit()
    conn.close()


def uprav_casovy_zaznam(time_id, incident_id, user_id, minutes, description):
    conn = pripoj()
    conn.execute("UPDATE casove_zaznamy SET incident_id = ?, pouzivatel_id = ?, trvanie_minuty = ?, popis = ? WHERE id = ?", (incident_id, user_id, minutes, description, time_id))
    conn.commit()
    conn.close()


def mesiac_vykaz(pouzivatel_id, mesiac):
    conn = pripoj()
    rows = conn.execute("SELECT id, incident_id, datum, trvanie_minuty, popis FROM casove_zaznamy WHERE pouzivatel_id = ? AND mesiac = ? ORDER BY datum", (pouzivatel_id, mesiac)).fetchall()
    conn.close()
    return rows


def export_mesiac(pouzivatel_id, mesiac):
    conn = pripoj()
    rows = conn.execute("SELECT datum, trvanie_minuty, popis FROM casove_zaznamy WHERE pouzivatel_id = ? AND mesiac = ? ORDER BY datum", (pouzivatel_id, mesiac)).fetchall()
    conn.close()
    return rows


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_legend():
    print("\nCOMMANDS")
    print("users        show users")
    print("add-user     add a user")
    print("incidents    show incidents")
    print("add-incident add an incident")
    print("time         show time records")
    print("add-time     add a time record")
    print("update       change an incident")
    print("update-user  change a user")
    print("update-time  change a time record")
    print("delete-user  delete a user")
    print("delete-incident delete an incident")
    print("delete-time  delete a time record")
    print("report       show a monthly report")
    print("exit         close the program")


def show_users():
    conn = pripoj()
    rows = conn.execute("SELECT id, meno, email, rola FROM pouzivatelia ORDER BY id").fetchall()
    conn.close()
    print("\nUSERS")
    for row in rows:
        print(f"{row[0]}. {row[1]} | {row[2]} | {row[3]}")
    if not rows:
        print("No users.")


def show_incidents():
    rows = zoznam_incidentov()
    print("\nINCIDENTS")
    for row in rows:
        print(f"{row[0]}. {row[1]} | {row[2]} | {row[3]} | {row[4]}")
    if not rows:
        print("No incidents.")


def show_time():
    conn = pripoj()
    rows = conn.execute("SELECT id, incident_id, pouzivatel_id, datum, trvanie_minuty, popis FROM casove_zaznamy ORDER BY id").fetchall()
    conn.close()
    print("\nTIME")
    for row in rows:
        print(f"{row[0]}. Incident {row[1]} | User {row[2]} | {row[3]} | {row[4]} min | {row[5]}")
    if not rows:
        print("No time records.")


def choose_incident():
    show_incidents()
    return read_number("\nIncident ID: ")


def choose_user():
    show_users()
    return read_number("\nUser ID: ")


def choose_time():
    show_time()
    return read_number("\nTime ID: ")


def read_number(text):
    while True:
        try:
            return int(input(text))
        except ValueError:
            print("Please enter a number.")


def pause():
    input("\nPress Enter to continue...")
    clear_screen()
    show_legend()


def console():
    vytvor_tabulky()
    clear_screen()
    print("SCHOOL IT SYSTEM")
    show_legend()
    while True:
        command = input("\n> ").lower()
        if command == "exit":
            clear_screen()
            return
        if command == "users":
            show_users()
        elif command == "add-user":
            try:
                pridaj_pouzivatela(input("Email: "), input("Password: "), input("Name: "), input("Role: "))
                print("User added.")
            except sqlite3.IntegrityError:
                print("This email is already used.")
        elif command == "incidents":
            show_incidents()
        elif command == "add-incident":
            incident_id = vytvor_incident(input("Type: "), input("Device: "), input("Description: "), input("Priority: "), choose_user())
            print(f"Incident added. ID: {incident_id}")
        elif command == "time":
            show_time()
        elif command == "add-time":
            vykaz_casu(choose_incident(), choose_user(), read_number("Minutes: "), input("Description: "))
            print("Time record added.")
        elif command == "update":
            incident_id = choose_incident()
            uprav_incident(incident_id, input("New status: "))
            print("Incident updated.")
        elif command == "update-user":
            user_id = choose_user()
            uprav_pouzivatela(user_id, input("Email: "), input("Password: "), input("Name: "), input("Role: "))
            print("User updated.")
        elif command == "update-time":
            time_id = choose_time()
            incident_id = choose_incident()
            user_id = choose_user()
            uprav_casovy_zaznam(time_id, incident_id, user_id, read_number("Minutes: "), input("Description: "))
            print("Time record updated.")
        elif command == "delete-user":
            user_id = choose_user()
            zmaz_pouzivatela(user_id)
            print("User deleted.")
        elif command == "delete-incident":
            zmaz_incident(choose_incident())
            print("Incident deleted.")
        elif command == "delete-time":
            zmaz_casovy_zaznam(choose_time())
            print("Time record deleted.")
        elif command == "report":
            rows = mesiac_vykaz(read_number("User ID: "), input("Month (YYYY-MM): "))
            print("\nREPORT")
            for row in rows:
                print(f"{row[2]} | {row[3]} min | {row[4]}")
            if not rows:
                print("No records.")
        else:
            print("Unknown command.")
        pause()


if __name__ == "__main__":
    console()
