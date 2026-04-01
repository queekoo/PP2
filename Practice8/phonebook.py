from connect import connect


def search(pattern):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_con(%s)", (pattern,))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    conn.close()


def upsert(name, phone):
    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL upsert_contacts(%s, %s)", (name, phone))
    conn.commit()

    conn.close()


def insert_many():
    conn = connect()
    cur = conn.cursor()

    names = ['Ali', 'Bob', 'Charlie']
    phones = ['87001234567', 'abc', '87771234567']

    cur.execute("CALL insert_many_con(%s, %s)", (names, phones))
    conn.commit()

    conn.close()


def pagination(limit, offset):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM get_con_pag(%s, %s)", (limit, offset))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    conn.close()


def delete(value):
    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL delete_con(%s)", (value,))
    conn.commit()

    conn.close()



if __name__ == "__main__":
    while True:
        print("\n1. Search")
        print("2. Add/Update")
        print("3. Insert Many")
        print("4. Pagination")
        print("5. Delete")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            p = input("Enter pattern: ")
            search(p)

        elif choice == "2":
            name = input("Name: ")
            phone = input("Phone: ")
            upsert(name, phone)

        elif choice == "3":
            insert_many()

        elif choice == "4":
            limit = int(input("Limit: "))
            offset = int(input("Offset: "))
            pagination(limit, offset)

        elif choice == "5":
            val = input("Enter name or phone: ")
            delete(val)

        elif choice == "0":
            break
