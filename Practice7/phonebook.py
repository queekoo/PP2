import psycopg2
import csv
from config import load_config


def connect():
    config = load_config()
    return psycopg2.connect(**config)



def add_contact():
    conn = connect()
    cur = conn.cursor()

    name = input("Enter name: ")
    phone = input("Enter phone: ")

    cur.execute(
        "INSERT INTO phonebook (first_name, phone) VALUES (%s,%s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()



def upload_csv():
    conn = connect()
    cur = conn.cursor()

    with open("contacts.csv", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            cur.execute(
                "INSERT INTO phonebook (first_name, phone) VALUES (%s,%s)",
                (row[0], row[1])
            )

    conn.commit()
    cur.close()
    conn.close()



def search():
    conn = connect()
    cur = conn.cursor()

    name = input("Enter name: ")

    cur.execute("SELECT * FROM phonebook WHERE first_name=%s", (name,))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()



def update():
    conn = connect()
    cur = conn.cursor()

    name = input("Enter name: ")
    new_phone = input("New phone: ")

    cur.execute(
        "UPDATE phonebook SET phone=%s WHERE first_name=%s",
        (new_phone, name)
    )

    conn.commit()
    cur.close()
    conn.close()


def delete():
    conn = connect()
    cur = conn.cursor()

    value = input("Enter name or phone: ")

    cur.execute(
        "DELETE FROM phonebook WHERE first_name=%s OR phone=%s",
        (value, value)
    )

    conn.commit()
    cur.close()
    conn.close()



while True:
    print("\n1 Add")
    print("2 CSV")
    print("3 Search")
    print("4 Update")
    print("5 Delete")
    print("6 Exit")

    choice = input("Choose: ")

    if choice == "1":
        add_contact()
    elif choice == "2":
        upload_csv()
    elif choice == "3":
        search()
    elif choice == "4":
        update()
    elif choice == "5":
        delete()
    elif choice == "6":
        break